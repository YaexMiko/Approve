from os import environ
from typing import Dict, Any, List

class DynamicConfig:
    _instance = None
    config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DynamicConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Static config (from environment variables)
        self.config = {
            "API_ID": int(environ.get("API_ID", "28614709")),
            "API_HASH": environ.get("API_HASH", "f36fd2ee6e3d3a17c4d244ff6dc1bac8"),
            "BOT_TOKEN": environ.get("BOT_TOKEN", "7558079740:AAH7ntHUduGi9kq-55fTUl_eUtmUIqrqevs"),
            "LOG_CHANNEL": int(environ.get("LOG_CHANNEL", "-1004753466500")),
            "ADMINS": [int(admin_id) for admin_id in environ.get("ADMINS", "7207533746").split(",")],
            "DB_URI": environ.get("DB_URI", "mongodb+srv://ZeroTwo:aloksingh@zerotwo.3q3ij.mongodb.net/?retryWrites=true&w=majority"),
            "DB_NAME": environ.get("DB_NAME", "vjjoinrequetbot"),
            "NEW_REQ_MODE": environ.get('NEW_REQ_MODE', 'False').lower() == 'true',
            "WELCOME_MESSAGE": environ.get("WELCOME_MESSAGE", "Hello {user_mention}!\nWelcome to {chat_title}\n\n__Powered by @VJ_Botz__"),
            "BROADCAST_DELAY": int(environ.get("BROADCAST_DELAY", "1")),
        }

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        # Special handling for boolean values
        if isinstance(value, str):
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
        self.config[key] = value
        return True

    def get_all(self):
        return self.config.copy()

# Global configuration instance
config = DynamicConfig()
