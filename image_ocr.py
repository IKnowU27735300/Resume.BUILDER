"""
Image OCR Module
Extracts text with positions from images using Tesseract OCR
"""

import pytesseract
from PIL import Image
import io
import re

class ImageOCR:
    """Extract text and layout information from images using OCR"""
    
    def __init__(self):
        # Try to set Tesseract path (Windows default)
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        except:
            pass  # Use system PATH
    
    def extract_text_fields(self, image_bytes):
        """
        Extract text with positions from image
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            dict: Structured data with fields, layout info
        """
        # Open image
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Extract text with bounding boxes
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        # Parse OCR results
        fields = []
        field_id = 0
        
        for i in range(len(ocr_data['text'])):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            
            # Only include text with reasonable confidence
            if text and conf > 30:
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                w = ocr_data['width'][i]
                h = ocr_data['height'][i]
                
                # Estimate font size from height
                font_size = max(10, int(h * 0.8))
                
                # Infer label from content
                label = self._infer_label(text, y, field_id)
                
                fields.append({
                    "id": f"field_{field_id}",
                    "label": label,
                    "value": text,
                    "position": {
                        "x": x,
                        "y": y,
                        "width": w,
                        "height": h
                    },
                    "font": {
                        "family": "Arial",  # Default font
                        "size": font_size,
                        "color": "#000000",
                        "bold": False,
                        "italic": False
                    },
                    "confidence": conf
                })
                field_id += 1
        
        # Get layout info
        layout = {
            "pageWidth": img.width,
            "pageHeight": img.height,
            "format": img.format or "JPEG"
        }
        
        return {
            "fields": fields,
            "layout": layout,
            "metadata": {
                "totalFields": len(fields),
                "imageFormat": img.format or "JPEG",
                "dimensions": f"{img.width}x{img.height}"
            }
        }
    
    def _infer_label(self, text, y_pos, field_id):
        """
        Infer a meaningful label for a text field
        
        Args:
            text (str): The text content
            y_pos (int): Y position
            field_id (int): Field identifier
            
        Returns:
            str: Inferred label
        """
        text_lower = text.lower()
        
        # Check for common patterns
        if '@' in text and '.' in text:
            return "Email"
        elif re.match(r'^\+?\d[\d\s\-\(\)]+$', text):
            return "Phone Number"
        elif any(keyword in text_lower for keyword in ['name', 'title']):
            return "Name/Title"
        elif any(keyword in text_lower for keyword in ['address', 'location', 'city']):
            return "Address"
        elif any(keyword in text_lower for keyword in ['company', 'organization']):
            return "Company"
        elif any(keyword in text_lower for keyword in ['date', 'year']):
            return "Date"
        elif len(text) > 50:
            return f"Description {field_id}"
        elif y_pos < 150:
            return f"Header Text {field_id}"
        else:
            return f"Text Field {field_id}"
    
    def get_full_text(self, image_bytes):
        """
        Get all text from image as a single string
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            str: Extracted text
        """
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        return pytesseract.image_to_string(img)
    
    def check_tesseract_installed(self):
        """
        Check if Tesseract is installed
        
        Returns:
            bool: True if Tesseract is available
        """
        try:
            pytesseract.get_tesseract_version()
            return True
        except:
            return False
