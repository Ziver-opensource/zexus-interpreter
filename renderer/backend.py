"""
Renderer backend facade.

Provides a small, stable API used by evaluator builtins and (later) by runtime VM.
This wraps the richer renderer/color_system and exposes simple functions that
operate on an in-memory registry.
"""
from typing import Dict, Any, List, Optional
try:
	from .color_system import ColorPalette, Theme
except Exception:
	ColorPalette = None
	Theme = None

_registry: Dict[str, Any] = {
	'screens': {},     # name -> {'properties': dict, 'components': [] , 'theme': None}
	'components': {},  # name -> properties dict
	'themes': {},      # name -> properties dict
	'canvases': {},    # id -> {'width','height','draw_ops'}
	'current_theme': None
}

_palette = ColorPalette() if ColorPalette else None

def mix(color_a: str, color_b: str, ratio: float = 0.5) -> str:
	"""Mix two colors and return a stable string description or color object repr."""
	if _palette:
		try:
			col = _palette.mix(color_a, color_b, ratio)
			return str(col)
		except Exception:
			return f"mix({color_a},{color_b},{ratio})"
	# fallback
	return f"mix({color_a},{color_b},{ratio})"

def define_screen(name: str, properties: Optional[Dict[str, Any]] = None) -> None:
	_registry['screens'].setdefault(name, {'properties': properties or {}, 'components': [], 'theme': None})

def define_component(name: str, properties: Optional[Dict[str, Any]] = None) -> None:
	_registry['components'][name] = properties or {}

def add_to_screen(screen_name: str, component_name: str) -> None:
	if screen_name not in _registry['screens']:
		raise KeyError(f"Screen '{screen_name}' not found")
	_registry['screens'][screen_name]['components'].append(component_name)

def render_screen(name: str) -> str:
	screen = _registry['screens'].get(name)
	if not screen:
		return f"<missing screen: {name}>"
	props = screen.get('properties', {})
	comps = screen.get('components', [])
	theme = screen.get('theme') or _registry.get('current_theme')
	# Simple textual rendering — real backend can return structured render tree
	return f"Screen:{name} props={props} components={comps} theme={theme}"

def set_theme(target_or_theme: str, theme_name: Optional[str] = None) -> None:
	# set_theme(theme) or set_theme(target, theme)
	if theme_name is None:
		_registry['current_theme'] = target_or_theme
	else:
		target = target_or_theme
		if target in _registry['screens']:
			_registry['screens'][target]['theme'] = theme_name
		else:
			_registry['themes'].setdefault(theme_name, {})

def create_canvas(width: int, height: int) -> str:
	cid = f"canvas_{len(_registry['canvases'])+1}"
	_registry['canvases'][cid] = {'width': width, 'height': height, 'draw_ops': []}
	return cid

def draw_line(canvas_id: str, x1: int, y1: int, x2: int, y2: int) -> None:
	canvas = _registry['canvases'].get(canvas_id)
	if canvas is None:
		raise KeyError(f"Canvas {canvas_id} not found")
	canvas['draw_ops'].append(('line', (x1, y1, x2, y2)))

def draw_text(canvas_id: str, x: int, y: int, text: str) -> None:
	canvas = _registry['canvases'].get(canvas_id)
	if canvas is None:
		raise KeyError(f"Canvas {canvas_id} not found")
	canvas['draw_ops'].append(('text', (x, y, text)))

def inspect_registry() -> Dict[str, Any]:
	"""Return a shallow copy of registry for debugging."""
	return {
		'screens': dict(_registry['screens']),
		'components': dict(_registry['components']),
		'themes': dict(_registry['themes']),
		'canvases': dict(_registry['canvases']),
		'current_theme': _registry.get('current_theme')
	}
