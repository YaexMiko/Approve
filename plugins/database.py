import motor.motor_asyncio
from config import DB_NAME, DB_URI
from datetime import datetime

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
            join_date = datetime.now()
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('session')

    # New methods for group tracking
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

db = Database(DB_URI, DB_NAME)
