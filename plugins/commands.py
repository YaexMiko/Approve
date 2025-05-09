import asyncio 
from pyrogram import Client, filters, enums
from config import config, LOG_CHANNEL, API_ID, API_HASH
from plugins.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

LOG_TEXT = """<b>#NewUser
    
ID - <code>{}</code>

Nᴀᴍᴇ - {}</b>
"""

@Client.on_message(filters.command('start'))
async def start_message(c,m):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
    await m.reply_photo(f"https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
        caption=f"<b>Hello {m.from_user.mention} 👋\n\nI Am Join Request Acceptor Bot. I Can Accept All Old Pending Join Request.\n\nFor All Pending Join Request Use - /accept</b>",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')
            ],[
                InlineKeyboardButton("❣️ ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://t.me/Kingvj01'),
                InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ", url='https://t.me/VJ_Botz')
            ]]
        )
    )

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please Wait.....**")
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**For Accepte Pending Request You Have To /login First.**")
        return
    try:
        acc = Client("joinrequest", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except:
        return await show.edit("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
    show = await show.edit("**Now Forward A Message From Your Channel Or Group With Forward Tag\n\nMake Sure Your Logged In Account Is Admin In That Channel Or Group With Full Rights.**")
    vj = await client.listen(message.chat.id)
    if vj.forward_from_chat and not vj.forward_from_chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = vj.forward_from_chat.id
        try:
            info = await acc.get_chat(chat_id)
        except:
            await show.edit("**Error - Make Sure Your Logged In Account Is Admin In This Channel Or Group With Rights.**")
    else:
        return await message.reply("**Message Not Forwarded From Channel Or Group.**")
    await vj.delete()
    msg = await show.edit("**Accepting all join requests... Please wait until it's completed.**")
    try:
        while True:
            await acc.approve_all_chat_join_requests(chat_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
        await msg.edit("**Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"**An error occurred:** {str(e)}")

@Client.on_message(filters.command('users') & filters.private)
async def show_stats(client, message):
    try:
        total_users = await db.total_users_count()
        total_groups = await db.total_groups_count()
        total = total_users + total_groups
        
        stats_text = f"""
🍀 <b>Chats Stats</b> 🍀
🙋‍♂️ <b>Users:</b> {total_users}
👥 <b>Groups:</b> {total_groups}
🚧 <b>Total:</b> {total}
"""
        await message.reply_text(stats_text)
    except Exception as e:
        await message.reply_text(f"Error getting stats: {str(e)}")

@Client.on_message(filters.command('config') & filters.user(config.get("ADMINS")))
async def show_config(client, message):
    try:
        config_data = config.get_all()
        config_text = "⚙️ <b>Current Configuration:</b>\n\n"
        
        for key, value in config_data.items():
            if key in ["API_ID", "API_HASH", "BOT_TOKEN", "DB_URI"]:
                config_text += f"<b>{key}:</b> <code>*****</code>\n"
            else:
                config_text += f"<b>{key}:</b> <code>{value}</code>\n"
        
        await message.reply_text(config_text)
    except Exception as e:
        await message.reply_text(f"Error getting config: {str(e)}")

@Client.on_message(filters.command('setconfig') & filters.user(config.get("ADMINS")))
async def set_config(client, message):
    try:
        if len(message.command) < 3:
            return await message.reply_text("Usage: /setconfig <key> <value>")
        
        key = message.command[1].upper()
        value = " ".join(message.command[2:])
        
        # Prevent modification of sensitive/static configs
        if key in ["API_ID", "API_HASH", "BOT_TOKEN", "DB_URI", "DB_NAME"]:
            return await message.reply_text(f"Cannot modify {key} dynamically. Please update environment variables and restart the bot.")
        
        old_value = config.get(key)
        
        # Convert value to appropriate type
        if key in ["NEW_REQ_MODE"]:
            value = value.lower() in ["true", "yes", "1"]
        elif key in ["LOG_CHANNEL", "BROADCAST_DELAY"]:
            try:
                value = int(value)
            except ValueError:
                return await message.reply_text(f"Invalid integer value for {key}")
        elif key in ["ADMINS"]:
            try:
                value = [int(admin_id) for admin_id in value.split(",")]
            except ValueError:
                return await message.reply_text("Admin IDs must be comma-separated integers")
        
        config.set(key, value)
        
        await message.reply_text(
            f"✅ Config updated successfully\n\n"
            f"<b>{key}:</b>\n"
            f"Old: <code>{old_value}</code>\n"
            f"New: <code>{value}</code>"
        )
        
        # Log the change
        await client.send_message(
            LOG_CHANNEL,
            f"#CONFIG_CHANGE\n\n"
            f"<b>Admin:</b> {message.from_user.mention}\n"
            f"<b>Key:</b> {key}\n"
            f"<b>Old Value:</b> <code>{old_value}</code>\n"
            f"<b>New Value:</b> <code>{value}</code>"
        )
    except Exception as e:
        await message.reply_text(f"Error updating config: {str(e)}")

@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    if not config.get("NEW_REQ_MODE", False):
        return 
    try:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id, m.from_user.first_name)
            await client.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
        
        if not await db.is_group_exist(m.chat.id):
            await db.add_group(m.chat.id, m.chat.title)
            
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        
        welcome_message = config.get("WELCOME_MESSAGE", "Hello {user_mention}!\nWelcome to {chat_title}\n\n__Powered by @VJ_Botz__")
        formatted_message = welcome_message.format(
            user_mention=m.from_user.mention,
            chat_title=m.chat.title
        )
        
        try:
            await client.send_message(m.from_user.id, formatted_message)
        except:
            pass
    except Exception as e:
        print(str(e))
