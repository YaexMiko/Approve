from os import environ
from typing import Dict, Any, List

# Backward compatible exports
API_ID = int(environ.get("API_ID", "28614709"))
API_HASH = environ.get("API_HASH", "f36fd2ee6e3d3a17c4d244ff6dc1bac8")
BOT_TOKEN = environ.get("BOT_TOKEN", "7558079740:AAH7ntHUduGi9kq-55fTUl_eUtmUIqrqevs")
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1004753466500"))
ADMINS = int(environ.get("ADMINS", "7207533746"))
DB_URI = environ.get("DB_URI", "mongodb+srv://ZeroTwo:aloksingh@zerotwo.3q3ij.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = environ.get("DB_NAME", "vjjoinrequetbot")
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False))

class DynamicConfig:
    _instance = None
    config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DynamicConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Initialize with environment variables
        self.config = {
            "API_ID": API_ID,
            "API_HASH": API_HASH,
            "BOT_TOKEN": BOT_TOKEN,
            "LOG_CHANNEL": LOG_CHANNEL,
            "ADMINS": [ADMINS] if isinstance(ADMINS, int) else [int(x) for x in ADMINS.split(",")],
            "DB_URI": DB_URI,
            "DB_NAME": DB_NAME,
            "NEW_REQ_MODE": NEW_REQ_MODE,
            "WELCOME_MESSAGE": "Hello {user_mention}!\nWelcome to {chat_title}\n\n__Powered by @VJ_Botz__",
            "BROADCAST_DELAY": 1,
        }

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        if isinstance(value, str):
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
        self.config[key] = value
        return True

    def get_all(self):
        return self.config.copy()

# Global configuration instance
config = DynamicConfig()
