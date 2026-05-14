import os
import json
import asyncio
import logging
import base64
import requests as _requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import main as fb

BOT_TOKEN = "8101206245:AAENv9gxlh_T2RnXoZuA9Ljztss2OY5vvVY"
OWNER_ID = 6162078955

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_data = {}
seen_users = set()
approved_users = set()
pending_users = {}
stop_flags = {}
created_accounts = []
user_credits = {}
creating_msg = {}
otp_sessions = {}  # {user_id: {"session": ses, "email": email, "name": name, "password": password}}

USERS_FILE = "users.json"

def load_users():
    global seen_users, approved_users, user_credits, pending_users, created_accounts
    try:
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
        seen_users = set(data.get("seen_users", []))
        approved_users = set(data.get("approved_users", []))
        user_credits = {int(k): v for k, v in data.get("user_credits", {}).items()}
        for uid_str, info in data.get("pending_users", {}).items():
            uid = int(uid_str)
            if uid not in pending_users:
                pending_users[uid] = info
        created_accounts = data.get("created_accounts", [])
    except Exception:
        pass

def save_users():
    try:
        with open(USERS_FILE, "w") as f:
            json.dump({
                "seen_users": list(seen_users),
                "approved_users": list(approved_users),
                "user_credits": {str(k): v for k, v in user_credits.items()},
                "pending_users": {str(k): v for k, v in pending_users.items()},
                "created_accounts": created_accounts,
            }, f)
    except Exception:
        pass

def make_start_kb(uid=0):
    is_owner = (uid == OWNER_ID)
    rows = [[InlineKeyboardButton(text="🚀 Start Creating Accounts", callback_data="menu:create")]]
    if is_owner:
        rows.append([
            InlineKeyboardButton(text="📋 My Accounts", callback_data="menu:myaccs"),
            InlineKeyboardButton(text="🌐 Bot Accounts", callback_data="menu:botaccs"),
        ])
    else:
        rows.append([InlineKeyboardButton(text="📋 My Accounts", callback_data="menu:myaccs")])
        rows.append([InlineKeyboardButton(text="💳 My Credits", callback_data="menu:mycredits")])
    if is_owner:
        rows.append([InlineKeyboardButton(text="⚙️ Owner Menu", callback_data="menu:admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def make_name_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇵🇭 Filipino Names", callback_data="name:1")],
        [InlineKeyboardButton(text="🔥 RPW Names", callback_data="name:2")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back:main")],
    ])

def make_gender_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Male", callback_data="gender:1")],
        [InlineKeyboardButton(text="👩 Female", callback_data="gender:2")],
        [InlineKeyboardButton(text="⚧ Mixed", callback_data="gender:3")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back:name")],
    ])

def make_acc_pass_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Set Custom Password", callback_data="accpass:custom")],
        [InlineKeyboardButton(text="🎲 Use Random Password", callback_data="accpass:random")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back:gender")],
    ])

def make_stop_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛑 Stop Creation", callback_data=f"stop:{uid}")]
    ])

def make_approval_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"access:ok:{user_id}"),
            InlineKeyboardButton(text="❌ Deny", callback_data=f"access:no:{user_id}"),
        ]
    ])

def make_credit_give_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="5", callback_data=f"credits:give:{user_id}:5"),
            InlineKeyboardButton(text="10", callback_data=f"credits:give:{user_id}:10"),
            InlineKeyboardButton(text="20", callback_data=f"credits:give:{user_id}:20"),
        ],
        [
            InlineKeyboardButton(text="50", callback_data=f"credits:give:{user_id}:50"),
            InlineKeyboardButton(text="100", callback_data=f"credits:give:{user_id}:100"),
            InlineKeyboardButton(text="✏️ Custom", callback_data=f"credits:give:{user_id}:custom"),
        ],
    ])

def make_admin_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Approved Users", callback_data="menu:users")],
        [InlineKeyboardButton(text="📋 Created Accounts", callback_data="menu:accounts")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="menu:back")],
    ])

def make_users_kb():
    rows = []
    users = [u for u in approved_users if u != OWNER_ID]
    if not users:
        rows.append([InlineKeyboardButton(text="— No approved users —", callback_data="noop")])
    else:
        for u in users:
            info = pending_users.get(u, {})
            label = info.get("name", str(u))
            credits = user_credits.get(u, 0)
            rows.append([InlineKeyboardButton(text=f"👤 {label} ({u}) 💳 {credits} credits", callback_data="noop")])
            rows.append([
                InlineKeyboardButton(text="➕ Add Credits", callback_data=f"credits:add:{u}"),
                InlineKeyboardButton(text="🚫 Revoke", callback_data=f"revoke:{u}"),
            ])
    rows.append([InlineKeyboardButton(text="🔙 Back", callback_data="menu:admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def make_accounts_kb():
    rows = []
    if created_accounts:
        rows.append([InlineKeyboardButton(text=f"🗑 Clear All ({len(created_accounts)} accs)", callback_data="accounts:clear")])
    else:
        rows.append([InlineKeyboardButton(text="— No accounts yet —", callback_data="noop")])
    rows.append([InlineKeyboardButton(text="🔙 Back", callback_data="menu:admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def is_allowed(uid):
    return uid == OWNER_ID or uid in approved_users

async def _del(chat_id, msg_id, delay=0):
    try:
        if delay:
            await asyncio.sleep(delay)
        await bot.delete_message(chat_id, msg_id)
    except Exception:
        pass

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    first_name = message.from_user.first_name or "there"
    username = f"@{message.from_user.username}" if message.from_user.username else "no username"

    user_data.pop(uid, None)
    banner_id = creating_msg.pop(uid, None)
    if banner_id:
        asyncio.create_task(_del(uid, banner_id))

    if uid == OWNER_ID:
        approved_users.add(uid)

    if uid not in seen_users:
        seen_users.add(uid)
        save_users()
        await message.answer(
            f"👋 *Welcome, {first_name}!*\n\n"
            f"This bot automatically creates Facebook accounts using Yandex email.\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📌 *How to use:*\n"
            f"1️⃣ Tap *Start Creating Accounts*\n"
            f"2️⃣ Choose name style\n"
            f"3️⃣ Choose gender\n"
            f"4️⃣ Set account password\n"
            f"5️⃣ Type how many accounts\n"
            f"6️⃣ Enter OTP when asked\n"
            f"7️⃣ Get account details with cookies!\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"⚠️ *Note:* Access requires owner approval.",
            parse_mode="Markdown"
        )

    if is_allowed(uid):
        await message.answer(
            "🤖 *Facebook Auto Creator (Yandex Email)*\n\nSelect options step by step 👇",
            parse_mode="Markdown",
            reply_markup=make_start_kb(uid)
        )
        return

    if uid in pending_users:
        await message.answer("⏳ Your access request is still *pending approval*. Please wait.", parse_mode="Markdown")
        return

    pending_users[uid] = {"name": first_name, "username": username}
    save_users()
    req_msg = await message.answer(
        "🔒 *Access Required*\n\nThis bot requires approval to use.\nYour request has been sent to the owner.\n\nPlease wait for approval ⏳",
        parse_mode="Markdown"
    )
    pending_users[uid]["req_msg_id"] = req_msg.message_id
    try:
        await bot.send_message(
            OWNER_ID,
            f"🔔 *New Access Request*\n\n👤 Name: *{first_name}*\n🆔 User ID: `{uid}`\n📛 Username: {username}\n\nApprove or deny below:",
            parse_mode="Markdown",
            reply_markup=make_approval_kb(uid)
        )
    except Exception:
        pass

@dp.message(Command("credits"))
async def cmd_credits(message: types.Message):
    uid = message.from_user.id
    banner_id = creating_msg.pop(uid, None)
    if banner_id:
        asyncio.create_task(_del(uid, banner_id))
    if uid == OWNER_ID:
        await message.answer("👑 You have *unlimited credits* as owner.", parse_mode="Markdown")
        return
    if not is_allowed(uid):
        return
    credits = user_credits.get(uid, 0)
    await message.answer(f"💳 *Your Credits*\n\nAvailable: *{credits}* credit(s)\n_(1 credit = 1 account created)_", parse_mode="Markdown")

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("🔒 Owner only.")
        return
    total_seen = len(seen_users)
    total_approved = len([u for u in approved_users if u != OWNER_ID])
    total_pending = len(pending_users)
    total_credits_remaining = sum(user_credits.values())
    total_accounts = len(created_accounts)
    await message.answer(
        f"📊 *Bot Statistics*\n\n"
        f"👥 Total Users Seen: *{total_seen}*\n"
        f"✅ Approved Users: *{total_approved}*\n"
        f"⏳ Pending Requests: *{total_pending}*\n"
        f"💳 Total Credits Used: *{total_accounts}*\n"
        f"💰 Total Credits Remaining: *{total_credits_remaining}*\n"
        f"🤖 Total Accounts Created: *{total_accounts}*",
        parse_mode="Markdown"
    )

@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return
    await message.answer("⚙️ *Owner Menu*\n\nChoose a section:", parse_mode="Markdown", reply_markup=make_admin_menu_kb())

@dp.callback_query(lambda c: c.data.startswith("access:"))
async def cb_approval(callback: types.CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("You are not the owner.", show_alert=True)
        return
    
    parts = callback.data.split(":")
    action = parts[1]
    target_id = int(parts[2])
    user_info = pending_users.get(target_id, {})
    name = user_info.get("name", "User")
    
    if action == "ok":
        approved_users.add(target_id)
        pending_users.pop(target_id, None)
        await callback.message.edit_text(
            f"✅ *Approved!* 👤 {name} (`{target_id}`)\n\n💳 *How many credits to give this user?*\n_(1 credit = 1 account)_",
            parse_mode="Markdown",
            reply_markup=make_credit_give_kb(target_id)
        )
    else:
        pending_users.pop(target_id, None)
        await callback.message.edit_text(f"❌ *Denied.*\n👤 {name} (`{target_id}`) has been rejected.", parse_mode="Markdown")
        await bot.send_message(target_id, "❌ *Your access request was denied.*\n\nContact the owner if you think this is a mistake.", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("credits:give:"))
async def cb_give_credits(callback: types.CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("Owner only.", show_alert=True)
        return
    
    parts = callback.data.split(":")
    target_id = int(parts[2])
    amount = parts[3]
    
    amount = int(amount)
    user_credits[target_id] = user_credits.get(target_id, 0) + amount
    total = user_credits[target_id]
    save_users()
    
    target_info = pending_users.get(target_id, {})
    name = target_info.get("name", str(target_id))
    
    await callback.message.edit_text(f"✅ *Credits given!*\n👤 {name} (`{target_id}`) now has *{total}* credit(s).", parse_mode="Markdown")
    try:
        req_msg_id = pending_users.get(target_id, {}).get("req_msg_id")
        if req_msg_id:
            asyncio.create_task(_del(target_id, req_msg_id))
        await bot.send_message(
            target_id,
            f"✅ *Your access has been approved!*\n\n💳 You've been given *{amount}* credit(s).\n_(1 credit = 1 account)_\n\nTap below to start 👇",
            parse_mode="Markdown",
            reply_markup=make_start_kb(target_id)
        )
    except Exception:
        pass
    await callback.answer(f"✅ Gave {amount} credits!", show_alert=True)

@dp.callback_query(lambda c: c.data.startswith("credits:add:"))
async def cb_add_credits(callback: types.CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("Owner only.", show_alert=True)
        return
    target_id = int(callback.data.split(":")[2])
    info = pending_users.get(target_id, {})
    name = info.get("name", str(target_id))
    total = user_credits.get(target_id, 0)
    await callback.message.edit_text(
        f"💳 *Add Credits*\n👤 {name} (`{target_id}`) — current: *{total}* credit(s)\n\nHow many to add?",
        parse_mode="Markdown",
        reply_markup=make_credit_give_kb(target_id)
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu:admin")
async def cb_admin_menu(callback: types.CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("Owner only.", show_alert=True)
        return
    await callback.message.edit_text("⚙️ *Owner Menu*\n\nChoose a section:", parse_mode="Markdown", reply_markup=make_admin_menu_kb())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu:back")
async def cb_menu_back(callback: types.CallbackQuery):
    uid = callback.from_user.id
    await callback.message.edit_text("🤖 *Facebook Auto Creator (Yandex Email)*\n\nSelect options step by step 👇", parse_mode="Markdown", reply_markup=make_start_kb(uid))
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu:users")
async def cb_menu_users(callback: types.CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("Owner only.", show_alert=True)
        return
    users = [u for u in approved_users if u != OWNER_ID]
    header = f"👥 *Approved Users* — {len(users)} user(s)\n\nManage credits & access:"
    await callback.message.edit_text(header, parse_mode="Markdown", reply_markup=make_users_kb())
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("revoke:"))
async def cb_revoke(callback: types.CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("Owner only.", show_alert=True)
        return
    target = int(callback.data.split(":")[1])
    approved_users.discard(target)
    user_credits.pop(target, None)
    save_users()
    try:
        await bot.send_message(target, "🚫 Your access to this bot has been revoked.")
    except Exception:
        pass
    users = [u for u in approved_users if u != OWNER_ID]
    header = f"👥 *Approved Users* — {len(users)} user(s)\n\nManage credits & access:"
    await callback.message.edit_text(header, parse_mode="Markdown", reply_markup=make_users_kb())
    await callback.answer(f"🚫 Revoked access for {target}", show_alert=True)

@dp.callback_query(lambda c: c.data == "menu:accounts")
async def cb_menu_accounts(callback: types.CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("Owner only.", show_alert=True)
        return
    if not created_accounts:
        text = "📋 *Created Accounts*\n\nNo accounts have been created yet."
    else:
        lines = []
        for i, acc in enumerate(created_accounts[-10:], 1):
            lines.append(f"*{i}.* 👤 `{acc['name']}`\n    📧 `{acc['email']}`\n    🔑 `{acc['password']}`\n    🆔 `{acc['uid']}`")
        body = "\n\n".join(lines)
        text = f"📋 *Created Accounts* — {len(created_accounts)} total\n\n{body}"
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=make_accounts_kb())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "accounts:clear")
async def cb_accounts_clear(callback: types.CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("Owner only.", show_alert=True)
        return
    count = len(created_accounts)
    created_accounts.clear()
    save_users()
    await callback.message.edit_text(f"🗑 *Cleared!* {count} account record(s) removed.\n\n📋 *Created Accounts*\n\nNo accounts yet.", parse_mode="Markdown", reply_markup=make_accounts_kb())
    await callback.answer("✅ Cleared!", show_alert=True)

@dp.callback_query(lambda c: c.data == "menu:myaccs")
async def cb_my_accounts(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if not is_allowed(uid):
        await callback.answer("No access.", show_alert=True)
        return
    mine = [a for a in created_accounts if a.get("by") == uid]
    if not mine:
        text = "📋 *My Created Accounts*\n\nYou haven't created any accounts yet."
    else:
        lines = []
        for i, acc in enumerate(mine[-10:], 1):
            lines.append(f"*{i}.* 👤 `{acc['name']}`\n    📧 `{acc['email']}`\n    🔑 `{acc['password']}`\n    🆔 `{acc['uid']}`")
        body = "\n\n".join(lines)
        text = f"📋 *My Created Accounts* — {len(mine)} total\n\n{body}"
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back", callback_data="menu:back")]])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu:botaccs")
async def cb_bot_accounts(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if not is_allowed(uid):
        await callback.answer("No access.", show_alert=True)
        return
    is_owner = (uid == OWNER_ID)
    mine = created_accounts if is_owner else [a for a in created_accounts if a.get("by") == uid]
    label = "🌐 *Bot Accounts*" if is_owner else "📋 *My Accounts*"
    if not mine:
        text = f"{label}\n\nNo accounts created yet."
    else:
        lines = []
        for i, acc in enumerate(mine[-10:], 1):
            by_line = f"\n    👤 by `{acc.get('by', '?')}`" if is_owner else ""
            lines.append(f"*{i}.* 👤 `{acc['name']}`\n    📧 `{acc['email']}`\n    🔑 `{acc['password']}`\n    🆔 `{acc['uid']}`{by_line}")
        body = "\n\n".join(lines)
        text = f"{label} — {len(mine)} account(s)\n\n{body}"
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back", callback_data="menu:back")]])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu:mycredits")
async def cb_my_credits(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if not is_allowed(uid):
        await callback.answer("No access.", show_alert=True)
        return
    credits = user_credits.get(uid, 0)
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back", callback_data="menu:back")]])
    await callback.message.edit_text(f"💳 *My Credits*\n\nAvailable: *{credits}* credit(s)\n_(1 credit = 1 account created)_", parse_mode="Markdown", reply_markup=back_kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "noop")
async def cb_noop(callback: types.CallbackQuery):
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu:create")
async def cb_name_style(callback: types.CallbackQuery):
    if not is_allowed(callback.from_user.id):
        await callback.answer("⛔ You don't have access. Use /start to request.", show_alert=True)
        return
    await callback.message.edit_text("📛 Choose *Name Style*:", parse_mode="Markdown", reply_markup=make_name_kb())
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("back:"))
async def cb_back(callback: types.CallbackQuery):
    uid = callback.from_user.id
    step = callback.data.split(":")[1]
    if uid in user_data:
        user_data[uid].pop("awaiting", None)
        user_data[uid].pop("prompt_msg_id", None)
    if step == "main":
        user_data.pop(uid, None)
        await callback.message.edit_text("🤖 *Facebook Auto Creator (Yandex Email)*\n\nSelect options step by step 👇", parse_mode="Markdown", reply_markup=make_start_kb(uid))
    elif step == "name":
        await callback.message.edit_text("📛 Choose *Name Style*:", parse_mode="Markdown", reply_markup=make_name_kb())
    elif step == "gender":
        await callback.message.edit_text("⚤ Choose *Gender*:", parse_mode="Markdown", reply_markup=make_gender_kb())
    elif step == "accpass":
        await callback.message.edit_text("🔑 *Set a password for the created accounts:*", parse_mode="Markdown", reply_markup=make_acc_pass_kb())
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("name:"))
async def cb_gender(callback: types.CallbackQuery):
    uid = callback.from_user.id
    user_data[uid] = {"name": callback.data.split(":")[1]}
    await callback.message.edit_text("⚤ Choose *Gender*:", parse_mode="Markdown", reply_markup=make_gender_kb())
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("gender:"))
async def cb_gender_select(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if uid not in user_data:
        await callback.answer("Session expired. Use /start", show_alert=True)
        return
    user_data[uid]["gender"] = callback.data.split(":")[1]
    await callback.message.edit_text("🔑 *Set a password for the created accounts:*", parse_mode="Markdown", reply_markup=make_acc_pass_kb())
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("accpass:"))
async def cb_acc_pass(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if uid not in user_data:
        await callback.answer("Session expired. Use /start", show_alert=True)
        return
    choice = callback.data.split(":")[1]
    if choice == "random":
        user_data[uid]["password"] = None
        user_data[uid]["awaiting"] = "count"
        user_data[uid]["prompt_msg_id"] = callback.message.message_id
        await callback.message.edit_text(
            "🔢 *How many accounts do you want to create?*\n\n_(Type a number, e.g. 5)_",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back", callback_data="back:accpass")]])
        )
    else:
        user_data[uid]["awaiting"] = "custom_pass"
        user_data[uid]["prompt_msg_id"] = callback.message.message_id
        await callback.message.edit_text(
            "🔑 *Type your custom password for the accounts:*\n\n_(minimum 6 characters)_",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back", callback_data="back:accpass")]])
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("stop:"))
async def cb_stop(callback: types.CallbackQuery):
    uid = int(callback.data.split(":")[1])
    if callback.from_user.id != uid and callback.from_user.id != OWNER_ID:
        await callback.answer("Not your session.", show_alert=True)
        return
    stop_flags[uid] = True
    if uid in otp_sessions:
        del otp_sessions[uid]
    creating_msg.pop(uid, None)
    await callback.answer("🛑 Stopped!", show_alert=False)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await bot.send_message(uid, "🛑 *Creation stopped.*", parse_mode="Markdown")
    await bot.send_message(uid, "🤖 *Facebook Auto Creator (Yandex Email)*\n\nSelect options step by step 👇", parse_mode="Markdown", reply_markup=make_start_kb(uid))

# Handle messages (OTP and count/password)
@dp.message()
async def handle_message(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    
    # Check for OTP
    if uid in otp_sessions:
        session_data = otp_sessions[uid]
        
        if text.isdigit() and len(text) in [5, 6]:
            await message.answer("⏳ *Verifying OTP...*", parse_mode="Markdown")
            
            success = fb.submit_otp(session_data["session"], text)
            
            if success:
                cookies = session_data["session"].cookies.get_dict()
                cookie_string = "; ".join([f"{k}={v}" for k, v in cookies.items()])
                
                account_data = {
                    "name": session_data["name"],
                    "email": session_data["email"],
                    "password": session_data["password"],
                    "uid": cookies.get("c_user", "Unknown"),
                    "cookies": cookie_string,
                    "by": uid
                }
                
                created_accounts.append(account_data)
                save_users()
                
                if uid != OWNER_ID:
                    user_credits[uid] = max(0, user_credits.get(uid, 0) - 1)
                    save_users()
                
                await message.answer(
                    f"✅ *Account Verified Successfully!*\n\n"
                    f"👤 *Name:* `{account_data['name']}`\n"
                    f"📧 *Email:* `{account_data['email']}`\n"
                    f"🔑 *Password:* `{account_data['password']}`\n"
                    f"🆔 *UID:* `{account_data['uid']}`\n\n"
                    f"🍪 *Full Cookies:*\n`{cookie_string}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📝 *Save these details safely!*",
                    parse_mode="Markdown"
                )
                
                del otp_sessions[uid]
                
                await message.answer(
                    "🤖 *Facebook Auto Creator (Yandex Email)*\n\nSelect options step by step 👇",
                    parse_mode="Markdown",
                    reply_markup=make_start_kb(uid)
                )
            else:
                await message.answer("❌ *Invalid OTP!* Please check the code and try again.\n\nSend the correct 5-6 digit code:")
        else:
            await message.answer("❌ *Invalid code format!* Please send only the 5-6 digit OTP number.")
        return
    
    # Handle waiting for input
    data = user_data.get(uid)
    awaiting = data.get("awaiting") if data else None
    
    if not data or awaiting not in ("custom_pass", "count"):
        return
    
    prompt_msg_id = data.pop("prompt_msg_id", None)
    asyncio.create_task(_del(message.chat.id, message.message_id))
    if prompt_msg_id:
        asyncio.create_task(_del(message.chat.id, prompt_msg_id))
    
    if awaiting == "custom_pass":
        if len(text) < 6:
            err = await message.answer("⚠️ Password too short _(min 6 chars)_. Try again:", parse_mode="Markdown")
            asyncio.create_task(_del(message.chat.id, err.message_id, delay=4))
            user_data[uid]["awaiting"] = "custom_pass"
            user_data[uid]["prompt_msg_id"] = err.message_id
            return
        
        user_data[uid]["password"] = text
        user_data[uid].pop("awaiting", None)
        
        prompt = await message.answer(
            "✅ *Custom password set!*\n\n🔢 *How many accounts do you want to create?*\n\n_(Type a number, e.g. 5)_",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back", callback_data="back:accpass")]])
        )
        user_data[uid]["awaiting"] = "count"
        user_data[uid]["prompt_msg_id"] = prompt.message_id
        return
    
    if awaiting == "count":
        if not text.isdigit() or int(text) <= 0:
            err = await message.answer("⚠️ Please type a *valid number* (e.g. 5).", parse_mode="Markdown")
            asyncio.create_task(_del(message.chat.id, err.message_id, delay=4))
            user_data[uid]["awaiting"] = "count"
            user_data[uid]["prompt_msg_id"] = err.message_id
            return
        
        count = int(text)
        
        if uid != OWNER_ID:
            available = user_credits.get(uid, 0)
            if available <= 0:
                err = await message.answer("❌ *You have no credits left.*\nContact the owner to get more credits.", parse_mode="Markdown")
                asyncio.create_task(_del(message.chat.id, err.message_id, delay=6))
                user_data.pop(uid, None)
                return
            if count > available:
                count = available
                note = await message.answer(f"⚠️ You only have *{available}* credit(s). Creating *{available}* account(s).", parse_mode="Markdown")
                asyncio.create_task(_del(message.chat.id, note.message_id, delay=5))
        
        data = user_data.pop(uid)
        
        banner = await message.answer(
            f"⚡ *Creating {count} account(s)...*\n\n📧 Using Yandex email\n💡 You'll be asked for OTP for each account if needed.",
            parse_mode="Markdown",
            reply_markup=make_stop_kb(uid)
        )
        creating_msg[uid] = banner.message_id
        
        success_count = 0
        
        for i in range(count):
            if stop_flags.get(uid):
                break
            
            ses = _requests.Session()
            
            result = fb.register_account_with_otp(
                ses,
                name_option=data.get("name", "1"),
                gender_option=data.get("gender", "3"),
                custom_pass=data.get("password", None)
            )
            
            if result is None:
                await message.answer(f"❌ *Account {i+1}/{count} Failed*\nCould not complete registration.")
                continue
            
            if result.get("uid"):
                success_count += 1
                
                if uid != OWNER_ID:
                    user_credits[uid] = max(0, user_credits.get(uid, 0) - 1)
                    save_users()
                
                created_accounts.append({
                    "name": result["name"],
                    "email": result["email"],
                    "password": result["password"],
                    "uid": result["uid"],
                    "cookies": result["cookies"],
                    "by": uid
                })
                save_users()
                
                credits_left = "" if uid == OWNER_ID else f"\n💳 Credits left: *{user_credits.get(uid, 0)}*"
                
                await message.answer(
                    f"✅ *Account {success_count}/{count} Created!*\n\n"
                    f"👤 *Name:* `{result['name']}`\n"
                    f"📧 *Email:* `{result['email']}`\n"
                    f"🔑 *Password:* `{result['password']}`\n"
                    f"🆔 *UID:* `{result['uid']}`\n"
                    f"🍪 *Cookies:* `{result['cookies'][:100]}...`{credits_left}",
                    parse_mode="Markdown"
                )
                
            elif result.get("needs_otp"):
                otp_sessions[uid] = {
                    "session": result["session"],
                    "email": result["email"],
                    "name": result["name"],
                    "password": result["password"]
                }
                
                await message.answer(
                    f"📧 *OTP Required for Account {i+1}/{count}*\n\n"
                    f"👤 *Name:* `{result['name']}`\n"
                    f"📧 *Yandex Email:* `{result['email']}`\n\n"
                    f"🔐 *Please check your Yandex inbox and send the 5-6 digit OTP code here.*\n\n"
                    f"_The OTP will arrive within 30 seconds_",
                    parse_mode="Markdown"
                )
                return
        
        banner_id = creating_msg.pop(uid, None)
        if banner_id:
            asyncio.create_task(_del(message.chat.id, banner_id))
        
        credits_summary = "" if uid == OWNER_ID else f"\n💳 Credits remaining: *{user_credits.get(uid, 0)}*"
        
        if success_count == 0:
            await message.answer(
                "❌ *No accounts were created.*\n\nFacebook may be blocking registrations. Try again later.",
                parse_mode="Markdown"
            )
        else:
            await message.answer(f"🎉 *Done!* {success_count}/{count} accounts created.{credits_summary}", parse_mode="Markdown")
        
        await message.answer(
            "🤖 *Facebook Auto Creator (Yandex Email)*\n\nSelect options step by step 👇",
            parse_mode="Markdown",
            reply_markup=make_start_kb(uid)
        )

async def main():
    print("🤖 Bot is running with Yandex Email support...")
    logging.basicConfig(level=logging.INFO)
    load_users()
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🚀 Start the bot"),
        types.BotCommand(command="myaccs", description="📋 My created accounts"),
        types.BotCommand(command="credits", description="💳 Check your credits"),
    ])
    
    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="🚀 Start the bot"),
            types.BotCommand(command="myaccs", description="📋 My created accounts"),
            types.BotCommand(command="botaccs", description="🌐 All bot accounts"),
            types.BotCommand(command="credits", description="💳 Credits info"),
            types.BotCommand(command="stats", description="📊 Bot statistics"),
            types.BotCommand(command="menu", description="⚙️ Owner menu"),
        ],
        scope=types.BotCommandScopeChat(chat_id=OWNER_ID)
    )
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
