import fitz  # PyMuPDF
import json
import os
import logging
from pdf_utils import (
    get_document_body_style,
    get_header_footer_zones,
    extract_title_from_content,
    extract_outline_from_toc,
    extract_outline_with_heuristics,
    classify_and_sort_headings
)

# --- CORE EXTRACTION LOGIC ---

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





def classify_and_sort_headings(headings):
    """Classifies a list of identified headings based on their style_key."""
    if not headings:
        return []
        
    style_to_headings = defaultdict(list)
    for h in headings:
        style_to_headings[h['style_key']].append(h)
    
    sorted_styles = sorted(style_to_headings.keys(), key=lambda x: (x[0], x[1]), reverse=True)
    level_map = {style: f"H{i+1}" for i, style in enumerate(sorted_styles[:4])}
    
    classified_headings = []
    for style, level in level_map.items():
        for h in style_to_headings[style]:
            h['level'] = level
            del h['style_key']
            classified_headings.append(h)
            
    classified_headings.sort(key=lambda x: (x['page'], x['level']))
    return classified_headings

def extract_universal_outline(pdf_path):
    """Main function to extract an outline, returning an empty title if none is found."""
    doc = fitz.open(pdf_path)
    if not doc.page_count:
        return {"title": "", "outline": []}

    # Start with an empty title as the default
    title = ""
    # --- Title Extraction ---
    # Look for the largest text on the first page for the title.
    # Combine adjacent lines if they have similar large font sizes.
    try:
        first_page = doc[0]
        blocks = first_page.get_text("dict", sort=True)["blocks"]
        
        font_sizes = [s['size'] for b in blocks if 'lines' in b for l in b['lines'] for s in l['spans']]
        if not font_sizes:
            raise Exception("No text found on first page")
            
        largest_size = max(font_sizes)
        # Consider fonts within 95% of the largest size as part of the title
        title_texts = [
            s['text'].strip() 
            for b in blocks if 'lines' in b 
            for l in b['lines'] 
            for s in l['spans'] 
            if abs(s['size'] - largest_size) < largest_size * 0.05
        ]
        title = " ".join(dict.fromkeys(title_texts)) # Use dict.fromkeys to remove duplicates
    except Exception as e:
        print(f"Could not determine title automatically: {e}")
        title = os.path.basename(pdf_path)

    
    # 2. If metadata fails, try extracting from content
    if not title:
        content_title = extract_title_from_content(doc)
        if content_title and len(content_title) >= 4:
            title = content_title
    
    # --- Outline extraction remains the same ---
    # 'title' will be an empty string if both methods above failed.
    outline = extract_outline_from_toc(doc)
    if not outline:
        logging.warning(f"No valid TOC found in '{os.path.basename(pdf_path)}'. Falling back to heuristics.")
        outline = extract_outline_with_heuristics(doc)

    return {"title": title, "outline": outline}

# --- Main Execution Block ---
if __name__ == "__main__":
    import argparse
    from tqdm import tqdm

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("process.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    parser = argparse.ArgumentParser(description="Batch PDF Outline Extractor")
    parser.add_argument('--input-dir', type=str, default=None, help='Input directory with PDF files')
    parser.add_argument('--output-dir', type=str, default=None, help='Output directory for JSON files')
    parser.add_argument('--sample-pages', type=int, default=3, help='Number of sample pages for header/footer detection')
    args = parser.parse_args()

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    INPUT_DIR = args.input_dir or os.path.join(PROJECT_ROOT, "input")
    OUTPUT_DIR = args.output_dir or os.path.join(PROJECT_ROOT, "output")
    SAMPLE_PAGES = args.sample_pages

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logging.info(f"Created output directory at: {OUTPUT_DIR}")

    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        logging.info(f"Created dummy input directory at: {INPUT_DIR}")
        logging.info("Please place your PDF files there.")

    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        logging.warning(f"No PDF files found in {INPUT_DIR}. Exiting.")

    for filename in tqdm(pdf_files, desc="Processing PDFs"):
        pdf_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(filename)[0] + ".json")
        logging.info(f"Processing '{filename}'...")
        try:
            result = extract_universal_outline(pdf_path)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            logging.info(f"✅ Successfully created JSON for '{filename}'")
        except Exception as e:
            logging.error(f"❌ Failed to process '{filename}'. Error: {e}", exc_info=True)