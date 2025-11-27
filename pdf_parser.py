"""
PDF Parser Module
Extracts text, images, fonts, and layout information from PDF resumes.
"""

import fitz  # PyMuPDF
import base64
import io
from PIL import Image

class PDFParser:
    def __init__(self, pdf_bytes):
        """
        Initialize PDF parser with PDF file bytes.
        
        Args:
            pdf_bytes: PDF file content as bytes
        """
        self.pdf_bytes = pdf_bytes
        self.doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.page = self.doc[0]  # Assume single-page resume
        
    def parse(self):
        """
        Parse the PDF and extract all relevant information.
        
        Returns:
            dict: Structured data containing fields, images, and layout info
        """
        fields = self._extract_text_fields()
        images = self._extract_images()
        layout = self._extract_layout()
        
        return {
            "fields": fields,
            "images": images,
            "layout": layout,
            "metadata": {
                "pageCount": len(self.doc),
                "hasText": len(fields) > 0,
                "hasImages": len(images) > 0
            }
        }
    
    def _extract_text_fields(self):
        """
        Extract text content with position and font information.
        
        Returns:
            list: List of text field dictionaries
        """
        fields = []
        blocks = self.page.get_text("dict")["blocks"]
        field_id = 0
        
        for block in blocks:
            if block["type"] == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span["text"].strip()
                        if text:  # Only include non-empty text
                            bbox = span["bbox"]
                            font_info = {
                                "family": span["font"],
                                "size": round(span["size"], 1),
                                "color": self._rgb_to_hex(span["color"]),
                                "bold": "Bold" in span["font"],
                                "italic": "Italic" in span["font"] or "Oblique" in span["font"]
                            }
                            
                            # Infer field label based on position and content
                            label = self._infer_label(text, bbox, field_id)
                            
                            fields.append({
                                "id": f"field_{field_id}",
                                "label": label,
                                "value": text,
                                "position": {
                                    "x": round(bbox[0], 2),
                                    "y": round(bbox[1], 2),
                                    "width": round(bbox[2] - bbox[0], 2),
                                    "height": round(bbox[3] - bbox[1], 2)
                                },
                                "font": font_info
                            })
                            field_id += 1
        
        return fields
    
    def _extract_images(self):
        """
        Extract images from the PDF.
        
        Returns:
            list: List of image dictionaries with base64 encoded data
        """
        images = []
        image_list = self.page.get_images()
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = self.doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Get image position on page
            img_rects = self.page.get_image_rects(xref)
            if img_rects:
                rect = img_rects[0]
                
                # Convert to base64 for JSON serialization
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                
                # Get image dimensions
                pil_image = Image.open(io.BytesIO(image_bytes))
                
                images.append({
                    "id": f"img_{img_index}",
                    "position": {
                        "x": round(rect.x0, 2),
                        "y": round(rect.y0, 2),
                        "width": round(rect.width, 2),
                        "height": round(rect.height, 2)
                    },
                    "data": image_base64,
                    "format": base_image["ext"],
                    "dimensions": {
                        "width": pil_image.width,
                        "height": pil_image.height
                    }
                })
        
        return images
    
    def _extract_layout(self):
        """
        Extract page layout information.
        
        Returns:
            dict: Layout information including page size and margins
        """
        rect = self.page.rect
        
        # Estimate margins by finding the outermost content
        blocks = self.page.get_text("dict")["blocks"]
        min_x = rect.width
        min_y = rect.height
        max_x = 0
        max_y = 0
        
        for block in blocks:
            bbox = block["bbox"]
            min_x = min(min_x, bbox[0])
            min_y = min(min_y, bbox[1])
            max_x = max(max_x, bbox[2])
            max_y = max(max_y, bbox[3])
        
        # Calculate margins
        margin_left = round(min_x, 2) if min_x < rect.width else 50
        margin_top = round(min_y, 2) if min_y < rect.height else 50
        margin_right = round(rect.width - max_x, 2) if max_x > 0 else 50
        margin_bottom = round(rect.height - max_y, 2) if max_y > 0 else 50
        
        return {
            "pageWidth": round(rect.width, 2),
            "pageHeight": round(rect.height, 2),
            "margins": {
                "top": margin_top,
                "right": margin_right,
                "bottom": margin_bottom,
                "left": margin_left
            }
        }
    
    def _infer_label(self, text, bbox, field_id):
        """
        Infer a meaningful label for a text field based on content and position.
        
        Args:
            text (str): The text content
            bbox (tuple): Bounding box coordinates
            field_id (int): Field identifier
            
        Returns:
            str: Inferred label
        """
        text_lower = text.lower()
        
        # Check for common resume sections
        if any(keyword in text_lower for keyword in ['name', 'title']):
            return "Name/Title"
        elif '@' in text and '.' in text:
            return "Email"
        elif any(keyword in text_lower for keyword in ['phone', 'mobile', 'tel']):
            return "Phone"
        elif any(keyword in text_lower for keyword in ['address', 'location', 'city']):
            return "Address"
        elif any(keyword in text_lower for keyword in ['experience', 'work', 'employment']):
            return "Work Experience Section"
        elif any(keyword in text_lower for keyword in ['education', 'degree', 'university', 'college']):
            return "Education Section"
        elif any(keyword in text_lower for keyword in ['skill', 'expertise', 'proficiency']):
            return "Skills Section"
        elif any(keyword in text_lower for keyword in ['summary', 'objective', 'profile']):
            return "Summary/Objective"
        else:
            # Generic label based on position
            y_pos = bbox[1]
            if y_pos < 150:
                return f"Header Text {field_id}"
            else:
                return f"Content {field_id}"
    
    def _rgb_to_hex(self, rgb_int):
        """
        Convert RGB integer to hex color code.
        
        Args:
            rgb_int (int): RGB color as integer
            
        Returns:
            str: Hex color code
        """
        # PyMuPDF returns color as integer, convert to hex
        r = (rgb_int >> 16) & 0xFF
        g = (rgb_int >> 8) & 0xFF
        b = rgb_int & 0xFF
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def is_scanned(self):
        """
        Check if the PDF appears to be a scanned document (image-only).
        
        Returns:
            bool: True if PDF appears to be scanned
        """
        text = self.page.get_text().strip()
        images = self.page.get_images()
        
        # If there are images but very little text, likely scanned
        return len(images) > 0 and len(text) < 50
    
    def close(self):
        """Close the PDF document."""
        if self.doc:
            self.doc.close()
