from PyQt6.QtGui import QGuiApplication

class UIScaler:
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080

    @staticmethod
    def get_scale_factor():
        screen = QGuiApplication.primaryScreen().geometry()
        width_ratio = screen.width() / UIScaler.BASE_WIDTH
        height_ratio = screen.height() / UIScaler.BASE_HEIGHT
        return min(width_ratio, height_ratio)

    @staticmethod
    def scale(value):
        """Масштабирует числовое значение (пиксели)"""
        return int(value * UIScaler.get_scale_factor())

def apply_adaptive_geometry(widget, w, h, x=None, y=None):
    scaler = UIScaler()
    new_w = scaler.scale(w)
    new_h = scaler.scale(h)

    widget.setFixedSize(new_w, new_h)

    if x is not None and y is not None:
        widget.move(scaler.scale(x), scaler.scale(y))

    current_style = widget.styleSheet()
    import re
    def replace_px(match):
        px_value = int(match.group(1))
        return f"{scaler.scale(px_value)}px"

    new_style = re.sub(r'(\d+)px', replace_px, current_style)
    widget.setStyleSheet(new_style)