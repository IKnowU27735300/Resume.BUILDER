"""
Image Regenerator Module
Regenerates images with edited text while preserving layout
"""

from PIL import Image, ImageDraw, ImageFont
import io

class ImageRegenerator:
    """Regenerate images with edited text"""
    
    def __init__(self, layout_data):
        """
        Initialize regenerator with layout information
        
        Args:
            layout_data (dict): Layout information from OCR
        """
        self.layout = layout_data
        self.width = layout_data.get("pageWidth", 800)
        self.height = layout_data.get("pageHeight", 1000)
        self.format = layout_data.get("format", "JPEG")
    
    def regenerate(self, original_bytes, fields):
        """
        Regenerate image with edited text
        
        Args:
            original_bytes: Original image bytes
            fields (list): List of text fields with edited content
            
        Returns:
            bytes: Regenerated image bytes
        """
        # Load original image
        img = Image.open(io.BytesIO(original_bytes))
        
        # Convert to RGB if needed
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        
        # Create drawing context
        draw = ImageDraw.Draw(img)
        
        # Process each field
        for field in fields:
            self._draw_text_field(draw, field, img)
        
        # Save to bytes
        output = io.BytesIO()
        
        # Save with appropriate format
        if self.format == 'PNG' or img.mode == 'RGBA':
            img.save(output, format='PNG', optimize=True)
        else:
            # Convert RGBA to RGB for JPEG
            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img
            img.save(output, format='JPEG', quality=95, optimize=True)
        
        return output.getvalue()
    
    def _draw_text_field(self, draw, field, img):
        """
        Draw a text field on the image
        
        Args:
            draw: PIL ImageDraw object
            field (dict): Field data with position, font, and content
            img: PIL Image object
        """
        position = field["position"]
        font_info = field["font"]
        text = field["value"]
        
        # Get position
        x = position["x"]
        y = position["y"]
        width = position["width"]
        height = position["height"]
        
        # Clear original text area with white rectangle
        draw.rectangle(
            [(x-2, y-2), (x + width + 2, y + height + 2)],
            fill='white'
        )
        
        # Get font
        font_size = font_info.get("size", 12)
        font = self._get_font(font_info.get("family", "Arial"), font_size)
        
        # Get color
        color = font_info.get("color", "#000000")
        if color.startswith('#'):
            color = self._hex_to_rgb(color)
        
        # Draw text
        try:
            draw.text((x, y), text, font=font, fill=color)
        except Exception as e:
            # Fallback to default font if custom font fails
            draw.text((x, y), text, fill=color)
    
    def _get_font(self, font_family, font_size):
        """
        Get PIL font object
        
        Args:
            font_family (str): Font family name
            font_size (int): Font size
            
        Returns:
            ImageFont: PIL font object
        """
        # Try to load TrueType font
        font_paths = [
            f"C:/Windows/Fonts/{font_family}.ttf",
            f"C:/Windows/Fonts/arial.ttf",
            f"C:/Windows/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
        ]
        
        for path in font_paths:
            try:
                return ImageFont.truetype(path, font_size)
            except:
                continue
        
        # Fallback to default font
        try:
            return ImageFont.load_default()
        except:
            return None
    
    def _hex_to_rgb(self, hex_color):
        """
        Convert hex color to RGB tuple
        
        Args:
            hex_color (str): Hex color code (e.g., "#FF0000")
            
        Returns:
            tuple: RGB values
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def create_preview(self, original_bytes, fields):
        """
        Create a preview image (same as regenerate for now)
        
        Args:
            original_bytes: Original image bytes
            fields (list): List of text fields
            
        Returns:
            bytes: Preview image bytes
        """
        return self.regenerate(original_bytes, fields)
