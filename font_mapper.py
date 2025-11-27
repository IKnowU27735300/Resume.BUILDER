"""
Font mapping utility to handle font substitutions when original fonts are unavailable.
"""

# Common font family mappings
FONT_SUBSTITUTIONS = {
    # Serif fonts
    'Times New Roman': 'Times-Roman',
    'Times': 'Times-Roman',
    'Georgia': 'Times-Roman',
    'Garamond': 'Times-Roman',
    
    # Sans-serif fonts
    'Arial': 'Helvetica',
    'Helvetica Neue': 'Helvetica',
    'Calibri': 'Helvetica',
    'Verdana': 'Helvetica',
    'Tahoma': 'Helvetica',
    'Segoe UI': 'Helvetica',
    
    # Monospace fonts
    'Courier New': 'Courier',
    'Consolas': 'Courier',
    'Monaco': 'Courier',
}

def get_font_substitute(font_name):
    """
    Get the best available substitute for a given font name.
    
    Args:
        font_name (str): Original font name
        
    Returns:
        tuple: (substitute_font_name, was_substituted)
    """
    # Clean font name
    font_name = font_name.strip()
    
    # Check if we have a direct mapping
    if font_name in FONT_SUBSTITUTIONS:
        return FONT_SUBSTITUTIONS[font_name], True
    
    # Check for partial matches
    font_lower = font_name.lower()
    
    if 'times' in font_lower or 'serif' in font_lower:
        return 'Times-Roman', True
    elif 'arial' in font_lower or 'helvetica' in font_lower or 'sans' in font_lower:
        return 'Helvetica', True
    elif 'courier' in font_lower or 'mono' in font_lower:
        return 'Courier', True
    
    # Default to Helvetica if no match found
    return 'Helvetica', True

def get_reportlab_font(font_name, bold=False, italic=False):
    """
    Get the appropriate ReportLab font name based on style.
    
    Args:
        font_name (str): Base font name
        bold (bool): Whether font should be bold
        italic (bool): Whether font should be italic
        
    Returns:
        str: ReportLab font name
    """
    base_font, _ = get_font_substitute(font_name)
    
    # Handle font styles
    if base_font == 'Helvetica':
        if bold and italic:
            return 'Helvetica-BoldOblique'
        elif bold:
            return 'Helvetica-Bold'
        elif italic:
            return 'Helvetica-Oblique'
        return 'Helvetica'
    
    elif base_font == 'Times-Roman':
        if bold and italic:
            return 'Times-BoldItalic'
        elif bold:
            return 'Times-Bold'
        elif italic:
            return 'Times-Italic'
        return 'Times-Roman'
    
    elif base_font == 'Courier':
        if bold and italic:
            return 'Courier-BoldOblique'
        elif bold:
            return 'Courier-Bold'
        elif italic:
            return 'Courier-Oblique'
        return 'Courier'
    
    return base_font
