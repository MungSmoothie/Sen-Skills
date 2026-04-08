#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
send_email_with_attachment.py — 发送日报邮件（正文内嵌样式 + HTML附件）
用法: python3 send_email_with_attachment.py <html_file> [recipient_email]...
"""
import sys, re, base64, os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders as email_encoders

SENDER_EMAIL = "2323831454@qq.com"
SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 587

DEFAULT_RECIPIENTS = ["179621078@qq.com", "hakusai22@qq.com", "536574781@qq.com"]

CSS_VARS = {
    '--wine-red': '#8b2635', '--charcoal': '#1a1a1a', '--warm-gray': '#6b6560',
    '--light-warm': '#f0ebe3', '--paper': '#faf8f3', '--navy': '#1a3a5c',
    '--text': '#222222', '--text-light': '#5a5a5a', '--border': '#d4cfc5',
}

def get_password():
    try:
        with open(os.path.expanduser("~/.msmtprc"), "r") as f:
            for line in f:
                if "password" in line.lower():
                    return line.strip().split()[-1]
    except: pass
    return None

def encode_str(s):
    """RFC 2047 encoded-word"""
    return "=?utf-8?B?" + base64.b64encode(s.encode('utf-8')).decode('ascii') + "?="

def encode_header(s):
    return encode_str(s) + " <" + SENDER_EMAIL + ">"

def specificity(s):
    score = 0
    for part in re.findall(r'[.#]?[\w-]+', s):
        if '#' in part: score += 100
        elif '.' in part: score += 10
        else: score += 1
    return score

def matches(tag, classes, elem_id, selector):
    selector = selector.strip()
    if ',' in selector:
        return any(matches(tag, classes, elem_id, s) for s in selector.split(','))
    selector = re.sub(r':[\w-]+(?:\([^)]*\))?', '', selector).strip()
    if not selector or selector == '*': return True
    for id_sel in re.findall(r'#([\w-]+)', selector):
        if elem_id != id_sel: return False
    for cls in re.findall(r'\.([\w-]+)', selector):
        if cls not in classes: return False
    tag_match = re.search(r'^[a-zA-Z][\w-]*', selector)
    if tag_match and tag.lower() != tag_match.group(0).lower(): return False
    return True

def parse_tag(html, i):
    if html[i:i+4] == '<!--':
        end = html.find('-->', i+4)
        return ('!--', {}, False, end+3 if end != -1 else len(html))
    if html[i:i+2] == '<!':
        end = html.find('>', i)
        return ('!', {}, False, end+1 if end != -1 else len(html))
    j = i + 1
    if j < len(html) and html[j] == '/':
        k = j + 1
        while k < len(html) and html[k] != '>': k += 1
        return ('', {}, False, k+1 if k < len(html) else len(html))
    while j < len(html) and html[j] in ' \t\n\r': j += 1
    k = j
    while k < len(html) and html[k] not in ' \t\n\r/>': k += 1
    tag = html[j:k].lower()
    if not tag: return ('', {}, False, i+1)
    attrs = {}
    pos = k
    while pos < len(html):
        while pos < len(html) and html[pos] in ' \t\n\r': pos += 1
        if pos >= len(html) or html[pos] in '>/': break
        astart = pos
        while pos < len(html) and html[pos] not in ' \t\n\r=/': pos += 1
        attr = html[astart:pos].strip()
        if not attr: break
        if pos >= len(html) or html[pos] == '>': break
        if html[pos] == '/': break
        if html[pos] == '=':
            pos += 1
            while pos < len(html) and html[pos] in ' \t\n\r': pos += 1
            if pos < len(html) and html[pos] in '"\'':
                quote = html[pos]; pos += 1; qend = pos
                while qend < len(html) and html[qend] != quote: qend += 1
                attrs[attr] = html[pos:qend]; pos = qend + 1
            else:
                vend = pos
                while vend < len(html) and html[vend] not in ' \t\n\r>"\'/': vend += 1
                attrs[attr] = html[pos:vend]; pos = vend
        else:
            attrs[attr] = attr; pos += 1
    end = pos
    while end < len(html) and html[end] not in '>': end += 1
    if end < len(html): end += 1
    return (tag, attrs, False, end)

def inline_css(html, html_path):
    # Remove scripts
    while '<script' in html:
        start = html.find('<script')
        end = html.find('</script>', start)
        if end == -1:
            gt = html.find('>', start)
            if gt != -1: html = html[:start] + html[gt+1:]
            break
        html = html[:start] + html[end + len('</script>'):]

    # Load CSS from external files
    css_texts = []
    for m in re.finditer(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>', html):
        href = m.group(1)
        if href.startswith('http'): continue
        candidates = [
            os.path.join(os.path.dirname(os.path.abspath(html_path)), href),
            '/home/claw/.openclaw/workspace/skills/ai-daily-news/assets/' + href,
        ]
        for p in candidates:
            if os.path.exists(p):
                css_texts.append(open(p).read())
                break
    for m in re.finditer(r'<style[^>]*>(.*?)</style>', html, re.DOTALL):
        css_texts.append(m.group(1))
    all_css = '\n'.join(css_texts)
    for k, v in CSS_VARS.items():
        all_css = all_css.replace('var(' + k + ')', v)
    all_css = re.sub(r':root\s*\{[^}]*\}\s*', '', all_css)
    all_css = re.sub(r'/\*.*?\*/', '', all_css, flags=re.DOTALL)

    # Parse rules
    rules = []
    ci = 0
    while ci < len(all_css):
        while ci < len(all_css) and all_css[ci] in ' \t\n\r': ci += 1
        if ci >= len(all_css): break
        if all_css[ci] == '@':
            brace = all_css.find('{', ci)
            if brace == -1: break
            j = brace + 1; depth = 1
            while j < len(all_css) and depth > 0:
                c = all_css[j]
                if c == '{': depth += 1
                elif c == '}': depth -= 1
                j += 1
            ci = j; continue
        brace = all_css.find('{', ci)
        if brace == -1: break
        selector = all_css[ci:brace].strip()
        j = brace + 1; depth = 1
        while j < len(all_css) and depth > 0:
            c = all_css[j]
            if c == '{': depth += 1
            elif c == '}': depth -= 1
            j += 1
        decls = all_css[brace+1:j-1]
        if '::' in selector:
            ci = j; continue
        if selector:
            style = {}
            for d in decls.split(';'):
                d = d.strip()
                if ':' in d:
                    p, v = d.split(':', 1)
                    p, v = p.strip(), v.strip()
                    if p and not p.startswith('--'): style[p] = v
            rules.append((selector, style))
        ci = j

    selector_map = {}
    for sel, style in rules:
        sp = specificity(sel)
        if sel not in selector_map or sp > selector_map[sel][0]:
            selector_map[sel] = (sp, style)

    elements = []
    i = 0
    while i < len(html):
        if html[i] != '<': i += 1; continue
        tag, attrs, _, end = parse_tag(html, i)
        if tag and tag not in ('style', 'script', 'link', '!--', ''):
            classes = set()
            for v in attrs.get('class', '').split(): classes.add(v)
            elem_id = attrs.get('id', '')
            elements.append((i, tag, classes, elem_id))
        i = end

    def get_ancestors(pos):
        return [(t, c, eid) for (s, t, c, eid) in elements if s < pos]

    def all_classes_match(ancestors, selector):
        for part in selector.split():
            part = part.strip()
            if not part: continue
            for (tag, classes, elem_id) in ancestors:
                if matches(tag, classes, elem_id, part): return True
        return False

    for k, v in CSS_VARS.items():
        html = html.replace('var(' + k + ')', v)

    result = []
    i = 0
    while i < len(html):
        if html[i] != '<':
            result.append(html[i]); i += 1; continue
        tag, attrs, self_closing, end = parse_tag(html, i)
        tag_str = html[i:end]
        if tag in ('script', 'link', '!--'):
            i = end; continue
        if tag == 'style':
            close_pos = html.find('</style>', end)
            if close_pos != -1: end = close_pos + len('</style>')
            i = end; continue
        if tag == '':
            result.append(tag_str); i = end; continue
        classes = set()
        for v in attrs.get('class', '').split(): classes.add(v)
        elem_id = attrs.get('id', '')
        ancestors = get_ancestors(i)
        combined = {}
        for sel, (sp, style) in selector_map.items():
            sel_parts = sel.split()
            if len(sel_parts) == 1:
                if matches(tag, classes, elem_id, sel): combined.update(style)
            else:
                if matches(tag, classes, elem_id, sel_parts[-1]):
                    if all_classes_match(ancestors, ' '.join(sel_parts[:-1])):
                        combined.update(style)
        if 'style' in attrs:
            for d in attrs['style'].split(';'):
                d = d.strip()
                if ':' in d:
                    p, v = d.split(':', 1)
                    p, v = p.strip(), v.strip()
                    if p and p not in combined: combined[p] = v
        if combined and tag:
            style_val = '; '.join(p + ':' + v for p, v in combined.items())
            attrs['style'] = style_val
            parts = [tag]
            for k, v in attrs.items():
                if k == 'style': parts.append('style="' + v + '"')
                elif v == k: parts.append(k)
                else: parts.append(k + '="' + v + '"')
            result.append('<' + ' '.join(parts) + '>')
        else:
            result.append(tag_str)
        i = end
    return ''.join(result)

def embed_external_css(html_file):
    """把外部 CSS 文件嵌入 HTML（供附件使用），返回新的 HTML 内容"""
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    css_file = "/home/claw/.openclaw/workspace/skills/ai-daily-news/assets/style.css"
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            css_content = f.read()
        # 移除 @import 和 Google Fonts
        css_content = re.sub(r'@import\s+url\([^)]+\);?\s*', '', css_content)
        html = re.sub(
            r'<link[^>]+href=["\']style\.css["\'][^>]*/?>',
            f'<style>\n{css_content}\n</style>',
            html
        )
    return html

def make_msg(subject, to_email, body_html, attachment_html_bytes, filename):
    msg = MIMEMultipart('mixed')
    msg['From'] = encode_header("村口情报社")
    msg['To'] = to_email
    msg['Subject'] = encode_str(subject)

    # 正文：CSS 内联版本
    body = MIMEText(body_html, 'html', 'utf-8')
    msg.attach(body)

    # 附件：原始 HTML（带 <style> 标签）
    att = MIMEBase('application', 'octet-stream')
    att.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', filename))
    att.set_payload(attachment_html_bytes)
    email_encoders.encode_base64(att)
    msg.attach(att)

    return msg.as_bytes()

def send_email(msg_bytes, to_email):
    password = get_password()
    if not password:
        raise RuntimeError("未找到 SMTP 授权码")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SENDER_EMAIL, password)
        server.sendmail(SENDER_EMAIL, [to_email], msg_bytes)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 send_email_with_attachment.py <html_file> [recipient_email]...", file=sys.stderr)
        sys.exit(1)
    html_file = sys.argv[1]
    recipients = sys.argv[2:] if len(sys.argv) > 2 else DEFAULT_RECIPIENTS
    if not os.path.exists(html_file):
        print("错误: 文件不存在 " + html_file, file=sys.stderr); sys.exit(1)

    # 邮件正文：CSS 内联
    with open(html_file, "r", encoding="utf-8") as f:
        raw_html = f.read()
    body_html = inline_css(raw_html, html_file)

    # 附件：嵌入 CSS 后的原始 HTML
    embedded_html = embed_external_css(html_file)
    attachment_bytes = embedded_html.encode('utf-8')

    # 提取日期
    date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', raw_html)
    if date_match:
        subject = f"村口情报社 AI日报 {date_match.group(1)}年{date_match.group(2)}月{date_match.group(3)}日"
    else:
        from datetime import datetime
        subject = "村口情报社 AI日报 " + datetime.now().strftime("%Y年%m月%d日")

    filename = os.path.basename(html_file)
    print(f"邮件主题: {subject}")
    print(f"正文长度: {len(body_html)} 字符（CSS已内联）")
    print(f"附件长度: {len(attachment_bytes)} 字节（带<style>标签）")
    print(f"收件人: {', '.join(recipients)}")

    for r in recipients:
        msg_bytes = make_msg(subject, r, body_html, attachment_bytes, filename)
        send_email(msg_bytes, r)
        print(f"发送成功 -> {r}")

if __name__ == "__main__":
    main()
