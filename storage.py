import json
from pathlib import Path
from logger import logger


class Storage:
    def __init__(self, filepath="data.json"):
        self.filepath = Path(filepath)
        self.accounts = {}
        self.source_channels = []
        self.target_channels = []
        self.links = []
        self.active_forwarders = {}
        self.filters = []
        self.interval = 0
        self._seen_list = []
        self._seen_set = set()
        self._load()

    def _load(self):
        if not self.filepath.exists():
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.accounts = data.get("accounts", {})
                self.source_channels = data.get("source_channels", [])
                self.target_channels = data.get("target_channels", [])
                self.links = data.get("links", [])
                self.filters = data.get("filters", [])
                self.interval = data.get("interval", 0)
                self._seen_list = data.get("seen_messages", [])
                self._seen_set = set(self._seen_list)
            logger.info("Дані завантажено")
        except Exception as e:
            logger.error(f"Помилка завантаження: {e}")

    def _save(self):
        try:
            data = {
                "accounts": {k: {
                    "api_id": v["api_id"],
                    "api_hash": v["api_hash"],
                    "phone": v["phone"]
                } for k, v in self.accounts.items()},
                "source_channels": self.source_channels,
                "target_channels": self.target_channels,
                "links": self.links,
                "filters": self.filters,
                "interval": self.interval,
                "seen_messages": self._seen_list
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Дані збережено")
        except Exception as e:
            logger.error(f"Помилка збереження: {e}")
    
    def add_account(self, name, api_id, api_hash, phone):
        self.accounts[name] = {
            "api_id": api_id,
            "api_hash": api_hash,
            "phone": phone
        }
        self._save()
        logger.info(f"Додано акаунт: {name}")
    
    def remove_account(self, name):
        if name in self.accounts:
            del self.accounts[name]
            self._save()
            logger.info(f"Видалено акаунт: {name}")
    
    def add_source(self, channel):
        if channel not in self.source_channels:
            self.source_channels.append(channel)
            self._save()
            logger.info(f"Додано джерело: {channel}")
    
    def add_target(self, channel):
        if channel not in self.target_channels:
            self.target_channels.append(channel)
            self._save()
            logger.info(f"Додано отримувач: {channel}")
    
    def remove_source(self, channel):
        if channel in self.source_channels:
            self.source_channels.remove(channel)
            self.links = [l for l in self.links if l["source"] != channel]
            self._save()
            logger.info(f"Видалено джерело: {channel}")
    
    def remove_target(self, channel):
        if channel in self.target_channels:
            self.target_channels.remove(channel)
            self.links = [l for l in self.links if l["target"] != channel]
            self._save()
            logger.info(f"Видалено отримувач: {channel}")
    
    def add_link(self, source, target):
        link = {"source": source, "target": target}
        if link not in self.links:
            self.links.append(link)
            self._save()
            logger.info(f"Додано зв'язок: {source} → {target}")
    
    def remove_link(self, index):
        if 0 <= index < len(self.links):
            link = self.links.pop(index)
            self._save()
            logger.info(f"Видалено зв'язок: {link['source']} → {link['target']}")

    def add_filter(self, keyword):
        kw = keyword.lower()
        if kw not in self.filters:
            self.filters.append(kw)
            self._save()
            logger.info(f"Додано фільтр: {kw}")

    def remove_filter(self, index):
        if 0 <= index < len(self.filters):
            kw = self.filters.pop(index)
            self._save()
            logger.info(f"Видалено фільтр: {kw}")
            return kw
        return None

    def set_interval(self, seconds):
        self.interval = int(seconds)
        self._save()
        logger.info(f"Інтервал: {seconds} сек")

    def is_duplicate(self, key):
        return key in self._seen_set

    def mark_seen(self, key):
        if key in self._seen_set:
            return
        self._seen_set.add(key)
        self._seen_list.append(key)
        if len(self._seen_list) > 10000:
            removed = self._seen_list[:5000]
            self._seen_list = self._seen_list[5000:]
            for k in removed:
                self._seen_set.discard(k)
        self._save()


storage = Storage()