# Resume Builder - PDF Editor

A sophisticated web application that allows users to upload PDF resumes, edit content through dynamically generated forms, and regenerate documents while preserving original formatting.

## Features

- 📤 **Easy Upload**: Drag & drop or click to upload PDF resumes
- ✏️ **Smart Editing**: Automatically generated forms based on PDF content
- 🎨 **Format Preservation**: Maintains original fonts, spacing, and layout
- 🖼️ **Image Support**: Detect and replace images in your resume
- 📄 **Multiple Formats**: Export to both PDF and DOCX
- 🔄 **Unlimited Usage**: Edit and regenerate as many times as needed
- 🔒 **Privacy First**: No file storage, all processing in memory

## Technology Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **PyMuPDF (fitz)** - PDF parsing
- **ReportLab** - PDF generation
- **python-docx** - DOCX export

### Frontend
- **HTML5** - Structure
- **CSS3** - Premium styling with glassmorphism
- **Vanilla JavaScript** - Application logic

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd "s:/CLG/Projects/RESUME Builder"
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start the Flask server**
   ```bash
   python app.py
   ```
   Server will start at `http://localhost:5000`

4. **Open the frontend**
   - Open `index.html` in your web browser
   - Or use a local server (recommended):
     ```bash
     # Using Python
     python -m http.server 8000
     ```
   - Navigate to `http://localhost:8000`

## Usage

1. **Upload Resume**
   - Drag and drop your PDF resume or click to browse
   - Maximum file size: 5 MB
   - PDF format only (with extractable text)

2. **Edit Content**
   - Modify text fields as needed
   - Replace images if desired
   - All formatting will be preserved

3. **Preview & Download**
   - Review any font substitution warnings
   - Download as PDF or DOCX format
   - Repeat the process unlimited times

## Project Structure

```
RESUME Builder/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── pdf_parser.py          # PDF parsing logic
│   ├── pdf_generator.py       # PDF regeneration
│   ├── docx_exporter.py       # DOCX export
│   ├── requirements.txt       # Python dependencies
│   └── utils/
│       ├── font_mapper.py     # Font substitution handling
│       └── validators.py      # File validation
├── index.html                 # Main application page
├── styles.css                 # Premium styling
├── script.js                  # Frontend logic
└── README.md                  # This file
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/upload` - Upload and parse PDF
- `POST /api/regenerate` - Generate edited PDF
- `POST /api/export-docx` - Export as DOCX
- `POST /api/preview` - Get preview warnings
- `POST /api/clear-session` - Clear session data

## Limitations

- **Layout Fidelity**: Achieves 85-95% accuracy for most resumes
- **Font Embedding**: Some fonts may be substituted with similar alternatives
- **Scanned PDFs**: Image-only PDFs are not supported (OCR coming soon)
- **Complex Layouts**: Multi-column or table-heavy layouts may require manual adjustment

## Security

- File size validation (max 5 MB)
- PDF format validation
- No permanent file storage
- In-memory processing only
- CORS enabled for frontend communication

## Browser Support

- Chrome (recommended)
- Firefox
- Edge
- Safari

## Future Enhancements

- OCR support for scanned PDFs
- Template-based reconstruction for complex layouts
- Real-time preview comparison
- Custom font upload
- Batch processing

## License

This project is for educational and personal use.

## Support

For issues or questions, please check the console logs for detailed error messages.

---

**Built with ❤️ for seamless resume editing**
