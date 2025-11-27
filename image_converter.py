"""
Image Converter Module
Handles conversion between JPEG, PNG, HEIC, and SVG formats
"""

from PIL import Image
import io
import base64
import os

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIF_SUPPORT = True
except ImportError:
    HEIF_SUPPORT = False

try:
    import cairosvg
    SVG_SUPPORT = True
except ImportError:
    SVG_SUPPORT = False

class ImageConverter:
    """Handle image format conversions"""
    
    SUPPORTED_FORMATS = {
        'jpeg': {'ext': ['.jpg', '.jpeg'], 'mime': 'image/jpeg', 'has_alpha': False},
        'png': {'ext': ['.png'], 'mime': 'image/png', 'has_alpha': True},
        'heic': {'ext': ['.heic', '.heif'], 'mime': 'image/heic', 'has_alpha': True},
        'svg': {'ext': ['.svg'], 'mime': 'image/svg+xml', 'has_alpha': True}
    }
    
    def __init__(self):
        self.heif_support = HEIF_SUPPORT
        self.svg_support = SVG_SUPPORT
    
    def detect_format(self, file_bytes, filename):
        """
        Detect image format from bytes and filename
        
        Args:
            file_bytes: Image file bytes
            filename: Original filename
            
        Returns:
            str: Detected format (jpeg, png, heic, svg)
        """
        ext = os.path.splitext(filename.lower())[1]
        
        # Check by extension first
        for fmt, info in self.SUPPORTED_FORMATS.items():
            if ext in info['ext']:
                return fmt
        
        # Try to detect from image data
        try:
            img = Image.open(io.BytesIO(file_bytes))
            return img.format.lower()
        except:
            return None
    
    def convert(self, file_bytes, source_format, target_format, quality=90):
        """
        Convert image from source format to target format
        
        Args:
            file_bytes: Source image bytes
            source_format: Source format (jpeg, png, heic, svg)
            target_format: Target format (jpeg, png, heic, svg)
            quality: Quality for JPEG (1-100)
            
        Returns:
            tuple: (converted_bytes, mime_type, warnings)
        """
        warnings = []
        
        # Handle SVG source
        if source_format == 'svg':
            if not self.svg_support:
                raise Exception("SVG support not available. Install cairosvg.")
            
            # Convert SVG to PNG first, then to target
            png_bytes = cairosvg.svg2png(bytestring=file_bytes)
            img = Image.open(io.BytesIO(png_bytes))
        else:
            # Open image
            img = Image.open(io.BytesIO(file_bytes))
        
        # Handle target format
        if target_format == 'svg':
            warnings.append("Converting to SVG creates a rasterized SVG (not true vector)")
            # For SVG output, we'll create a simple SVG with embedded PNG
            return self._create_svg_wrapper(img), 'image/svg+xml', warnings
        
        elif target_format == 'jpeg':
            # Convert RGBA to RGB for JPEG
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
                warnings.append("Transparency removed (JPEG doesn't support transparency)")
            
            # Save as JPEG
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            return output.getvalue(), 'image/jpeg', warnings
        
        elif target_format == 'png':
            # Save as PNG
            output = io.BytesIO()
            img.save(output, format='PNG', optimize=True)
            return output.getvalue(), 'image/png', warnings
        
        elif target_format == 'heic':
            if not self.heif_support:
                raise Exception("HEIC support not available. Install pillow-heif.")
            
            # Save as HEIC
            output = io.BytesIO()
            img.save(output, format='HEIF', quality=quality)
            return output.getvalue(), 'image/heic', warnings
        
        else:
            raise Exception(f"Unsupported target format: {target_format}")
    
    def _create_svg_wrapper(self, img):
        """Create SVG with embedded raster image"""
        # Convert image to PNG bytes
        png_buffer = io.BytesIO()
        img.save(png_buffer, format='PNG')
        png_base64 = base64.b64encode(png_buffer.getvalue()).decode('utf-8')
        
        # Create SVG
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
     width="{img.width}" height="{img.height}" viewBox="0 0 {img.width} {img.height}">
    <image width="{img.width}" height="{img.height}" 
           xlink:href="data:image/png;base64,{png_base64}"/>
</svg>'''
        return svg.encode('utf-8')
    
    def get_image_info(self, file_bytes):
        """
        Get information about an image
        
        Args:
            file_bytes: Image file bytes
            
        Returns:
            dict: Image information
        """
        try:
            img = Image.open(io.BytesIO(file_bytes))
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_kb': len(file_bytes) / 1024
            }
        except Exception as e:
            return {'error': str(e)}
