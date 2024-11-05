import os
import PyPDF2
from difflib import get_close_matches
from nltk.corpus import wordnet
from trie import Trie

class InformationRetrieval:
    def __init__(self, doc_folder):
        self.doc_folder = doc_folder
        self.docs_content = {}  # Dictionary to hold document content
        self.indexed_words = set()  # Set to hold all words in the documents
        self.trie = Trie()  # Trie for auto-suggestions

    def index_documents(self):
        # Index all documents in the given folder
        for filename in os.listdir(self.doc_folder):
            if filename.endswith('.pdf'):
                file_path = os.path.join(self.doc_folder, filename)
                with open(file_path, 'rb') as file:
                    try:
                        reader = PyPDF2.PdfReader(file)
                        content = ""
                        for page in range(len(reader.pages)):
                            content += reader.pages[page].extract_text()
                        content = content.lower()
                        self.docs_content[filename] = content
                        
                        # Index words for fuzzy matching and synonym search
                        words = content.split()
                        self.indexed_words.update(words)
                        
                        # Insert words into Trie for auto-suggestions
                        for word in words:
                            self.trie.insert(word)
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")
    
    def fuzzy_match(self, query, threshold=0.8):
        """Find the closest matches for the query in the indexed words."""
        return get_close_matches(query, self.indexed_words, n=5, cutoff=threshold)

    def get_synonyms(self, query):
        """Get synonyms of the query word using WordNet."""
        synonyms = set()
        for syn in wordnet.synsets(query):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name().lower())  # Add synonyms to the set
        return list(synonyms)

    def search(self, query):
        # Search for the query, fuzzy matches, and synonyms in indexed documents
        query = query.lower()
        
        # Get exact matches, fuzzy matches, and synonyms
        exact_matches = self.search_exact(query)
        fuzzy_matches = self.fuzzy_match(query)
        synonym_matches = self.get_synonyms(query)

        # Combine results if no exact matches are found
        if not exact_matches:
            combined_results = []
            
            # Fuzzy match results
            if fuzzy_matches:
                for match in fuzzy_matches:
                    combined_results.extend(self.search_exact(match))
            
            # Synonym match results
            if synonym_matches:
                for synonym in synonym_matches:
                    combined_results.extend(self.search_exact(synonym))

            return combined_results
        
        return exact_matches

    def search_exact(self, query):
        """Search for the exact word in the indexed documents."""
        search_results = []
        for doc, content in self.docs_content.items():
            word_count = content.count(query)  # Count occurrences of the word
            if word_count > 0:
                snippet = content[:100]  # Get a snippet (first 100 characters)
                search_results.append((doc, word_count, snippet))  # Append the document, count, and snippet

        # Sort the results by the word count (descending order)
        search_results.sort(key=lambda x: x[1], reverse=True)
        return search_results

    def auto_suggest(self, prefix):
        """Provide auto-suggestions based on the user's query prefix."""
        return self.trie.search(prefix)

    def expand_query(self, query):
        """Provide query expansion using synonyms and common phrases."""
        expanded_terms = set()
        
        # Add synonyms
        synonyms = self.get_synonyms(query)
        expanded_terms.update(synonyms)
        
        # Add similar words based on fuzzy matches
        fuzzy_matches = self.fuzzy_match(query)
        expanded_terms.update(fuzzy_matches)

        return list(expanded_terms)