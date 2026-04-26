import os
from typing import List, Dict

class KnowledgeRetriever:
    """
    A simple RAG (Retrieval-Augmented Generation) component that retrieves 
    music theory insights based on user intent.
    """
    def __init__(self, kb_path: str = "data/knowledge_base"):
        self.kb_path = kb_path
        self.documents = []
        self._load_docs()

    def _load_docs(self):
        if not os.path.exists(self.kb_path):
            return
        for filename in os.listdir(self.kb_path):
            if filename.endswith(".txt"):
                with open(os.path.join(self.kb_path, filename), "r") as f:
                    content = f.read()
                    # Split into sections by '#' headers
                    sections = content.split("#")
                    for section in sections:
                        if section.strip():
                            self.documents.append(section.strip())

    def retrieve_insight(self, query: str, genre: str, mood: str) -> str:
        """
        Retrieves the most relevant music theory snippet for the given intent.
        """
        search_terms = [genre.lower(), mood.lower()]
        
        best_doc = ""
        max_matches = 0
        
        for doc in self.documents:
            matches = sum(1 for term in search_terms if term in doc.lower())
            if matches > max_matches:
                max_matches = matches
                best_doc = doc
        
        if best_doc:
            # Extract just the explanation, skip the header
            lines = best_doc.split("\n")
            return "\n".join(lines[1:]).strip()
        
        return "Music theory suggests that matching rhythm to heart rate optimizes the listening experience."
