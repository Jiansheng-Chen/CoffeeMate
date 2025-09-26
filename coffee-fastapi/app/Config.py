import json
from pathlib import Path
class Config:
    def __init__(self, config_filename: str = "config.json"):
        self.path = Path(__file__).parent / config_filename
        if not self.path.exists():
            raise FileNotFoundError(f"Config file not found : {self.path}")
        else:
            with open(self.path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
    
    def get(self, key_path :str, default = None):
        keys = key_path.split('.')
        #print(f"key_path:{key_path}")
        #print(f"keys: {keys}")
        value = self._data
        #print(f"_data: {self._data}")
        try:
            for key in keys:
                value = value[key]
                #print(f"value: {value}")
            return value
        except Exception as e:
            print(f"config key error:{e}")

config=Config()
