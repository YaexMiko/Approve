from pyrogram import Client
from config import config  # Changed to import the config instance

class Bot(Client):
    def __init__(self):
        super().__init__(
            "vj join request bot",
            api_id=config.get("API_ID"),  # Access through config instance
            api_hash=config.get("API_HASH"),  # Access through config instance
            bot_token=config.get("BOT_TOKEN"),  # Access through config instance
            plugins=dict(root="plugins"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = '@' + me.username
        print('Bot Started Powered By @VJ_Botz')

    async def stop(self, *args):
        await super().stop()
        print('Bot Stopped Bye')

if __name__ == "__main__":
    Bot().run()
