from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
from nlp_processor import NLPProcessor


app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting NLP Processor initialization...")
    nlp_processor = NLPProcessor()
    logger.info("NLP Processor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize NLP Processor: {e}")
    nlp_processor = None

# Mapping environment to FAQ file
ENV_FAQ_MAP = {
    'stunting': 'faq_stunting.json',
    'ppid': 'faq_ppid.json'
}

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'FAQ Chatbot is running',
        'nlp_ready': nlp_processor is not None,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'supported_envs': list(ENV_FAQ_MAP.keys())
    })

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle FAQ questions for multiple environments"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Question is required',
                'status': 'error'
            }), 400
        question = data['question'].strip()
        if not question:
            return jsonify({
                'error': 'Question cannot be empty',
                'status': 'error'
            }), 400
        if len(question) > 500:
            return jsonify({
                'error': 'Question too long (max 500 characters)',
                'status': 'error'
            }), 400
        if not nlp_processor:
            return jsonify({
                'answer': 'Maaf, sistem FAQ sedang tidak tersedia. Silakan coba lagi nanti.',
                'confidence': 0.0,
                'category': 'system_error',
                'status': 'error'
            }), 503
        # Ambil parameter lingkungan (env), default ke 'stunting' jika tidak ada
        env = data.get('env', 'stunting').lower()
        faq_file = ENV_FAQ_MAP.get(env, 'faq_stunting.json')
        # Ganti FAQ jika berbeda
        if nlp_processor.faq_file != faq_file:
            nlp_processor.switch_faq(faq_file)
        response = nlp_processor.get_response(question, env=env)
        logger.info(f"Question: {question}")
        logger.info(f"Env: {env} | FAQ file: {faq_file}")
        logger.info(f"Category: {response['category']}")
        logger.info(f"Confidence: {response['confidence']:.3f}")
        logger.info(f"Status: {response['status']}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({
            'answer': 'Maaf, terjadi kesalahan sistem. Silakan coba lagi nanti.',
            'confidence': 0.0,
            'category': 'system_error',
            'status': 'error'
        }), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get available FAQ categories for selected environment"""
    try:
        env = request.args.get('env', 'stunting').lower()
        faq_file = ENV_FAQ_MAP.get(env, 'faq_stunting.json')
        if nlp_processor.faq_file != faq_file:
            nlp_processor.switch_faq(faq_file)
        if not nlp_processor or not nlp_processor.faqs:
            return jsonify({'categories': []})
        categories = nlp_processor.get_all_categories()
        # Deskripsi kategori generik
        generic_desc = {
            'umum': 'Informasi umum',
            'prosedur': 'Prosedur permohonan dan keberatan',
            'informasi': 'Jenis informasi publik',
            'kontak': 'Informasi kontak',
            'layanan': 'Layanan website',
            # kategori stunting
            'definisi': 'Pengertian dan definisi stunting',
            'penyebab': 'Faktor penyebab terjadinya stunting',
            'gejala': 'Ciri-ciri dan tanda-tanda stunting',
            'pencegahan': 'Cara mencegah stunting',
            'dampak': 'Akibat dan dampak stunting',
            'asi': 'ASI eksklusif dan menyusui',
            'mpasi': 'Makanan pendamping ASI',
            'gizi_ibu': 'Gizi dan nutrisi ibu hamil',
            'posyandu': 'Posyandu dan pemantauan',
            'periode_emas': '1000 hari pertama kehidupan'
        }
        result = []
        for cat in categories:
            result.append({
                'category': cat,
                'description': generic_desc.get(cat, cat.replace('_', ' ').title())
            })
        return jsonify({'categories': result})
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({'categories': []})

@app.route('/faqs', methods=['GET'])
def get_all_faqs():
    """Get all FAQ data for selected environment"""
    try:
        env = request.args.get('env', 'stunting').lower()
        faq_file = ENV_FAQ_MAP.get(env, 'faq_stunting.json')
        if nlp_processor.faq_file != faq_file:
            nlp_processor.switch_faq(faq_file)
        if not nlp_processor:
            return jsonify({'faqs': []})
        return jsonify({'faqs': nlp_processor.faqs})
    except Exception as e:
        logger.error(f"Error getting FAQs: {e}")
        return jsonify({'faqs': []})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get bot statistics for selected environment"""
    try:
        env = request.args.get('env', 'stunting').lower()
        faq_file = ENV_FAQ_MAP.get(env, 'faq_stunting.json')
        if nlp_processor.faq_file != faq_file:
            nlp_processor.switch_faq(faq_file)
        if not nlp_processor:
            return jsonify({
                'total_faqs': 0,
                'total_questions': 0,
                'categories': 0,
                'env': env,
                'status': 'error'
            })
        total_questions = sum(len(faq['questions']) for faq in nlp_processor.faqs)
        return jsonify({
            'total_faqs': len(nlp_processor.faqs),
            'total_questions': total_questions,
            'categories': len(nlp_processor.get_all_categories()),
            'env': env,
            'status': 'active'
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'total_faqs': 0,
            'total_questions': 0,
            'categories': 0,
            'env': env,
            'status': 'error'
        })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    logger.info("Starting FAQ Bot Server...")
    logger.info("Server will run on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
    