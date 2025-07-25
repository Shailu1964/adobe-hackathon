# src/intelligence_core.py
from sentence_transformers import SentenceTransformer, util
import torch

class DocumentAnalyst:
    def __init__(self, model_path: str):
        # Load the model from the local path for offline use
        self.model = SentenceTransformer(model_path)

    def rank_sections(self, persona_job_text: str, document_sections: list):
        """
        Ranks document sections based on their relevance to a persona/job.

        Args:
            persona_job_text: A string combining the persona and job description.
            document_sections: A list of dicts, where each dict has 'doc_name',
                               'title', 'page', and 'content'.

        Returns:
            A list of ranked sections with scores.
        """
        if not document_sections or not persona_job_text:
            return []

        # Encode the query (persona + job)
        print(" - Encoding query...")
        query_embedding = self.model.encode(persona_job_text, convert_to_tensor=True)

        # Encode all the document sections' content
        print(f" - Encoding {len(document_sections)} document sections...")
        section_contents = [section['content'] for section in document_sections]
        section_embeddings = self.model.encode(section_contents, convert_to_tensor=True, show_progress_bar=True)

        # Calculate cosine similarity
        print(" - Calculating similarity scores...")
        cosine_scores = util.cos_sim(query_embedding, section_embeddings)

        # Add scores to each section and sort
        ranked_sections = []
        for i, section in enumerate(document_sections):
            section['importance_rank'] = round(cosine_scores[0][i].item(), 4) # Add score
            ranked_sections.append(section)
        
        # Sort by rank in descending order
        ranked_sections.sort(key=lambda x: x['importance_rank'], reverse=True)
        
        return ranked_sections