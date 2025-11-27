"""
PDF Generator Module
Regenerates PDF documents from structured data while preserving formatting.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import base64
from utils.font_mapper import get_reportlab_font

class PDFGenerator:
    def __init__(self, layout_data):
        """
        Initialize PDF generator with layout information.
        
        Args:
            layout_data (dict): Layout information from parsed PDF
        """
        self.layout = layout_data
        self.page_width = layout_data.get("pageWidth", 595)
        self.page_height = layout_data.get("pageHeight", 842)
        self.font_warnings = []
        
    def generate(self, fields, images):
        """
        Generate a new PDF from edited fields and images.
        
        Args:
            fields (list): List of text fields with content and formatting
            images (list): List of images with position and data
            
        Returns:
            tuple: (pdf_bytes, font_warnings)
        """
        # Create PDF in memory
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(self.page_width, self.page_height))
        
        # Draw images first (background layer)
        for img in images:
            self._draw_image(c, img)
        
        # Draw text fields
        for field in fields:
            self._draw_text_field(c, field)
        
        # Finalize PDF
        c.save()
        buffer.seek(0)
        
        return buffer.getvalue(), self.font_warnings
    
    def _draw_text_field(self, canvas_obj, field):
        """
        Draw a text field on the canvas with proper formatting.
        
        Args:
            canvas_obj: ReportLab canvas object
            field (dict): Field data with position, font, and content
        """
        position = field["position"]
        font_info = field["font"]
        text = field["value"]
        
        # Get appropriate font
        original_font = font_info.get("family", "Helvetica")
        is_bold = font_info.get("bold", False)
        is_italic = font_info.get("italic", False)
        
        font_name = get_reportlab_font(original_font, is_bold, is_italic)
        
        # Track font substitutions
        if original_font not in ["Helvetica", "Times-Roman", "Courier"]:
            warning = f"Font '{original_font}' substituted with '{font_name}'"
            if warning not in self.font_warnings:
                self.font_warnings.append(warning)
        
        # Set font and size
        font_size = font_info.get("size", 12)
        canvas_obj.setFont(font_name, font_size)
        
        # Set text color
        color = font_info.get("color", "#000000")
        rgb = self._hex_to_rgb(color)
        canvas_obj.setFillColorRGB(rgb[0], rgb[1], rgb[2])
        
        # Calculate position (PDF coordinates start from bottom-left)
        x = position["x"]
        y = self.page_height - position["y"] - position["height"]
        
        # Draw text
        canvas_obj.drawString(x, y, text)
    
    def _draw_image(self, canvas_obj, image):
        """
        Draw an image on the canvas.
        
        Args:
            canvas_obj: ReportLab canvas object
            image (dict): Image data with position and base64 content
        """
        position = image["position"]
        
        # Decode base64 image
        image_data = base64.b64decode(image["data"])
        image_buffer = io.BytesIO(image_data)
        
        # Create ImageReader object
        img_reader = ImageReader(image_buffer)
        
        # Calculate position (PDF coordinates start from bottom-left)
        x = position["x"]
        y = self.page_height - position["y"] - position["height"]
        width = position["width"]
        height = position["height"]
        
        # Draw image
        canvas_obj.drawImage(img_reader, x, y, width, height, preserveAspectRatio=True)
    
    def _hex_to_rgb(self, hex_color):
        """
        Convert hex color to RGB tuple (0-1 range).
        
        Args:
            hex_color (str): Hex color code (e.g., "#FF0000")
            
        Returns:
            tuple: RGB values in 0-1 range
        """
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)
    
    def generate_preview_image(self, fields, images):
        """
        Generate a preview image of the PDF for comparison.
        
        Args:
            fields (list): List of text fields
            images (list): List of images
            
        Returns:
            bytes: PNG image bytes
        """
        # For now, return the PDF itself
        # In a more advanced implementation, this could use pdf2image
        pdf_bytes, _ = self.generate(fields, images)
        return pdf_bytes
