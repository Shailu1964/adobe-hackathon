import fitz  # PyMuPDF
import json
import os
import re
from collections import Counter

def get_style_identifier(span):
    """Creates a unique identifier for a text style."""
    return f"{span['font']}_{span['size']:.0f}_{'bold' if 'bold' in span['font'].lower() else ''}"

def analyze_styles(doc):
    """
    Analyzes the document to find the most common text style (body)
    and potential heading styles.
    """
    style_counts = Counter()
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        # Ignore very small text or table-like data
                        if s['size'] > 6:
                            style_counts[get_style_identifier(s)] += 1
    
    # Assume the most frequent style is the body text
    if not style_counts:
        return {}, {}
        
    body_style = style_counts.most_common(1)[0][0]
    body_size = float(body_style.split('_')[1])

    # Consider styles with larger font size than body text as headings
    # This heuristic is a good starting point.
    # Format: {'style_identifier': (size, is_bold)}
    heading_styles = {}
    for style, count in style_counts.items():
        parts = style.split('_')
        size = float(parts[1])
        is_bold = parts[2] == 'bold'
        if size > body_size:
            heading_styles[style] = (size, is_bold)
            
    # Sort heading styles primarily by size (desc), then by boldness
    sorted_headings = sorted(heading_styles.items(), key=lambda item: (item[1][0], item[1][1]), reverse=True)
    
    # Map the top 3 sorted styles to H1, H2, H3
    level_map = {}
    if len(sorted_headings) > 0: level_map[sorted_headings[0][0]] = "H1"
    if len(sorted_headings) > 1: level_map[sorted_headings[1][0]] = "H2"
    if len(sorted_headings) > 2: level_map[sorted_headings[2][0]] = "H3"
    
    return level_map

def process_pdf(pdf_path, style_level_map):
    """
    Extracts the title and a structured outline from a PDF document
    using the pre-analyzed style map.
    """
    doc = fitz.open(pdf_path)
    outline = []
    title = os.path.basename(pdf_path) # Fallback title

    # Heuristic for title: often the largest text on the first page
    try:
        first_page = doc[0]
        blocks = sorted(first_page.get_text("dict")["blocks"], key=lambda b: b['bbox'][1])
        largest_size = 0
        potential_title = ""
        for b in blocks[:5]: # Check top 5 blocks
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        if s["size"] > largest_size:
                            largest_size = s["size"]
                            potential_title = s["text"].strip()
        if potential_title:
             title = potential_title
    except Exception:
        pass

    # Extract headings based on the style map
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    # Concatenate spans in a line to form a single heading
                    line_text = "".join(s["text"] for s in l["spans"]).strip()
                    if not line_text:
                        continue
                        
                    span = l["spans"][0] # Use the style of the first span
                    style_id = get_style_identifier(span)
                    
                    if style_id in style_level_map:
                        # Simple rule to avoid adding stray text as headings
                        if len(line_text) > 2 and re.search('[a-zA-Z]', line_text):
                            outline.append({
                                "level": style_level_map[style_id],
                                "text": line_text,
                                "page": page_num + 1
                            })
                            # Break after finding a heading in a line to avoid duplicates
                            break 

    return {"title": title, "outline": outline}


if __name__ == "__main__":
    # Define directories relative to the script's location
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    INPUT_DIR = os.path.join(PROJECT_ROOT, "input")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            print(f"Processing {filename}...")
            try:
                # First, analyze the entire doc to build a style hierarchy
                doc = fitz.open(pdf_path)
                style_map = analyze_styles(doc)
                doc.close() # Close the doc before processing
                
                # Now, extract content using the identified styles
                result = process_pdf(pdf_path, style_map)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                print(f"✅ Successfully created {output_filename}")

            except Exception as e:
                print(f"❌ Failed to process {filename}. Error: {e}")