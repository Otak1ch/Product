import json
import os
import sys

def get_save_path(filename="config.json"):

    if hasattr(sys, '_MEIPASS'):
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, filename)
    return os.path.join(os.path.abspath("."), filename)


class DataManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self._ensure_path()

    def _ensure_path(self):
        dir_name = os.path.dirname(self.config_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

    def load_all_data(self):
        if not os.path.exists(self.config_path):
            default_data = {
                "main_window": {"x": 100, "y": 100},
                "opened_widgets": [],
                "persistent_data": {},
                "last_positions": {},
                "last_geometries": {}
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)

        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_all_data(self, data):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_widget_content(self, widget_type):
        return self.load_all_data().get("persistent_data", {}).get(widget_type)

    def get_last_position(self, widget_type):
        data = self.load_all_data()
        pos_data = data.get("last_positions", {}).get(widget_type)
        if pos_data:
            return pos_data.get("x"), pos_data.get("y")
        return None, None

    def update_last_position(self, widget_type, x, y):
        data = self.load_all_data()
        if "last_positions" not in data:
            data["last_positions"] = {}
        data["last_positions"][widget_type] = {"x": x, "y": y}
        self.save_all_data(data)

    def get_last_geometry(self, widget_type):
        data = self.load_all_data()
        geo = data.get("last_geometries", {}).get(widget_type)
        if geo:
            return geo.get("x"), geo.get("y"), geo.get("w"), geo.get("h")
        return None, None, None, None

    def update_last_geometry(self, widget_type, x, y, w, h):
        data = self.load_all_data()
        if "last_geometries" not in data:
            data["last_geometries"] = {}
        data["last_geometries"][widget_type] = {"x": x, "y": y, "w": w, "h": h}
        self.save_all_data(data)