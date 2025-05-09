from os import environ

API_ID = int(environ.get("API_ID", "28614709"))
API_HASH = environ.get("API_HASH", "f36fd2ee6e3d3a17c4d244ff6dc1bac8")
BOT_TOKEN = environ.get("BOT_TOKEN", "7558079740:AAH7ntHUduGi9kq-55fTUl_eUtmUIqrqevs")

# Make Bot Admin In Log Channel With Full Rights
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1004753466500"))
ADMINS = int(environ.get("ADMINS", "7207533746"))

# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = environ.get("DB_URI", "mongodb+srv://ZeroTwo:aloksingh@zerotwo.3q3ij.mongodb.net/?retryWrites=true&w=majority") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = environ.get("DB_NAME", "vjjoinrequetbot")

# If this is True Then Bot Accept New Join Request 
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False))
