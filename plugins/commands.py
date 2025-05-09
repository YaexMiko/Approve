import asyncio 
from pyrogram import Client, filters, enums
from config import config
from plugins.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import matplotlib.pyplot as plt
import os

LOG_TEXT = """<b>#NewUser
    
ID - <code>{}</code>

Nᴀᴍᴇ - {}</b>
"""

async def generate_stats_chart(stats):
    plt.figure(figsize=(10, 6))
    categories = ['Users', 'Verified', 'Active', 'Groups']
    values = [
        stats['total_users'],
        stats['verified_users'],
        stats['active_today'],
        stats['total_groups']
    ]
    bars = plt.bar(categories, values, color=['blue', 'green', 'orange', 'red'])
    plt.title('Bot Statistics Overview', fontsize=16)
    plt.ylabel('Count', fontsize=12)
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig('stats_chart.png', dpi=300)
    plt.close()

@Client.on_message(filters.command('start'))
async def start_message(c, m):
    try:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id, m.from_user.first_name)
            await c.send_message(
                config.get("LOG_CHANNEL"), 
                LOG_TEXT.format(m.from_user.id, m.from_user.mention)
            )
        
        help_text = "<b>Hello {mention} 👋\n\nI Am Join Request Acceptor Bot.</b>\n\n<b>Available Commands:</b>\n/accept - Accept pending join requests"
        
        if m.from_user.id in config.get("ADMINS", []):
            help_text += "\n\n<b>Admin Commands:</b>"
            help_text += "\n/verify - Verify a user (reply to user)"
            help_text += "\n/stats - Show advanced statistics"
            help_text += "\n/config - View bot configuration"
            help_text += "\n/setconfig - Modify configuration"
        
        await m.reply_photo(
            "https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
            caption=help_text.format(mention=m.from_user.mention),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('💝 YouTube Channel', url='https://youtube.com/@Tech_VJ')],
                    [
                        InlineKeyboardButton("❣️ Developer", url='https://t.me/Kingvj01'),
                        InlineKeyboardButton("🤖 Updates", url='https://t.me/VJ_Botz')
                    ]
                ]
            )
        )
    except Exception as e:
        print(f"Error in start_message: {e}")
        await m.reply_text("❌ An error occurred. Please try again later.")

@Client.on_message(filters.command('verify') & filters.user(config.get("ADMINS")))
async def verify_user(client, message):
    try:
        if not message.reply_to_message:
            return await message.reply("❌ Reply to a user's message to verify them")
        
        user_id = message.reply_to_message.from_user.id
        await db.verify_user(user_id)
        
        try:
            await client.send_message(
                user_id,
                "🎉 Your account has been verified by admin!"
            )
        except:
            pass
            
        await message.reply_text(f"✅ User {user_id} verified successfully")
        await client.send_message(
            config.get("LOG_CHANNEL"),
            f"#USER_VERIFIED\n\nAdmin: {message.from_user.mention}\nUser: {message.reply_to_message.from_user.mention}\nID: {user_id}"
        )
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command('stats') & filters.user(config.get("ADMINS")))
async def show_advanced_stats(client, message):
    try:
        stats = {
            'total_users': await db.total_users_count(),
            'verified_users': await db.get_verified_users_count(),
            'active_today': await db.active_users_count(1),
            'active_week': await db.active_users_count(7),
            'total_groups': await db.total_groups_count(),
            'join_requests': await db.total_requests_count(),
            'storage_size': await db.get_storage_size()
        }
        
        stats_text = f"""
📊 <b>Advanced Statistics Dashboard</b> 📊
┌──────────────────────┬────────────────┐
│ <b>Total Users</b>       │ {stats['total_users']:>14} │
│ <b>Verified Users</b>    │ {stats['verified_users']:>14} │
│ <b>Active Today</b>      │ {stats['active_today']:>14} │
│ <b>Active This Week</b>  │ {stats['active_week']:>14} │
├──────────────────────┼────────────────┤
│ <b>Total Groups</b>      │ {stats['total_groups']:>14} │
│ <b>Total Join Requests</b> │ {stats['join_requests']:>14} │
│ <b>Database Size</b>     │ {stats['storage_size']:>14} │
└──────────────────────┴────────────────┘

<b>Last Updated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await message.reply_text(stats_text, parse_mode=enums.ParseMode.HTML)
        
        try:
            await generate_stats_chart(stats)
            await message.reply_photo("stats_chart.png")
            os.remove("stats_chart.png")
        except Exception as e:
            print(f"Chart generation error: {e}")
            
    except Exception as e:
        await message.reply_text(f"❌ Error generating stats: {str(e)}")

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    try:
        show = await message.reply("**Please Wait.....**")
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            return await show.edit("**For Accept Pending Request You Have To /login First.**")
        
        try:
            acc = Client("joinrequest", session_string=user_data, api_hash=config.get("API_HASH"), api_id=config.get("API_ID"))
            await acc.connect()
        except Exception as e:
            print(f"Session connection error: {e}")
            return await show.edit("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
        
        show = await show.edit("**Now Forward A Message From Your Channel Or Group With Forward Tag\n\nMake Sure Your Logged In Account Is Admin In That Channel Or Group With Full Rights.**")
        
        try:
            vj = await client.listen(message.chat.id, timeout=300)
            if not (vj.forward_from_chat and not vj.forward_from_chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]):
                return await message.reply("**Message Not Forwarded From Channel Or Group.**")
            
            chat_id = vj.forward_from_chat.id
            try:
                info = await acc.get_chat(chat_id)
            except Exception as e:
                print(f"Chat access error: {e}")
                return await show.edit("**Error - Make Sure Your Logged In Account Is Admin In This Channel Or Group With Rights.**")
            
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
        except asyncio.TimeoutError:
            await show.edit("**Timed out waiting for forwarded message.**")
    except Exception as e:
        print(f"Error in accept command: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

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
        print(f"Error in show_stats: {e}")
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
        print(f"Error in show_config: {e}")
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
            config.get("LOG_CHANNEL"),
            f"#CONFIG_CHANGE\n\n"
            f"<b>Admin:</b> {message.from_user.mention}\n"
            f"<b>Key:</b> {key}\n"
            f"<b>Old Value:</b> <code>{old_value}</code>\n"
            f"<b>New Value:</b> <code>{value}</code>"
        )
    except Exception as e:
        print(f"Error in set_config: {e}")
        await message.reply_text(f"Error updating config: {str(e)}")

@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    try:
        # Check if auto-approval is enabled
        if not config.get("NEW_REQ_MODE", False):
            return
            
        # Validate the chat/channel first
        try:
            chat = await client.get_chat(m.chat.id)
            if not chat:
                print(f"Chat not found: {m.chat.id}")
                return
        except Exception as chat_error:
            print(f"Chat validation failed for {m.chat.id}: {chat_error}")
            # Notify admin about the channel error
            for admin_id in config.get("ADMINS", []):
                try:
                    await client.send_message(
                        admin_id,
                        f"⚠️ Channel Error:\n\nFailed to validate chat {m.chat.id}\nError: {chat_error}"
                    )
                except:
                    pass
            return

        # User and group database handling
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id, m.from_user.first_name)
            await client.send_message(
                config.get("LOG_CHANNEL"), 
                LOG_TEXT.format(m.from_user.id, m.from_user.mention)
            )
        
        if not await db.is_group_exist(m.chat.id):
            await db.add_group(m.chat.id, m.chat.title)
            
        # Approve the join request
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        
        # Send welcome message if possible
        welcome_message = config.get(
            "WELCOME_MESSAGE", 
            "**Hello {user_mention}!\nWelcome To {chat_title}\n\n__Powered By : @VJ_Botz __**"
        )
        try:
            await client.send_message(
                m.from_user.id,
                welcome_message.format(
                    user_mention=m.from_user.mention,
                    chat_title=m.chat.title
                )
            )
        except Exception as welcome_error:
            print(f"Welcome message failed: {welcome_error}")

    except Exception as e:
        error_msg = f"⚠️ Critical Error in approve_new:\n\n{str(e)}"
        print(error_msg)
        # Notify all admins about critical failure
        for admin_id in config.get("ADMINS", []):
            try:
                await client.send_message(admin_id, error_msg)
            except:
                pass
