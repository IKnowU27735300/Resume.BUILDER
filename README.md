# Image Editor with OCR

Extract text from images using OCR, edit the content, and regenerate images with preserved formatting.

## Features

- 📤 **Image Upload**: Upload images with text content
- 🔍 **OCR Extraction**: Automatically extract text using Tesseract OCR
- ✏️ **Edit Fields**: Modify extracted text in dynamic forms
- 🖼️ **Image Regeneration**: Regenerate images with edited text
- 🎨 **Format Preservation**: Maintains original layout and positioning
- 🔒 **Privacy First**: No file storage, all processing in memory

## Supported Image Formats

- **PNG** (.png) - Best for text clarity
- **JPEG** (.jpg, .jpeg) - Common format
- **BMP** (.bmp) - Bitmap images
- **TIFF** (.tiff) - High quality scans

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR** (system install required)

### Install Tesseract OCR

#### Windows
1. Download installer from: https://github.com/tesseract-ocr/tesseract/releases
2. Run installer (default path: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH or the app will auto-detect

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS
```bash
brew install tesseract
```

### Setup

1. **Navigate to backend directory**
   ```bash
   cd "s:/CLG/Projects/RESUME Builder/image-converter/backend"
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask server**
   ```bash
   python app.py
   ```
   Server will start at `http://localhost:5001`

4. **Open the frontend**
   - Open `image-converter/index.html` in your web browser
   - Or navigate from the main hub at `index.html`

## Usage

### Step 1: Upload Image
- Drag and drop an image or click to browse
- Image should contain clear, readable text
- Best results with high-contrast, printed text

### Step 2: Edit Extracted Text
- OCR automatically extracts text with positions
- Edit any field in the generated form
- Low confidence fields are marked with warnings

### Step 3: Download
- Click "Preview & Download"
- Review any OCR warnings
- Download the regenerated image

## How It Works

### OCR Text Extraction
```python
# Uses Tesseract OCR to extract text with bounding boxes
data = pytesseract.image_to_data(image)
# Returns: text, position (x, y, width, height), confidence
```

### Image Regeneration
```python
# 1. Load original image
# 2. Draw white rectangles over original text
# 3. Render new text at same positions
# 4. Save in original format
```

## Project Structure

```
image-converter/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── image_ocr.py           # OCR extraction module
│   ├── image_regenerator.py   # Image regeneration
│   └── requirements.txt       # Python dependencies
├── index.html                 # Main application page
├── styles.css                 # Premium styling
├── script.js                  # Frontend logic
└── README.md                  # This file
```

## API Endpoints

- `GET /api/health` - Health check and Tesseract status
- `POST /api/upload` - Upload image and extract text
- `POST /api/regenerate` - Regenerate image with edited text
- `POST /api/preview` - Get OCR warnings
- `POST /api/clear-session` - Clear session data

## Limitations

### OCR Accuracy
- **85-95%** for clear, printed text
- **Lower** for:
  - Handwritten text
  - Complex fonts
  - Poor image quality
  - Low contrast backgrounds

### Font Matching
- Exact font replication is difficult
- System estimates font family and size
- Uses closest available system font
- Perfect matching not guaranteed

### Best Practices
- Use high-resolution images (300+ DPI)
- Ensure good contrast between text and background
- Avoid rotated or skewed text
- Use standard fonts when possible

## Dependencies

```
Flask==3.0.0
Flask-CORS==4.0.0
Pillow==10.1.0
pytesseract==0.3.10
```

Plus **Tesseract OCR** (system install)

## Troubleshooting

### "Tesseract OCR not found"
- Install Tesseract OCR (see Installation section)
- Windows: Ensure installed at `C:\Program Files\Tesseract-OCR`
- Linux/Mac: Ensure `tesseract` is in PATH

### Low OCR Accuracy
- Use higher resolution images
- Improve image contrast
- Ensure text is horizontal
- Try preprocessing (denoise, sharpen)

### Text Positioning Issues
- OCR provides approximate positions
- Some adjustment may be needed
- Works best with simple layouts

## Browser Support

- Chrome (recommended)
- Firefox
- Edge
- Safari

## License

This project is for educational and personal use.

---

**Powered by Tesseract OCR** - Open source OCR engine
