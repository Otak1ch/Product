import json
import os

class DataManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self._ensure_path()

    def _ensure_path(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

    def load_all_data(self):
        if not os.path.exists(self.config_path):
            return {"main_window": {}, "opened_widgets": [], "persistent_data": {}}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "persistent_data" not in data: data["persistent_data"] = {}
                return data
        except Exception:
            return {"main_window": {}, "opened_widgets": [], "persistent_data": {}}

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