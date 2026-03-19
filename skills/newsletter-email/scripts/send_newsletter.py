# -*- coding: utf-8 -*-
"""
send_newsletter.py — 将日报 HTML 发送至 QQ 邮箱
用法: python3 send_newsletter.py <html_file> [recipient_email]...
"""
import sys, subprocess, re, base64, os

DEFAULT_RECIPIENTS = ["179621078@qq.com", "hakusai22@qq.com", "536574781@qq.com"]
SENDER_EMAIL = "2323831454@qq.com"
SENDER_DISPLAY = "村口情报社"

CSS_VARS = {
    '--wine-red': '#8b2635', '--charcoal': '#1a1a1a', '--warm-gray': '#6b6560',
    '--light-warm': '#f0ebe3', '--paper': '#faf8f3', '--navy': '#1a3a5c',
    '--text': '#222222', '--text-light': '#5a5a5a', '--border': '#d4cfc5',
}

def encode_header(s):
    return "=?UTF-8?B?" + base64.b64encode(s.encode("utf-8")).decode("ascii") + "?="

def find_css_path(href, html_path):
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(html_path)), href),
        '/home/claw/.openclaw/workspace/skills/ai-daily-news/assets/' + href,
    ]
    # For email, prefer email-style.css over style.css
    if href == 'style.css':
        email_alt = '/home/claw/.openclaw/workspace/skills/ai-daily-news/assets/email-style.css'
        if os.path.exists(email_alt):
            return email_alt
    for p in candidates:
        if os.path.exists(p):
            return p

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
    # General closing tag </...> — find the closing >
    if j < len(html) and html[j] == '/':
        k = j + 1
        while k < len(html) and html[k] != '>':
            k += 1
        return ('', {}, False, k + 1 if k < len(html) else len(html))
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
    self_closing = False
    end = pos
    if end < len(html) and html[end] == '/': self_closing = True
    while end < len(html) and html[end] not in '>': end += 1
    if end < len(html): end += 1
    return (tag, attrs, self_closing, end)

def inline_css(html, html_path):
    # Load CSS from external files
    css_texts = []
    for m in re.finditer(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>', html):
        p = find_css_path(m.group(1), html_path)
        if p: css_texts.append(open(p).read())
    for m in re.finditer(r'<style[^>]*>(.*?)</style>', html, re.DOTALL):
        css_texts.append(m.group(1))
    all_css = '\n'.join(css_texts)
    for k, v in CSS_VARS.items():
        all_css = all_css.replace('var(' + k + ')', v)
    all_css = re.sub(r':root\s*\{[^}]*\}\s*', '', all_css)
    all_css = re.sub(r'/\*.*?\*/', '', all_css, flags=re.DOTALL)

    # Parse CSS rules
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

    # Selector -> best style map
    selector_map = {}
    for sel, style in rules:
        sp = specificity(sel)
        if sel not in selector_map or sp > selector_map[sel][0]:
            selector_map[sel] = (sp, style)

    # Pre-parse elements for ancestor matching
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

    # Expand CSS vars in HTML
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
            # Skip opening <style> tag and its CSS content and closing </style>
            close_pos = html.find('</style>', end)
            if close_pos != -1:
                end = close_pos + len('</style>')
            i = end; continue
        if tag == '':
            # Closing tag: output it as-is
            result.append(tag_str)
            i = end; continue
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

def send_email(html_content, subject, to_email):
    subject_enc = encode_header(subject)
    from_enc = encode_header(SENDER_DISPLAY) + " <" + SENDER_EMAIL + ">"
    headers = "\r\n".join([
        "From: " + from_enc,
        "To: " + to_email,
        "Subject: " + subject_enc,
        "Content-Type: text/html; charset=UTF-8",
        "MIME-Version: 1.0", "", html_content
    ])
    r = subprocess.run(["msmtp", to_email], input=headers.encode("utf-8"),
                       capture_output=True, timeout=30)
    return r

def main():
    if len(sys.argv) < 2:
        print("用法: python3 send_newsletter.py <html_file> [recipient_email]...", file=sys.stderr)
        sys.exit(1)
    html_file = sys.argv[1]
    recipients = sys.argv[2:] if len(sys.argv) > 2 else DEFAULT_RECIPIENTS
    if not os.path.exists(html_file):
        print("错误: 文件不存在 " + html_file, file=sys.stderr); sys.exit(1)

    with open(html_file, "r", encoding="utf-8") as f:
        raw_html = f.read()

    date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', raw_html)
    if date_match:
        subject = "村口情报社 AI日报 " + date_match.group(1) + "年" + date_match.group(2) + "月" + date_match.group(3) + "日"
    else:
        from datetime import datetime
        subject = "村口情报社 AI日报 " + datetime.now().strftime("%Y年%m月%d日")

    email_html = inline_css(raw_html, html_file)
    success = True
    for r in recipients:
        result = send_email(email_html, subject, r)
        if result.returncode == 0:
            print("发送成功: " + subject + " -> " + r)
        else:
            print("发送失败 " + r + ": " + result.stderr.decode(), file=sys.stderr)
            success = False
    if not success: sys.exit(1)

if __name__ == "__main__":
    main()
