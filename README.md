# 🤖 Multi-Domain FAQ Chatbot - Assistant untuk Diskominfo

Aplikasi chatbot FAQ berbasis NLP (Natural Language Processing) yang dikembangkan untuk membantu masyarakat mendapatkan informasi terkait berbagai layanan Diskominfo Kota Sukoharjo secara otomatis dan responsif.

## 📋 Deskripsi

Chatbot ini mendukung dua domain utama:

### 🏛️ PPID (Pejabat Pengelola Informasi dan Dokumentasi)

Menjawab pertanyaan seputar layanan PPID, seperti:

- Informasi tentang PPID
- Jenis layanan yang tersedia
- Cara pengajuan permohonan informasi
- Waktu pemrosesan
- Biaya layanan
- Prosedur keberatan informasi

### 👶 Stunting Prevention

Memberikan informasi tentang pencegahan stunting, meliputi:

- Pengertian stunting dan penyebabnya
- Gizi dan nutrisi untuk ibu hamil
- Makanan bergizi untuk anak
- Tanda-tanda stunting pada anak
- Program pemerintah terkait stunting
- Tips pencegahan stunting

## ✨ Fitur Utama

### 🎯 Core Features

- **Multi-Domain Support**: Mendukung PPID dan Stunting Prevention
- **Natural Language Processing**: Memahami pertanyaan dalam bahasa Indonesia
- **Real-time Response**: Jawaban instant untuk pertanyaan umum
- **Template Questions**: Pertanyaan template yang dapat di-collapse
- **Responsive Design**: Mendukung desktop dan mobile dengan UI yang optimal
- **Environment Switching**: Dapat beralih antara mode PPID dan Stunting

### 📱 Mobile Features

- **Slide-in Interface**: Chatbot slide dari kiri di mobile
- **Touch-optimized**: Button dan input yang ramah sentuhan
- **Collapsible Templates**: Template pertanyaan yang dapat disembunyikan
- **Full-width Send Button**: Tombol kirim memanjang penuh di mobile

### 🎨 UI/UX Features

- **Modern Design**: Interface yang bersih dan user-friendly
- **Smooth Animations**: Transisi yang halus dan engaging
- **Typing Indicator**: Indikator saat bot sedang memproses
- **Message Bubbles**: Chat bubble yang intuitif

## 🛠️ Teknologi yang Digunakan

### Backend

- **Python 3.x**: Language utama
- **Flask**: Web framework untuk API
- **NLTK**: Natural Language Processing
- **scikit-learn**: Machine learning untuk similarity matching
- **JSON**: Database FAQ sederhana

### Frontend

- **HTML5**: Struktur halaman
- **CSS3**: Styling dengan responsive design
- **Vanilla JavaScript**: Interaktifitas tanpa dependency
- **ES6 Classes**: Struktur kode yang terorganisir

### Deployment

- **ngrok**: Tunneling untuk development dan testing

## 📁 Struktur Project

```
python-bot/
├── app.py                 # Main Flask application
├── nlp_processor.py       # NLP processing logic
├── test_api.py           # API testing script
├── requirements.txt      # Python dependencies
├── bot.log              # Application logs
├── data/
│   ├── faq_ppid.json    # FAQ data untuk PPID
│   └── faq_stunting.json # FAQ data untuk Stunting
├── __pycache__/         # Python cache files
└── README.md           # Project documentation
```

## 🚀 Instalasi dan Setup

### Prerequisites

- Python 3.7 atau lebih tinggi
- pip (Python package manager)
- Git

### 1. Clone Repository

```bash
git clone https://github.com/hoshiii15/Chatbot-for-Diskominfo-with-NLP.git
cd Chatbot-for-Diskominfo-with-NLP
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download NLTK Data

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### 4. Jalankan Aplikasi

```bash
python app.py
```

Server akan berjalan di `http://localhost:5000`

### 5. Setup ngrok (Opsional untuk Testing)

```bash
# Install ngrok terlebih dahulu
ngrok http 5000
```

## 🔧 Konfigurasi

### Environment Variables

Tidak ada environment variables khusus yang diperlukan untuk development lokal.

### FAQ Data

Edit file FAQ sesuai dengan domain yang diinginkan:

**PPID FAQ (`data/faq_ppid.json`):**

```json
{
  "faqs": [
    {
      "question": "Apa itu PPID?",
      "answer": "PPID adalah Pejabat Pengelola Informasi dan Dokumentasi..."
    }
  ]
}
```

**Stunting FAQ (`data/faq_stunting.json`):**

```json
{
  "faqs": [
    {
      "question": "Apa itu stunting?",
      "answer": "Stunting adalah kondisi gagal tumbuh pada anak..."
    }
  ]
}
```

## 📖 Penggunaan

### API Endpoints

#### POST /ask

Endpoint utama untuk bertanya ke chatbot.

**Request untuk PPID:**

```json
{
  "question": "Apa itu PPID?",
  "env": "ppid"
}
```

**Request untuk Stunting:**

```json
{
  "question": "Apa itu stunting?",
  "env": "stunting"
}
```

**Response:**

```json
{
  "answer": "PPID adalah Pejabat Pengelola Informasi dan Dokumentasi...",
  "confidence": 0.85
}
```

#### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-09-07T07:00:00"
}
```

### Domain Environment

Chatbot mendukung dua environment:

- `"ppid"`: Untuk pertanyaan seputar PPID
- `"stunting"`: Untuk pertanyaan seputar pencegahan stunting

## 🧪 Testing

### Manual Testing

```bash
python test_api.py
```

### API Testing dengan curl

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test PPID endpoint
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Apa itu PPID?", "env": "ppid"}'

# Test Stunting endpoint
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Apa itu stunting?", "env": "stunting"}'
```

## 🔒 CORS Configuration

Aplikasi sudah dikonfigurasi untuk menerima request dari domain manapun:

```python
CORS(app, origins=['*'])
```

Untuk production, disarankan untuk membatasi origins:

```python
CORS(app, origins=['https://yourdomain.com'])
```

### Template Questions

Tambah/edit pertanyaan template di HTML sesuai domain:

## 🐛 Troubleshooting

### Common Issues

1. **CORS Error**: Pastikan Flask-CORS terinstall dan dikonfigurasi
2. **NLTK Data Missing**: Jalankan `nltk.download()` untuk download data
3. **Port Already in Use**: Ganti port di `app.py` atau stop proses yang menggunakan port 5000
4. **ngrok Connection**: Pastikan ngrok terinstall dan running

### Logging

Check file `bot.log` untuk error logs dan debugging.

## 🚀 Deployment

### Production Deployment

1. Use production WSGI server (Gunicorn, uWSGI)
2. Configure proper CORS origins
3. Use environment variables untuk konfigurasi
4. Setup SSL/HTTPS
5. Use proper database instead of JSON files

### Docker Deployment (Coming Soon)

```dockerfile
# Dockerfile akan ditambahkan di versi selanjutnya
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Guidelines

- Untuk menambah domain baru, buat file JSON di folder `data/`
- Update `nlp_processor.py` untuk mendukung environment baru
- Buat widget HTML terpisah untuk setiap domain
- Test kedua environment sebelum commit

## 📊 Data Sources

### PPID FAQ

Data FAQ PPID bersumber dari:

- Peraturan perundang-undangan tentang keterbukaan informasi publik
- Panduan layanan PPID Kota Sukoharjo
- FAQ umum dari masyarakat

### Stunting FAQ

Data FAQ Stunting bersumber dari:

- Panduan Kementerian Kesehatan RI
- Program pencegahan stunting nasional
- Edukasi gizi dan kesehatan anak

## 👥 Team

**Dikembangkan oleh Hosea Raka (Anak Magang Diskominfo Kota Sukoharjo)**

- **Role**: Full Stack Development
- **Focus**: NLP, Web Development, UI/UX
- **Contact**: [GitHub](https://github.com/hoshiii15)

## 🙏 Acknowledgments

- Tim Diskominfo Kota Sukoharjo
- NLTK Community
- Flask Community
- Semua pihak yang mendukung pengembangan aplikasi ini

## 📞 Support

Jika mengalami masalah atau memiliki pertanyaan:

1. Check dokumentasi ini terlebih dahulu
2. Check Issues di GitHub repository
3. Create new issue dengan detail yang lengkap

---

**Made with ❤️ for Diskominfo Kota Sukoharjo**
