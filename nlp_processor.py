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
        self._init_ppid_categories()
        print("NLP Processor initialized successfully!")
    
    def _init_ppid_categories(self):
        """Initialize PPID information categories with keywords"""
        self.ppid_categories = {
            "profil_badan_publik": {
                "keywords": [
                    "kedudukan", "domisili", "alamat kantor", "visi misi", "tugas fungsi", 
                    "struktur organisasi", "profil pimpinan", "profil pegawai", "profil ppid", 
                    "struktur ppid", "lhkpn", "lhkan"
                ],
                "description": "Informasi tentang profil badan publik"
            },
            "program_kegiatan": {
                "keywords": [
                    "program kegiatan", "penanggungjawab program", "pelaksana program", "target capaian", 
                    "jadwal pelaksanaan", "sumber anggaran", "kak program", "agenda pelaksanaan",
                    "e-samsat", "layanan online disdukcapil", "harga barang kebutuhan pokok",
                    "penerimaan pegawai", "penerimaan peserta didik"
                ],
                "description": "Ringkasan program dan kegiatan yang sedang dijalankan"
            },
            "kinerja": {
                "keywords": [
                    "laporan kinerja", "lkjip", "sakip", "sistem akuntabilitas kinerja",
                    "ikplhd", "kinerja pengelolaan lingkungan", "lkpj", "laporan keterangan pertanggungjawaban"
                ],
                "description": "Ringkasan informasi tentang kinerja"
            },
            "laporan_keuangan": {
                "keywords": [
                    "kua", "kebijakan umum apbd", "ppas", "prioritas plafon anggaran", "apbd",
                    "anggaran pendapatan belanja", "daftar aset", "calk", "catatan laporan keuangan",
                    "neraca keuangan", "lra", "laporan realisasi anggaran", "laporan operasional",
                    "laporan arus kas", "laporan perubahan ekuitas", "laporan perubahan saldo anggaran",
                    "opini bpk", "rka", "rencana kerja anggaran", "dpa", "dokumen pelaksanaan anggaran",
                    "rko", "rencana kerja operasional", "rfk", "realisasi fisik keuangan",
                    "lkpd", "laporan keuangan pemerintah daerah"
                ],
                "description": "Ringkasan laporan keuangan"
            },
            "akses_informasi": {
                "keywords": [
                    "laporan layanan informasi", "infografis laporan", "register permohonan",
                    "rekapitulasi pelayanan", "indeks kepuasan masyarakat"
                ],
                "description": "Laporan akses informasi publik"
            },
            "peraturan_keputusan": {
                "keywords": [
                    "daftar peraturan", "daftar keputusan", "pembentukan rancangan peraturan",
                    "dokumen pendukung", "jdih dprd", "jaringan dokumentasi informasi hukum"
                ],
                "description": "Informasi tentang peraturan, keputusan, dan/atau kebijakan"
            },
            "tata_cara_informasi": {
                "keywords": [
                    "hak memperoleh informasi", "tata cara memperoleh informasi", 
                    "tata cara pengajuan keberatan", "proses penyelesaian sengketa",
                    "tata cara fasilitasi sengketa"
                ],
                "description": "Informasi tentang hak dan tata cara memperoleh informasi publik"
            },
            "pengaduan": {
                "keywords": [
                    "tata cara pengaduan", "penyalahgunaan wewenang", "pelanggaran",
                    "penggunaan aplikasi lapor", "pengaduan pelayanan informasi",
                    "formulir pengaduan", "standar pelayanan inspektorat",
                    "hasil penanganan pengaduan"
                ],
                "description": "Informasi tentang tata cara pengaduan penyalahgunaan wewenang atau pelanggaran"
            },
            "pengadaan_barang_jasa": {
                "keywords": [
                    "pengadaan barang", "pengadaan jasa", "tahap perencanaan", "sirup",
                    "rencana umum pengadaan", "tahap pemilihan", "tahap pelaksanaan",
                    "lpse", "layanan pengadaan elektronik", "proyek strategis"
                ],
                "description": "Pengumuman pengadaan barang dan jasa"
            },
            "ketenagakerjaan": {
                "keywords": [
                    "e-makaryo", "lowongan pekerjaan", "info lowongan", "penerimaan calon pegawai"
                ],
                "description": "Informasi tentang ketenagakerjaan"
            },
            "kependudukan": {
                "keywords": [
                    "profil perkembangan kependudukan", "buku data kependudukan", "profil gender"
                ],
                "description": "Informasi tentang kependudukan"
            },
            "peringatan_dini_bencana": {
                "keywords": [
                    "informasi kebencanaan", "peringatan dini", "prosedur evakuasi",
                    "keadaan darurat", "peta rawan bencana"
                ],
                "description": "Informasi prosedur peringatan dini bencana"
            },
            "sop": {
                "keywords": [
                    "sop", "standar operasional prosedur", "penyusunan daftar informasi",
                    "pelayanan permohonan informasi", "pelayanan informasi inklusi",
                    "uji konsekuensi informasi", "penanganan keberatan",
                    "fasilitasi sengketa", "maklumat pelayanan", "pengumuman informasi",
                    "standar biaya perolehan", "pelayanan informasi terintegrasi"
                ],
                "description": "Standar Operasional Prosedur"
            }
        }
    
    def check_ppid_category(self, question):
        """Check if question relates to PPID information categories"""
        question_lower = question.lower()
        
        for category, data in self.ppid_categories.items():
            for keyword in data["keywords"]:
                # Check for exact match atau fuzzy match dengan threshold lebih tinggi
                if keyword in question_lower or fuzz.partial_ratio(keyword, question_lower) > 85:
                    return {
                        "category": category,
                        "description": data["description"],
                        "matched_keyword": keyword
                    }
        return None
    
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
    
    def generate_ppid_response(self, ppid_info):
        """Generate response for PPID information query"""
        return {
            'answer': f"{ppid_info['description']} dapat ditemukan di",
            'confidence': 0.95,
            'category': 'ppid_informasi',
            'faq_id': ppid_info['category'],
            'status': 'ppid_link',
            'matched_keyword': ppid_info['matched_keyword'],
            'links': [{
                'text': 'Lihat Daftar Informasi Berkala PPID',
                'url': 'https://ppid.sukoharjokab.go.id/daftar-informasi-berkala/'
            }]
        }
    
    def get_response(self, user_question, env=None):
        """Get response for user question, with env-aware fallback"""
        print(f"Processing question: {user_question}")
        
        # Check for PPID information categories first
        ppid_info = self.check_ppid_category(user_question)
        if ppid_info:
            print(f"PPID category detected: {ppid_info['category']} (keyword: {ppid_info['matched_keyword']})")
            return self.generate_ppid_response(ppid_info)
        
        # Continue with regular FAQ matching
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