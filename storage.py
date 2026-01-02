import json
from pathlib import Path


class DataStorage:
    def __init__(self):
        self.accounts = {}
        self.source_channels = []
        self.target_channels = []
        self.channel_links = []
        self.active_forwarders = {}
        self.data_file = Path("data.json")
        self.load_data()
    
    def load_data(self):
        if self.data_file.exists():
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.accounts = data.get("accounts", {})
                self.source_channels = data.get("source_channels", [])
                self.target_channels = data.get("target_channels", [])
                self.channel_links = data.get("channel_links", [])
    
    def save_data(self):
        data = {
            "accounts": {k: {
                "api_id": v["api_id"],
                "api_hash": v["api_hash"],
                "phone": v["phone"]
            } for k, v in self.accounts.items()},
            "source_channels": self.source_channels,
            "target_channels": self.target_channels,
            "channel_links": self.channel_links
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_account_info(self, session_name):
        return self.accounts.get(session_name, {})


storage = DataStorage()