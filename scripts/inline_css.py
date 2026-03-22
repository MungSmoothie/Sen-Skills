#!/usr/bin/env python3
"""Inline all CSS into HTML elements for email compatibility."""
import sys, re, os

CSS_VARS = {
    '--wine-red': '#8b2635', '--charcoal': '#1a1a1a', '--warm-gray': '#6b6560',
    '--light-warm': '#f0ebe3', '--paper': '#faf8f3', '--navy': '#1a3a5c',
    '--text': '#222222', '--text-light': '#5a5a5a', '--border': '#d4cfc5',
}

def load_css(html_path):
    html = open(html_path).read()
    css = ''
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(html_path)), 'style.css'),
        '/home/claw/.openclaw/workspace/skills/ai-daily-news/assets/style.css',
    ]
    for p in candidates:
        if os.path.exists(p):
            css += open(p).read() + '\n'
    for k, v in CSS_VARS.items():
        css = css.replace('var(' + k + ')', v)
    css = re.sub(r':root\s*\{[^}]*\}\s*', '', css)
    return css, html

def parse_css(css_text):
    rules = []
    css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
    i = 0
    while i < len(css_text):
        while i < len(css_text) and css_text[i] in ' \t\n\r':
            i += 1
        if i >= len(css_text):
            break
        if css_text[i] == '@':
            brace = css_text.find('{', i)
            if brace == -1:
                break
            j = brace + 1
            depth = 1
            while j < len(css_text) and depth > 0:
                c = css_text[j]
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                j += 1
            i = j
            continue
        brace = css_text.find('{', i)
        if brace == -1:
            break
        selector = css_text[i:brace].strip()
        j = brace + 1
        depth = 1
        while j < len(css_text) and depth > 0:
            c = css_text[j]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            j += 1
        decls = css_text[brace+1:j-1]
        if selector:
            style = {}
            for d in decls.split(';'):
                d = d.strip()
                if ':' in d:
                    parts = d.split(':', 1)
                    p, v = parts[0].strip(), parts[1].strip()
                    if p and not p.startswith('--'):
                        style[p] = v
            rules.append((selector, style))
        i = j
    return rules

def specificity(s):
    score = 0
    for part in re.findall(r'[.#]?[\w-]+', s):
        if '#' in part:
            score += 100
        elif '.' in part:
            score += 10
        else:
            score += 1
    return score

def matches(tag, classes, elem_id, selector):
    selector = selector.strip()
    if ',' in selector:
        return any(matches(tag, classes, elem_id, s) for s in selector.split(','))
    selector = re.sub(r':[\w-]+(?:\([^)]*\))?', '', selector).strip()
    if not selector or selector == '*':
        return True
    for id_sel in re.findall(r'#([\w-]+)', selector):
        if elem_id != id_sel:
            return False
    for cls in re.findall(r'\.([\w-]+)', selector):
        if cls not in classes:
            return False
    tag_match = re.search(r'^[a-zA-Z][\w-]*', selector)
    if tag_match and tag.lower() != tag_match.group(0).lower():
        return False
    return True

def parse_tag(html, i):
    if html[i:i+4] == '<!--':
        end = html.find('-->', i+4)
        return ('!--', {}, False, end+3 if end != -1 else len(html))
    if html[i:i+2] == '<!':
        end = html.find('>', i)
        return ('!', {}, False, end+1 if end != -1 else len(html))
    j = i + 1
    # Handle closing tags like </title>
    if j < len(html) and html[j] == '/':
        tag_end = html.find('>', j)
        if tag_end != -1:
            return ('', {}, False, tag_end + 1)
        else:
            return ('', {}, False, len(html))
    while j < len(html) and html[j] in ' \t\n\r':
        j += 1
    # Handle closing tags </tagname> — output as-is, don't skip
    if j + 1 < len(html) and html[j] == '/' and html[j+1] != '!':
        # Find the end of the closing tag
        end = html.find('>', j)
        if end != -1:
            return ('', {}, False, end + 1)
        return ('', {}, False, len(html))
    k = j
    while k < len(html) and html[k] not in ' \t\n\r/>':
        k += 1
    tag = html[j:k].lower()
    if not tag:
        return ('', {}, False, i+1)
    attrs = {}
    pos = k
    while pos < len(html):
        while pos < len(html) and html[pos] in ' \t\n\r':
            pos += 1
        if pos >= len(html) or html[pos] in '>/':
            break
        astart = pos
        while pos < len(html) and html[pos] not in ' \t\n\r=/':
            pos += 1
        attr = html[astart:pos].strip()
        if not attr:
            break
        if pos >= len(html) or html[pos] == '>':
            break
        if html[pos] == '/':
            break
        if html[pos] == '=':
            pos += 1
            while pos < len(html) and html[pos] in ' \t\n\r':
                pos += 1
            if pos < len(html) and html[pos] in '"\'':
                quote = html[pos]
                pos += 1
                qend = pos
                while qend < len(html) and html[qend] != quote:
                    qend += 1
                attrs[attr] = html[pos:qend]
                pos = qend + 1
            else:
                vend = pos
                while vend < len(html) and html[vend] not in ' \t\n\r>"\'/':
                    vend += 1
                attrs[attr] = html[pos:vend]
                pos = vend
        else:
            attrs[attr] = attr
            pos += 1
    self_closing = False
    end = pos
    if end < len(html) and html[end] == '/':
        self_closing = True
    while end < len(html) and html[end] not in '>':
        end += 1
    if end < len(html):
        end += 1
    return (tag, attrs, self_closing, end)

def inline_css(html, rules):
    selector_map = {}
    for sel, style in rules:
        sp = specificity(sel)
        if sel not in selector_map or sp > selector_map[sel][0]:
            selector_map[sel] = (sp, style)

    # Build class/id registry for all elements
    # Parse all elements first, recording their class/id
    elements = []  # list of (start_pos, tag, attrs, classes_set, elem_id)
    i = 0
    while i < len(html):
        if html[i] != '<':
            i += 1
            continue
        tag, attrs, self_closing, end = parse_tag(html, i)
        if tag and tag not in ('style', 'script', 'link', '!--', ''):
            classes = set()
            for v in attrs.get('class', '').split():
                classes.add(v)
            elem_id = attrs.get('id', '')
            elements.append((i, tag, classes, elem_id))
        i = end

    # Build ancestor chain for each element
    def get_ancestors(pos):
        ancestors = []
        for (start, tag, classes, elem_id) in elements:
            if start < pos:
                ancestors.append((tag, classes, elem_id))
        return ancestors

    # Combine all classes for descendant selector matching
    def all_classes_match(ancestors, selector):
        """Check if any ancestor matches selector's ancestor part."""
        for part in selector.split():
            part = part.strip()
            if not part:
                continue
            if part == '>':
                continue  # handle later if needed
            for (tag, classes, elem_id) in ancestors:
                if matches(tag, classes, elem_id, part):
                    return True
        return False

    result = []
    i = 0
    while i < len(html):
        if html[i] != '<':
            result.append(html[i])
            i += 1
            continue
        tag, attrs, self_closing, end = parse_tag(html, i)
        tag_str = html[i:end]
        # Note: closing tags like </title> return ('', {}, False, pos)
        # We output them as raw text (don't skip)
        if tag in ('style', 'script', 'link', '!--'):
            i = end
            continue

        classes = set()
        for v in attrs.get('class', '').split():
            classes.add(v)
        elem_id = attrs.get('id', '')

        # Get ancestors
        ancestors = get_ancestors(i)

        combined = {}
        for sel, (sp, style) in selector_map.items():
            # Split selector into parts (descendant selectors)
            sel_parts = sel.split()
            if len(sel_parts) == 1:
                # Simple selector
                if matches(tag, classes, elem_id, sel):
                    combined.update(style)
            else:
                # Descendant selector: check last part matches current, others match ancestors
                last = sel_parts[-1]
                others = ' '.join(sel_parts[:-1])
                if matches(tag, classes, elem_id, last):
                    if all_classes_match(ancestors, others):
                        combined.update(style)

        if 'style' in attrs:
            for d in attrs['style'].split(';'):
                d = d.strip()
                if ':' in d:
                    parts = d.split(':', 1)
                    p, v = parts[0].strip(), parts[1].strip()
                    if p and p not in combined:
                        combined[p] = v

        if combined and tag:
            style_val = '; '.join(p + ':' + v for p, v in combined.items())
            attrs['style'] = style_val
            parts = [tag]
            for k, v in attrs.items():
                if k == 'style':
                    parts.append('style="' + v + '"')
                elif v == k:
                    parts.append(k)
                else:
                    parts.append(k + '="' + v + '"')
            result.append('<' + ' '.join(parts) + '>')
        elif self_closing and tag:
            result.append('<' + tag + '>')
        else:
            result.append(tag_str)
        i = end

    return ''.join(result)

def main():
    html_path = sys.argv[1] if len(sys.argv) > 1 else 'ai-daily-news-2026-03-19.html'
    css, html = load_css(html_path)
    rules = parse_css(css)
    sys.stderr.write('Parsed ' + str(len(rules)) + ' CSS rules\n')
    result = inline_css(html, rules)
    out_path = html_path.replace('.html', '-inlined.html')
    open(out_path, 'w').write(result)
    sys.stderr.write('Written: ' + out_path + ' (' + str(len(result)) + ' bytes)\n')
    idx = result.find('<h1')
    if idx >= 0:
        snippet = result[idx:idx+200]
        sys.stderr.write('h1 tag: ' + snippet + '\n')

if __name__ == '__main__':
    main()
