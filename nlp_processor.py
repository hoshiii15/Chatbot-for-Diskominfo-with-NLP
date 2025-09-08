import nltk
import json
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from fuzzywuzzy import fuzz
import numpy as np

class NLPProcessor:
    def __init__(self, faq_file=None):
        print("Initializing NLP Processor...")
        self._download_nltk_data()
        print("Loading Sastrawi components...")
        self.stemmer = StemmerFactory().create_stemmer()
        self.stopword_remover = StopWordRemoverFactory().create_stop_word_remover()
        self.vectorizer = TfidfVectorizer()
        self.faq_file = faq_file or 'faq_stunting.json'
        self.load_faq_data(self.faq_file)
        self.prepare_corpus()
        print("NLP Processor initialized successfully!")
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
            print("NLTK punkt tokenizer already downloaded")
        except LookupError:
            print("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
            print("NLTK stopwords already downloaded")
        except LookupError:
            print("Downloading NLTK stopwords...")
            nltk.download('stopwords')
    
    def load_faq_data(self, faq_file=None):
        """Load FAQ data from JSON file (default: faq_stunting.json)"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_name = faq_file or self.faq_file or 'faq_stunting.json'
            faq_path = os.path.join(current_dir, 'data', file_name)
            print(f"Loading FAQ data from: {faq_path}")
            with open(faq_path, 'r', encoding='utf-8') as file:
                # Support both array and dict with 'faqs' key
                data = json.load(file)
                if isinstance(data, dict) and 'faqs' in data:
                    self.faqs = data['faqs']
                else:
                    self.faqs = data
            print(f"Loaded {len(self.faqs)} FAQ entries")
        except FileNotFoundError:
            print(f"ERROR: FAQ data file not found! ({faq_file})")
            self.faqs = []
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON format: {e}")
            self.faqs = []
        except Exception as e:
            print(f"ERROR: Failed to load FAQ data: {e}")
            self.faqs = []
    def switch_faq(self, faq_file):
        """Switch FAQ data to another file and re-prepare corpus"""
        self.faq_file = faq_file
        self.load_faq_data(faq_file)
        self.prepare_corpus()
    
    def preprocess_text(self, text):
        """Preprocess Indonesian text"""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        try:
            text = self.stopword_remover.remove(text)
        except Exception as e:
            print(f"Warning: Stopword removal failed: {e}")
        try:
            text = self.stemmer.stem(text)
        except Exception as e:
            print(f"Warning: Stemming failed: {e}")
        
        return text
    
    def prepare_corpus(self):
        """Prepare corpus for TF-IDF"""
        if not self.faqs:
            print("No FAQ data available for corpus preparation")
            self.processed_questions = []
            self.question_to_faq = []
            return
        
        print("Preparing corpus for TF-IDF...")
        
        self.processed_questions = []
        self.question_to_faq = []
        
        for faq in self.faqs:
            for question in faq['questions']:
                processed_q = self.preprocess_text(question)
                if processed_q:
                    self.processed_questions.append(processed_q)
                    self.question_to_faq.append(faq)
        
        print(f"Processed {len(self.processed_questions)} questions")
        
        if self.processed_questions:
            try:
                self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_questions)
                print("TF-IDF matrix created successfully")
            except Exception as e:
                print(f"ERROR: Failed to create TF-IDF matrix: {e}")
                self.tfidf_matrix = None
        else:
            self.tfidf_matrix = None
    
    def find_best_answer(self, user_question, threshold=0.2):
        """Find the best answer for user question"""
        if not self.processed_questions or self.tfidf_matrix is None:
            print("No processed questions available")
            return None, 0
        processed_user_q = self.preprocess_text(user_question)
        
        if not processed_user_q:
            print("Processed user question is empty")
            return None, 0
        
        try:
            user_tfidf = self.vectorizer.transform([processed_user_q])
            similarities = cosine_similarity(user_tfidf, self.tfidf_matrix).flatten()
            fuzzy_scores = []
            for q in self.processed_questions:
                fuzzy_score = fuzz.ratio(processed_user_q, q) / 100.0
                fuzzy_scores.append(fuzzy_score)
            combined_scores = 0.7 * similarities + 0.3 * np.array(fuzzy_scores)
            best_idx = np.argmax(combined_scores)
            best_score = combined_scores[best_idx]
            
            print(f"Best match score: {best_score:.3f} (threshold: {threshold})")
            
            if best_score >= threshold:
                return self.question_to_faq[best_idx], best_score
            else:
                return None, best_score
                
        except Exception as e:
            print(f"Error in finding best answer: {e}")
            return None, 0
    
    def get_response(self, user_question, env=None):
        """Get response for user question, with env-aware fallback"""
        print(f"Processing question: {user_question}")
        best_faq, confidence = self.find_best_answer(user_question)
        if best_faq:
            response = {
                'answer': best_faq['answer'],
                'confidence': float(confidence),
                'category': best_faq['category'],
                'faq_id': best_faq['id'],
                'status': 'found'
            }
            
            # Include links if available
            if 'links' in best_faq and best_faq['links']:
                response['links'] = best_faq['links']
                
                # Optional: Format answer with clickable links for HTML display
                formatted_answer = best_faq['answer']
                if best_faq['links']:
                    formatted_answer += "\n\nLink terkait:"
                    for link in best_faq['links']:
                        formatted_answer += f"\n• {link['text']}: {link['url']}"
                
                response['formatted_answer'] = formatted_answer
            
            print(f"Answer found with confidence: {confidence:.3f}")
            if 'links' in response:
                print(f"Including {len(response['links'])} links in response")
        else:
            # Fallback sesuai env
            env_key = env or self.faq_file.replace('.json','')
            if 'ppid' in env_key:
                fallback_answers = [
                    "Maaf, saya tidak dapat menemukan jawaban yang tepat untuk pertanyaan Anda.",
                    "Berikut beberapa topik yang bisa saya bantu:",
                    "• Apa itu PPID?",
                    "• Cara permohonan informasi publik",
                    "• Prosedur pengajuan keberatan",
                    "• Jenis informasi publik",
                    "• Layanan website PPID",
                    "• Kontak dan alamat PPID",
                    "",
                    "Silakan ajukan pertanyaan dengan kata kunci yang lebih spesifik, atau hubungi petugas PPID untuk informasi lebih lanjut."
                ]
            else:
                fallback_answers = [
                    "Maaf, saya tidak dapat menemukan jawaban yang tepat untuk pertanyaan Anda.",
                    "Berikut beberapa topik yang bisa saya bantu:",
                    "• Apa itu stunting?",
                    "• Penyebab dan cara mencegah stunting",
                    "• Gizi ibu hamil dan ASI eksklusif", 
                    "• MPASI dan nutrisi anak",
                    "• Imunisasi dan posyandu",
                    "",
                    "Silakan ajukan pertanyaan dengan kata kunci yang lebih spesifik, atau hubungi petugas kesehatan untuk informasi lebih lanjut."
                ]
            response = {
                'answer': "\n".join(fallback_answers),
                'confidence': float(confidence),
                'category': 'unknown',
                'faq_id': None,
                'status': 'not_found'
            }
            print(f"No suitable answer found. Confidence: {confidence:.3f}")
        return response
    
    def get_all_categories(self):
        """Get all available categories"""
        if not self.faqs:
            return []
        
        categories = list(set(faq['category'] for faq in self.faqs))
        return sorted(categories)
    
    def get_questions_by_category(self, category):
        """Get all questions for a specific category"""
        if not self.faqs:
            return []
        
        questions = []
        for faq in self.faqs:
            if faq['category'] == category:
                questions.extend(faq['questions'])
        
        return questions

if __name__ == "__main__":
    print("=== Testing NLP Processor ===")
    
    try:
        processor = NLPProcessor()
        
        test_questions = [
            "apa itu stunting?",
            "bagaimana cara mencegah stunting?", 
            "apa saja gejala stunting?",
            "kenapa anak bisa stunting?",
            "asi eksklusif berapa lama?",
            "pertanyaan yang tidak ada jawabannya"
        ]
        
        print("\n=== Testing Questions ===")
        for question in test_questions:
            print(f"\nQ: {question}")
            response = processor.get_response(question)
            print(f"A: {response['answer'][:150]}...")
            print(f"Confidence: {response['confidence']:.3f}")
            print(f"Category: {response['category']}")
            print(f"Status: {response['status']}")
            print("-" * 50)
            
        print("\n=== Available Categories ===")
        categories = processor.get_all_categories()
        for cat in categories:
            print(f"- {cat}")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()