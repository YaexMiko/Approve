import motor.motor_asyncio
from config import DB_NAME, DB_URI
from datetime import datetime, timedelta

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.groups_col = self.db.groups

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            session = None,
            verified = False,
            accepted = False,
            accepted_chats = {},
            join_date = datetime.now(),
            last_active = datetime.now(),
            last_accepted = None
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def get_accepted_users(self):
        return self.col.find({'accepted': True})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one(
            {'id': int(id)},
            {'$set': {'session': session, 'last_active': datetime.now()}}
        )

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('session')

    async def verify_user(self, user_id: int):
        await self.col.update_one(
            {'id': user_id},
            {'$set': {'verified': True, 'verification_date': datetime.now()}},
            upsert=True
        )

    async def get_verified_users_count(self):
        return await self.col.count_documents({'verified': True})

    async def active_users_count(self, days: int = 1):
        cutoff_date = datetime.now() - timedelta(days=days)
        return await self.col.count_documents({
            '$or': [
                {'last_active': {'$gte': cutoff_date}},
                {'join_date': {'$gte': cutoff_date}}
            ]
        })

    async def total_requests_count(self):
        return await self.col.count_documents({'join_requests': {'$exists': True}})

    async def get_storage_size(self):
        stats = await self.db.command("dbstats")
        return f"{stats['dataSize']/1024/1024:.2f} MB"

    async def add_group(self, id, title):
        await self.groups_col.update_one(
            {'id': int(id)},
            {'$set': {'id': int(id), 'title': title, 'last_updated': datetime.now()}},
            upsert=True
        )

    async def is_group_exist(self, id):
        group = await self.groups_col.find_one({'id': int(id)})
        return bool(group)

    async def total_groups_count(self):
        return await self.groups_col.count_documents({})

    async def add_accepted_user(self, user_id: int, chat_id: int, chat_title: str):
        await self.col.update_one(
            {'id': user_id},
            {'$set': {
                'accepted': True,
                f'accepted_chats.{chat_id}': chat_title,
                'last_accepted': datetime.now()
            }},
            upsert=True
        )

db = Database(DB_URI, DB_NAME)
