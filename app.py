"""
Flask API Server for Resume Builder
Handles PDF upload, parsing, regeneration, and export.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import traceback

from pdf_parser import PDFParser
from pdf_generator import PDFGenerator
from docx_exporter import DOCXExporter
from utils.validators import validate_upload

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Store parsed data temporarily (in production, use session storage or Redis)
session_data = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Resume Builder API is running"})

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """
    Handle PDF upload and parsing.
    
    Returns:
        JSON with parsed fields, images, and layout information
    """
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        is_valid, error_message = validate_upload(file)
        
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Read file bytes
        pdf_bytes = file.read()
        
        # Parse PDF
        parser = PDFParser(pdf_bytes)
        
        # Check if scanned
        if parser.is_scanned():
            parser.close()
            return jsonify({
                "error": "This appears to be a scanned PDF (image-only). Please upload a PDF with extractable text.",
                "suggestion": "OCR support coming soon!"
            }), 400
        
        # Parse content
        parsed_data = parser.parse()
        parser.close()
        
        # Store original PDF bytes for preview comparison
        session_id = str(hash(pdf_bytes))[:16]
        session_data[session_id] = {
            "original_pdf": pdf_bytes,
            "parsed_data": parsed_data
        }
        
        # Return parsed data with session ID
        return jsonify({
            "sessionId": session_id,
            "data": parsed_data,
            "message": "PDF parsed successfully"
        }), 200
        
    except Exception as e:
        print(f"Error in upload_pdf: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to parse PDF: {str(e)}"}), 500

@app.route('/api/regenerate', methods=['POST'])
def regenerate_pdf():
    """
    Regenerate PDF from edited data.
    
    Expects JSON:
    {
        "sessionId": "...",
        "fields": [...],
        "images": [...]
    }
    
    Returns:
        PDF file as download
    """
    try:
        data = request.json
        session_id = data.get('sessionId')
        fields = data.get('fields', [])
        images = data.get('images', [])
        
        # Retrieve session data
        if session_id not in session_data:
            return jsonify({"error": "Invalid session ID"}), 400
        
        layout = session_data[session_id]["parsed_data"]["layout"]
        
        # Generate new PDF
        generator = PDFGenerator(layout)
        pdf_bytes, font_warnings = generator.generate(fields, images)
        
        # Return PDF file
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='resume_edited.pdf'
        ), 200
        
    except Exception as e:
        print(f"Error in regenerate_pdf: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to regenerate PDF: {str(e)}"}), 500

@app.route('/api/export-docx', methods=['POST'])
def export_docx():
    """
    Export resume as DOCX file.
    
    Expects JSON:
    {
        "sessionId": "...",
        "fields": [...],
        "images": [...]
    }
    
    Returns:
        DOCX file as download
    """
    try:
        data = request.json
        session_id = data.get('sessionId')
        fields = data.get('fields', [])
        images = data.get('images', [])
        
        # Retrieve session data
        if session_id not in session_data:
            return jsonify({"error": "Invalid session ID"}), 400
        
        layout = session_data[session_id]["parsed_data"]["layout"]
        
        # Generate DOCX
        exporter = DOCXExporter(layout)
        docx_bytes = exporter.export(fields, images)
        
        # Return DOCX file
        return send_file(
            io.BytesIO(docx_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name='resume_edited.docx'
        ), 200
        
    except Exception as e:
        print(f"Error in export_docx: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to export DOCX: {str(e)}"}), 500

@app.route('/api/preview', methods=['POST'])
def generate_preview():
    """
    Generate preview comparison data.
    
    Expects JSON:
    {
        "sessionId": "...",
        "fields": [...],
        "images": [...]
    }
    
    Returns:
        JSON with font warnings and validation info
    """
    try:
        data = request.json
        session_id = data.get('sessionId')
        fields = data.get('fields', [])
        images = data.get('images', [])
        
        # Retrieve session data
        if session_id not in session_data:
            return jsonify({"error": "Invalid session ID"}), 400
        
        layout = session_data[session_id]["parsed_data"]["layout"]
        
        # Generate preview to check for warnings
        generator = PDFGenerator(layout)
        _, font_warnings = generator.generate(fields, images)
        
        return jsonify({
            "fontWarnings": font_warnings,
            "message": "Preview generated successfully"
        }), 200
        
    except Exception as e:
        print(f"Error in generate_preview: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to generate preview: {str(e)}"}), 500

@app.route('/api/clear-session', methods=['POST'])
def clear_session():
    """Clear session data for a new upload."""
    try:
        data = request.json
        session_id = data.get('sessionId')
        
        if session_id in session_data:
            del session_data[session_id]
        
        return jsonify({"message": "Session cleared"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Resume Builder API Server Starting...")
    print("Server running at: http://localhost:5000")
    print("Upload endpoint: http://localhost:5000/api/upload")
    app.run(debug=True, host='0.0.0.0', port=5000)
