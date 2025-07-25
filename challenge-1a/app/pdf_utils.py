import fitz  # PyMuPDF
import re
from collections import Counter, defaultdict


def get_document_body_style(doc):
    """Analyzes the document to find the most common font size and name (body text)."""
    style_counts = Counter()
    for page in doc:
        for b in page.get_text("dict")["blocks"]:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        style_counts[(round(s['size']), s['font'])] += 1
    if not style_counts:
        return 10, "default"
    most_common_style = style_counts.most_common(1)[0][0]
    return most_common_style[0], most_common_style[1]


def get_header_footer_zones(doc, sample_pages=3):
    """Identifies potential header/footer areas by finding common text on sample pages."""
    if doc.page_count <= sample_pages:
        return []
    pages_to_sample = [0, doc.page_count // 2, doc.page_count - 1]
    page_texts = defaultdict(list)
    for page_num in pages_to_sample:
        page = doc.load_page(page_num)
        for block in page.get_text("blocks"):
            text = "".join(line.strip() for line in block[4].split('\n'))
            if text:
                key = (text, round(block[1] / 10))
                page_texts[key].append(block[0:4])
    common_bboxes = []
    for key, bboxes in page_texts.items():
        if len(bboxes) >= sample_pages - 1:
            avg_bbox = [sum(b[i] for b in bboxes) / len(bboxes) for i in range(4)]
            common_bboxes.append(fitz.Rect(avg_bbox))
    return common_bboxes


def extract_title_from_content(doc):
    """
    Extracts the title by finding the largest font text in the top half of the first page.
    """
    try:
        first_page = doc[0]
        blocks = first_page.get_text("dict", sort=True)["blocks"]
        largest_font_size = 0
        title_candidate = ""
        # Heuristic: Title is likely in the top 60% of the page
        for b in blocks:
            if b['bbox'][3] < first_page.rect.height * 0.6:
                if 'lines' in b and b['lines'][0]['spans']:
                    size = b['lines'][0]['spans'][0]['size']
                    if size > largest_font_size:
                        largest_font_size = size
                        # Merge all text from the block to form the title
                        title_candidate = "".join(s['text'] for l in b['lines'] for s in l['spans']).strip()
        return title_candidate if title_candidate else None
    except Exception:
        return None


def extract_outline_from_toc(doc):
    """Extracts the outline from the PDF's embedded Table of Contents (bookmarks)."""
    toc = doc.get_toc()
    if not toc:
        return None
    outline = []
    level_map = {}
    for level, title, page in toc:
        if level not in level_map:
            next_h_level = f"H{len(level_map) + 1}"
            level_map[level] = next_h_level
        outline.append({
            "text": title.strip(),
            "level": level_map[level],
            "page": page
        })
    return outline if len(outline) > 2 else None


def extract_outline_with_heuristics(doc):
    """Extracts an outline using visual and structural heuristics."""
    body_size, _ = get_document_body_style(doc)
    header_footer_zones = get_header_footer_zones(doc)
    potential_headings = []
    prefix_regex = re.compile(r'^\s*((?:[IVXLCDM]+\b)|(?:[A-Z]\b)|(?:\d+(?:\.\d+)))\s[.\)]', re.IGNORECASE)
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict", sort=True)["blocks"]
        for block in blocks:
            block_rect = fitz.Rect(block['bbox'])
            if not block.get('lines') or not block['lines'][0]['spans']:
                continue
            if any(block_rect.intersects(zone) for zone in header_footer_zones):
                continue
            size = block['lines'][0]['spans'][0]['size']
            font = block['lines'][0]['spans'][0]['font']
            text = "".join(s['text'] for l in block['lines'] for s in l['spans']).strip()
            if not text or len(text) > 120:
                continue
            if size < body_size + 1:
                continue
            if not re.search(r'[a-zA-Z]', text):
                continue
            if prefix_regex.match(text):
                continue
            style_key = (round(size), font)
            potential_headings.append({
                "text": text,
                "page": page_num,
                "style_key": style_key
            })
    return classify_and_sort_headings(potential_headings)


def classify_and_sort_headings(headings):
    """Classifies a list of identified headings based on their style_key."""
    from collections import defaultdict
    style_to_headings = defaultdict(list)
    for h in headings:
        style_to_headings[h['style_key']].append(h)
    sorted_styles = sorted(style_to_headings.keys(), key=lambda x: (x[0], x[1]), reverse=True)
    level_map = {style: f"H{i+1}" for i, style in enumerate(sorted_styles[:4])}
    classified_headings = []
    # Assign levels to all headings, defaulting to H4 if not mapped
    for style, hs in style_to_headings.items():
        level = level_map.get(style, 'H4')
        for h in hs:
            h['level'] = level
            if 'style_key' in h:
                del h['style_key']
            classified_headings.append(h)
    classified_headings.sort(key=lambda x: (x['page'], x['level']))
    # Final pass: remove any internal keys from headings
    for h in classified_headings:
        h.pop('style_key', None)
        h.pop('score', None)
    return classified_headings
