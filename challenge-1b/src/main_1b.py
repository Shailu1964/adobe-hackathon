import os
import json
import re
import fitz  # PyMuPDF
from datetime import datetime, timezone
from intelligence_core import DocumentAnalyst
from pdf_utils import extract_outline_with_heuristics

def get_section_text(doc, outline):
    """
    Extracts the full text content for each section defined in the outline.
    """
    for i, section in enumerate(outline):
        start_page = section['page'] - 1
        end_page = doc.page_count - 1
        next_section_start_y = float('inf')

        if i + 1 < len(outline):
            next_section = outline[i + 1]
            if next_section['page'] > section['page']:
                end_page = next_section['page'] - 1
            else:
                end_page = start_page
                for block in doc[start_page].get_text("dict", sort=True)["blocks"]:
                    if "lines" in block:
                        block_text = "".join(span['text'] for line in block['lines'] for span in line['spans']).strip()
                        if next_section['text'] in block_text:
                            next_section_start_y = block['bbox'][1]
                            break
        
        content = []
        for page_num in range(start_page, end_page + 1):
            page = doc[page_num]
            current_section_y0 = 0
            if page_num == start_page:
                 for block in page.get_text("dict", sort=True)["blocks"]:
                    if "lines" in block:
                        block_text = "".join(span['text'] for line in block['lines'] for span in line['spans']).strip()
                        if section['text'] in block_text:
                            current_section_y0 = block['bbox'][3] 
                            break

            blocks = page.get_text("dict", sort=True)["blocks"]
            for block in blocks:
                if "lines" in block:
                    block_y0 = block['bbox'][1]
                    if (page_num > start_page) or (page_num == start_page and block_y0 >= current_section_y0):
                        if page_num == end_page and block_y0 >= next_section_start_y:
                            break
                        
                        block_text = "".join(span['text'] for line in block['lines'] for span in line['spans'])
                        content.append(block_text.strip())

        section['content'] = " ".join(content) if content else section['text']
        
    return outline

# --- IMPROVED FUNCTION FOR SUB-SECTION ANALYSIS ---
def perform_sub_section_analysis(sections_to_analyze, analyst, query_text, num_sub_sections=5):
    """
    Analyzes the content of a diverse pool of sections to find the most relevant sentences.
    """
    print(f"\nPerforming sub-section analysis on {len(sections_to_analyze)} diverse sections...")
    all_sentences = []
    
    # 1. Split content into sentences, filtering out titles
    for section in sections_to_analyze:
        sentences = re.split(r'(?<=[.?!])\s+', section['content'])
        for sentence in sentences:
            clean_sentence = sentence.strip()
            # **IMPROVEMENT**: Filter out short strings and sentences that are just the title
            if clean_sentence and len(clean_sentence.split()) > 3 and clean_sentence.lower() != section['section_title'].lower():
                all_sentences.append({
                    "content": clean_sentence,
                    "document": section['document'],
                    "page_number": section['page_number']
                })

    if not all_sentences:
        print(" - No suitable sentences found for sub-section analysis.")
        return []

    # 2. Rank the sentences
    ranked_sentences = analyst.rank_sections(query_text, all_sentences)
    
    # 3. Format top N sentences, ensuring no duplicates
    sub_section_results = []
    seen_sentences = set()
    for sentence_obj in ranked_sentences:
        # **IMPROVEMENT**: De-duplicate sentences
        if sentence_obj['content'] not in seen_sentences:
            sub_section_results.append({
                "document": sentence_obj['document'],
                "page_number": sentence_obj['page_number'],
                "refined_text": sentence_obj['content'],
                "importance_rank": sentence_obj['importance_rank']
            })
            seen_sentences.add(sentence_obj['content'])
        # Stop when we have enough unique snippets
        if len(sub_section_results) >= num_sub_sections:
            break
        
    print(f"✅ Sub-section analysis complete. Found {len(sub_section_results)} unique refined snippets.")
    return sub_section_results

# --- NEW HELPER FUNCTION TO DIVERSIFY SECTION POOL ---
def create_diverse_section_pool(ranked_sections):
    """
    Selects a variety of sections based on keywords to create a balanced pool for analysis.
    """
    print("\nCreating a diverse pool of sections for deeper analysis...")
    
    diverse_pool = []
    seen_titles = set()

    # Keywords to categorize sections
    category_keywords = {
        'activity': ['tours', 'things to do', 'adventures', 'sports', 'nightlife', 'hiking', 'shopping', 'experiences'],
        'food': ['cuisine', 'restaurants', 'dishes', 'culinary', 'wine', 'food'],
        'place': ['cities', 'city', 'marseille', 'nice', 'avignon', 'history', 'sites'],
        'logistics': ['tips', 'packing', 'hotels', 'guide', 'introduction', 'conclusion', 'planning']
    }

    # Add the #1 overall ranked section regardless of category
    if ranked_sections:
        top_section = ranked_sections[0]
        diverse_pool.append(top_section)
        seen_titles.add(top_section['section_title'])

    # Find the best section for each category
    for category, keywords in category_keywords.items():
        for section in ranked_sections:
            if section['section_title'] not in seen_titles:
                title_lower = section['section_title'].lower()
                if any(keyword in title_lower for keyword in keywords):
                    diverse_pool.append(section)
                    seen_titles.add(section['section_title'])
                    break # Move to the next category once one is found
    
    print(f" - Diverse pool contains {len(diverse_pool)} sections.")
    return diverse_pool


def main():
    # --- 1. Setup Paths ---
    try:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    except NameError:
        PROJECT_ROOT = os.path.abspath(".")

    INPUT_DIR = os.path.join(PROJECT_ROOT, 'input')
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
    MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'all-MiniLM-L6-v2')
    
    # --- 2. Load Inputs ---
    persona_file_path = os.path.join(INPUT_DIR, 'Collection 1.json')
    with open(persona_file_path, 'r', encoding='utf-8') as f:
        input_data = json.load(f)

    persona = input_data.get("Collection 1", {})
    job_to_be_done = input_data.get("job_to_be_done", {})
    documents_info = input_data.get("documents", [])

    role = persona.get("role", "user")
    expertise = persona.get("expertise", "general interest")
    task = job_to_be_done.get("task", "find relevant information")
    query_text = f"As a {role} with expertise in {expertise}, I need to {task}."

    pdf_filenames = [doc['filename'] for doc in documents_info if doc.get('filename')]
    doc_dir = os.path.join(INPUT_DIR, 'Collection 1')
    
    # --- 3. Extract Sections from all PDFs ---
    all_sections = []
    print("Processing PDF documents...")
    for pdf_file in pdf_filenames:
        pdf_path = os.path.join(doc_dir, pdf_file)
        if not os.path.exists(pdf_path):
            print(f"Warning: PDF file not found at {pdf_path}. Skipping.")
            continue
            
        print(f" - Extracting sections from {pdf_file}")
        doc = fitz.open(pdf_path)
        
        outline = extract_outline_with_heuristics(doc)
        sections_with_content = get_section_text(doc, outline)
        
        for section in sections_with_content:
            all_sections.append({
                "document": pdf_file,
                "page_number": section['page'],
                "section_title": section['text'],
                "content": section['content']
            })
        doc.close()

    if not all_sections:
        print("Error: No sections were extracted from any PDF. Cannot proceed.")
        return

    # --- 4. Rank Sections ---
    print("\nRanking sections based on relevance...")
    analyst = DocumentAnalyst(model_path=MODEL_PATH)
    ranked_sections = analyst.rank_sections(query_text, all_sections)

    # --- 5. Perform Sub-Section Analysis on a DIVERSE pool of sections ---
    sections_for_analysis = create_diverse_section_pool(ranked_sections)
    sub_section_results = perform_sub_section_analysis(sections_for_analysis, analyst, query_text)

    # --- 6. Format Final Output ---
    output_data = {
        "metadata": {
            "input_documents": [doc['filename'] for doc in documents_info],
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.now(timezone.utc).isoformat()
        },
        "extracted_sections": [
            {
                "document": s['document'],
                "page_number": s['page_number'],
                "section_title": s['section_title'],
                "importance_rank": s['importance_rank']
            } for s in ranked_sections[:10]
        ],
        "sub_section_analysis": sub_section_results
    }

    # --- 7. Write Final Result ---
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    output_file_path = os.path.join(OUTPUT_DIR, 'challenge1b_output.json')
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Successfully generated final Round 1B output at: {output_file_path}")


if __name__ == "__main__":
    main()