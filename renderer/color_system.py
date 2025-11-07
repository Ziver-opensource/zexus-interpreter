# renderer/color_system.py
"""
Advanced color system with mixing, gradients, and modern design capabilities
"""

import math
from typing import Tuple, List, Dict, Any

class RGBColor:
    """RGB color with mixing capabilities"""
    
    def __init__(self, r: int, g: int, b: int):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
    
    def mix(self, other: 'RGBColor', ratio: float = 0.5) -> 'RGBColor':
        """Mix two colors with given ratio (0.0 = self, 1.0 = other)"""
        ratio = max(0.0, min(1.0, ratio))
        inv_ratio = 1.0 - ratio
        
        r = int(self.r * inv_ratio + other.r * ratio)
        g = int(self.g * inv_ratio + other.g * ratio)
        b = int(self.b * inv_ratio + other.b * ratio)
        
        return RGBColor(r, g, b)
    
    def lighten(self, amount: float = 0.1) -> 'RGBColor':
        """Lighten color by amount (0.0 to 1.0)"""
        return self.mix(RGBColor(255, 255, 255), amount)
    
    def darken(self, amount: float = 0.1) -> 'RGBColor':
        """Darken color by amount (0.0 to 1.0)"""
        return self.mix(RGBColor(0, 0, 0), amount)
    
    def saturate(self, amount: float = 0.1) -> 'RGBColor':
        """Increase saturation"""
        h, s, v = self.to_hsv()
        s = min(1.0, s + amount)
        return self.from_hsv(h, s, v)
    
    def desaturate(self, amount: float = 0.1) -> 'RGBColor':
        """Decrease saturation"""
        h, s, v = self.to_hsv()
        s = max(0.0, s - amount)
        return self.from_hsv(h, s, v)
    
    def to_hsv(self) -> Tuple[float, float, float]:
        """Convert RGB to HSV"""
        r, g, b = self.r / 255.0, self.g / 255.0, self.b / 255.0
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        delta = cmax - cmin
        
        # Hue calculation
        if delta == 0:
            h = 0
        elif cmax == r:
            h = 60 * (((g - b) / delta) % 6)
        elif cmax == g:
            h = 60 * (((b - r) / delta) + 2)
        else:
            h = 60 * (((r - g) / delta) + 4)
        
        # Saturation calculation
        s = 0 if cmax == 0 else delta / cmax
        
        # Value calculation
        v = cmax
        
        return h, s, v
    
    def from_hsv(self, h: float, s: float, v: float) -> 'RGBColor':
        """Convert HSV to RGB"""
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        
        return RGBColor(r, g, b)
    
    def to_ansi(self, background: bool = False) -> str:
        """Convert to ANSI escape code"""
        if background:
            return f'\033[48;2;{self.r};{self.g};{self.b}m'
        else:
            return f'\033[38;2;{self.r};{self.g};{self.b}m'
    
    def __repr__(self) -> str:
        return f"RGBColor({self.r}, {self.g}, {self.b})"

class ColorPalette:
    """Modern color palette with mixing and themes"""
    
    # Base colors
    BASE_COLORS = {
        # Primary colors
        'red': RGBColor(255, 59, 48),
        'orange': RGBColor(255, 149, 0),
        'yellow': RGBColor(255, 204, 0),
        'green': RGBColor(52, 199, 89),
        'mint': RGBColor(0, 199, 190),
        'teal': RGBColor(48, 176, 199),
        'cyan': RGBColor(50, 173, 230),
        'blue': RGBColor(0, 122, 255),
        'indigo': RGBColor(88, 86, 214),
        'purple': RGBColor(175, 82, 222),
        'pink': RGBColor(255, 45, 85),
        'brown': RGBColor(162, 132, 94),
        
        # Neutrals
        'white': RGBColor(255, 255, 255),
        'gray': RGBColor(142, 142, 147),
        'gray2': RGBColor(174, 174, 178),
        'gray3': RGBColor(199, 199, 204),
        'gray4': RGBColor(209, 209, 214),
        'gray5': RGBColor(229, 229, 234),
        'gray6': RGBColor(242, 242, 247),
        'black': RGBColor(0, 0, 0),
    }
    
    def __init__(self):
        self.custom_colors = {}
        self.gradients = {}
        self._generate_derived_colors()
    
    def _generate_derived_colors(self):
        """Generate derived colors and gradients"""
        # Create lighter/darker variants
        for name, color in list(self.BASE_COLORS.items()):
            self.BASE_COLORS[f"light_{name}"] = color.lighten(0.3)
            self.BASE_COLORS[f"dark_{name}"] = color.darken(0.3)
            self.BASE_COLORS[f"pastel_{name}"] = color.desaturate(0.4).lighten(0.2)
    
    def mix(self, color1: str, color2: str, ratio: float = 0.5, name: str = None) -> RGBColor:
        """Mix two named colors and optionally register the result"""
        if color1 not in self.BASE_COLORS:
            raise ValueError(f"Unknown color: {color1}")
        if color2 not in self.BASE_COLORS:
            raise ValueError(f"Unknown color: {color2}")
        
        mixed = self.BASE_COLORS[color1].mix(self.BASE_COLORS[color2], ratio)
        
        if name:
            self.custom_colors[name] = mixed
        
        return mixed
    
    def create_gradient(self, start_color: str, end_color: str, steps: int, name: str) -> List[RGBColor]:
        """Create a color gradient"""
        if start_color not in self.BASE_COLORS:
            raise ValueError(f"Unknown color: {start_color}")
        if end_color not in self.BASE_COLORS:
            raise ValueError(f"Unknown color: {end_color}")
        
        start = self.BASE_COLORS[start_color]
        end = self.BASE_COLORS[end_color]
        
        gradient = []
        for i in range(steps):
            ratio = i / (steps - 1) if steps > 1 else 0
            gradient.append(start.mix(end, ratio))
        
        self.gradients[name] = gradient
        return gradient
    
    def get_color(self, name: str) -> RGBColor:
        """Get color by name (supports base, custom, and mixed colors)"""
        if name in self.BASE_COLORS:
            return self.BASE_COLORS[name]
        elif name in self.custom_colors:
            return self.custom_colors[name]
        else:
            # Try to parse mixed color syntax: "blue+red:0.3" or "blue|red:0.3"
            if '+' in name or '|' in name:
                separator = '+' if '+' in name else '|'
                parts = name.split(separator)
                if len(parts) == 2:
                    color2_part = parts[1]
                    if ':' in color2_part:
                        color2, ratio_str = color2_part.split(':')
                        try:
                            ratio = float(ratio_str)
                            return self.mix(parts[0], color2, ratio)
                        except ValueError:
                            pass
                    else:
                        return self.mix(parts[0], color2_part)
        
        raise ValueError(f"Unknown color: {name}")
    
    def define_color(self, name: str, r: int, g: int, b: int):
        """Define a custom color"""
        self.custom_colors[name] = RGBColor(r, g, b)
    
    def list_colors(self) -> List[str]:
        """List all available colors"""
        return list(self.BASE_COLORS.keys()) + list(self.custom_colors.keys())

class Theme:
    """Complete UI theme with coordinated colors"""
    
    def __init__(self, name: str, palette: ColorPalette):
        self.name = name
        self.palette = palette
        self.colors = {}
    
    def set_primary(self, color: str):
        """Set primary color and generate theme variants"""
        primary = self.palette.get_color(color)
        self.colors.update({
            'primary': primary,
            'primary_light': primary.lighten(0.2),
            'primary_dark': primary.darken(0.2),
            'primary_pastel': primary.desaturate(0.3).lighten(0.3),
        })
    
    def set_accent(self, color: str):
        """Set accent color"""
        self.colors['accent'] = self.palette.get_color(color)
    
    def set_background(self, color: str):
        """Set background color"""
        self.colors['background'] = self.palette.get_color(color)
        self.colors['surface'] = self.palette.get_color(color).lighten(0.1)
    
    def set_text(self, color: str):
        """Set text color"""
        self.colors['text'] = self.palette.get_color(color)
        self.colors['text_secondary'] = self.palette.get_color(color).desaturate(0.3)
    
    def get(self, color_name: str) -> RGBColor:
        """Get theme color"""
        return self.colors.get(color_name, self.palette.BASE_COLORS['black'])