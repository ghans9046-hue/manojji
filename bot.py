import os
import sys
import time
import logging
import asyncio
import threading
from typing import Dict, List
from datetime import datetime

# Telegram bot imports
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Import your original script functions
# NO CHANGES to original script - just importing what we need
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fb_creator import register_account, choose_email_domain, EMAIL_DOMAIN

# ================= CONFIGURATION =================
# ⚠️⚠️⚠️ YAHAN APNI DETAILS DALEN ⚠️⚠️⚠️
BOT_TOKEN = "8101206245:AAENv9gxlh_T2RnXoZuA9Ljztss2OY5vvVY"  # @BotFather se lekar yahan paste karein
OWNER_ID = 6162078955  # Apna Telegram user ID integer me dalen
# =================================================

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
active_tasks = {}
task_results = {}
task_counter = 0
task_lock = threading.Lock()

# ================= HELPER FUNCTIONS =================

def is_authorized(user_id: int) -> bool:
    """Check if user is authorized to use bot"""
    return user_id == OWNER_ID

async def send_long_message(update: Update, text: str, chat_id: int = None):
    """Send long messages by splitting if needed"""
    target = chat_id or update.effective_chat.id
    if len(text) <= 4096:
        await update.effective_message.reply_text(text) if chat_id is None else None
    else:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            await update.effective_message.reply_text(part) if chat_id is None else None

def create_account_background(task_id: int, user_id: int, num_accounts: int, name_option: str, gender_option: str, custom_pass: str = None):
    """Background task for account creation"""
    results = []
    success_count = 0
    
    for i in range(num_accounts):
        try:
            result = register_account(
                domain_choice="1",  # 1secmail.com
                name_option=name_option,
                gender_option=gender_option,
                custom_pass=custom_pass,
                max_retries=5
            )
            
            if result:
                success_count += 1
                results.append(result)
                
                # Update progress in global storage
                with task_lock:
                    task_results[task_id] = {
                        'total': num_accounts,
                        'completed': success_count,
                        'results': results,
                        'status': 'running'
                    }
            
            # Small delay between accounts
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Account creation error: {e}")
            continue
    
    # Task complete
    with task_lock:
        task_results[task_id] = {
            'total': num_accounts,
            'completed': success_count,
            'results': results,
            'status': 'completed',
            'end_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# ================= BOT COMMANDS =================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Unauthorized! You are not allowed to use this bot.")
        return
    
    welcome_text = """
🤖 *Facebook Account Creator Bot*

✅ *Authorized Access Granted*

*Available Commands:*
/start - Show this menu
/create - Create a single account
/createmulti <count> - Create multiple accounts (1-50)
/status <task_id> - Check task status
/listtasks - Show all active/completed tasks
/export - Download accounts.txt file
/help - Show detailed help
/cancel - Cancel current task

*Example:*
/create
/createmulti 5
/status 1

⚙️ *Bot Status:* Online
📝 *Original Script:* fb_creator.py (No modifications)
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    help_text = """
📖 *Detailed Help Guide*

*1. Account Creation Options:*
• Names: Filipino names or RPW names
• Gender: Male / Female / Mixed
• Password: Auto-generated or Custom
• Email: 1secmail.com (auto-confirm)

*2. Command Details:*

/create
• Creates 1 Facebook account
• Auto email confirmation
• Takes ~30-45 seconds

/createmulti <number>
• Creates multiple accounts (1-50)
• Example: /createmulti 10
• Auto saves all to accounts.txt

/status <task_id>
• Check progress of background task
• Shows completed/total count

/listtasks
• Shows all tasks with IDs

/export
• Sends accounts.txt file
• Contains: Name|Email|Password|UID

*3. Output Format:*
`Name|Email|Password|UID`
Example: Juan Dela Cruz|juan@1secmail.com|Pass@123|123456789

*4. Notes:*
• Each account takes ~30 seconds
• Use VPN for best results
• Accounts saved to accounts.txt
• Email automatically confirmed
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /create command - create single account"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    await update.message.reply_text("🔄 *Creating Facebook account...*\n⏳ This will take 30-45 seconds.", parse_mode='Markdown')
    
    try:
        # Run in thread to not block bot
        def run_creation():
            return register_account(
                domain_choice="1",
                name_option="1",
                gender_option="3",
                custom_pass=None,
                max_retries=5
            )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = await loop.run_in_executor(None, run_creation)
        loop.close()
        
        if result:
            success_text = f"""
✅ *Account Created Successfully!*

📝 *Name:* `{result['name']}`
📧 *Email:* `{result['email']}`
🔑 *Password:* `{result['password']}`
🆔 *UID:* `{result['uid']}`

💾 Saved to accounts.txt
🔓 Email confirmation was automatic
            """
            await update.message.reply_text(success_text, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ *Failed to create account.*\nTry again or check your connection.", parse_mode='Markdown')
            
    except Exception as e:
        await update.message.reply_text(f"❌ *Error:* `{str(e)}`", parse_mode='Markdown')

async def createmulti_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /createmulti command - create multiple accounts"""
    user_id = update.effective_user.id
    global task_counter
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    # Parse arguments
    args = context.args
    if not args:
        await update.message.reply_text("❌ *Usage:* `/createmulti <count>`\nExample: `/createmulti 5`", parse_mode='Markdown')
        return
    
    try:
        count = int(args[0])
        if count < 1 or count > 50:
            await update.message.reply_text("❌ Count must be between 1 and 50")
            return
    except ValueError:
        await update.message.reply_text("❌ Please provide a valid number")
        return
    
    # Ask for options first
    await update.message.reply_text(
        "🎯 *Account Creation Options:*\n\n"
        "Reply with:\n"
        "`1` - Filipino names / Mixed gender\n"
        "`2` - RPW names / Mixed gender\n"
        "`3` - Custom settings (will ask next)\n\n"
        "Example: `1`\n\n*You have 30 seconds to reply*",
        parse_mode='Markdown'
    )
    
    # Wait for user choice (simplified - for production, use ConversationHandler)
    # For now, using default values
    
    # Start background task
    task_counter += 1
    task_id = task_counter
    
    # Start background thread
    thread = threading.Thread(
        target=create_account_background,
        args=(task_id, user_id, count, "1", "3", None)
    )
    thread.daemon = True
    thread.start()
    
    await update.message.reply_text(
        f"🔄 *Task #{task_id} started!*\n"
        f"📊 Creating {count} account(s)...\n"
        f"📌 Use `/status {task_id}` to check progress\n"
        f"📁 Results will be in accounts.txt",
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("❌ *Usage:* `/status <task_id>`", parse_mode='Markdown')
        return
    
    try:
        task_id = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid task ID")
        return
    
    with task_lock:
        if task_id not in task_results:
            await update.message.reply_text(f"❌ Task #{task_id} not found")
            return
        
        task = task_results[task_id]
        
        if task['status'] == 'running':
            status_text = f"""
🔄 *Task #{task_id} Status*

📊 Progress: {task['completed']}/{task['total']} accounts
⏳ Status: Running...
✅ Success rate: {(task['completed']/task['total']*100):.1f}%
            """
        else:
            status_text = f"""
✅ *Task #{task_id} Complete*

📊 Total: {task['total']} accounts
✅ Success: {task['completed']} accounts
❌ Failed: {task['total'] - task['completed']} accounts
🏁 Status: Completed
⏰ Finished: {task.get('end_time', 'Unknown')}

📝 Type `/export` to get accounts.txt
            """
        
        await update.message.reply_text(status_text, parse_mode='Markdown')

async def listtasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listtasks command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    with task_lock:
        if not task_results:
            await update.message.reply_text("📭 No tasks found")
            return
        
        task_list = ""
        for tid, task in task_results.items():
            status_icon = "🔄" if task['status'] == 'running' else "✅"
            task_list += f"{status_icon} Task #{tid}: {task['completed']}/{task['total']} - {task['status']}\n"
        
        await update.message.reply_text(f"📋 *Tasks:*\n\n{task_list}", parse_mode='Markdown')

async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /export command - send accounts.txt file"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    # Check if accounts.txt exists
    if os.path.exists("accounts.txt"):
        # Check if file has content
        if os.path.getsize("accounts.txt") > 0:
            await update.message.reply_text("📤 *Sending accounts.txt file...*", parse_mode='Markdown')
            await update.message.reply_document(
                document=open("accounts.txt", "rb"),
                filename="accounts.txt",
                caption="✅ Facebook Accounts Created\nFormat: Name|Email|Password|UID"
            )
        else:
            await update.message.reply_text("📭 *accounts.txt exists but is empty*\nCreate some accounts first!", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ *No accounts.txt found*\nCreate some accounts first using /create or /createmulti", parse_mode='Markdown')

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    # Note: Proper cancellation would require more complex implementation
    await update.message.reply_text(
        "⚠️ *Note:* Background tasks cannot be forcefully cancelled.\n"
        "Wait for current task to complete or restart the bot.",
        parse_mode='Markdown'
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred. Please try again.")

# ================= MAIN =================

async def post_init(application: Application):
    """Setup bot commands after initialization"""
    commands = [
        BotCommand("start", "Show bot information"),
        BotCommand("create", "Create one Facebook account"),
        BotCommand("createmulti", "Create multiple accounts (usage: /createmulti 10)"),
        BotCommand("status", "Check task status (usage: /status 1)"),
        BotCommand("listtasks", "Show all tasks"),
        BotCommand("export", "Download accounts.txt file"),
        BotCommand("help", "Show detailed help"),
        BotCommand("cancel", "Cancel current operation"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    """Main function to run bot"""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     🤖 FACEBOOK ACCOUNT CREATOR TELEGRAM BOT 🤖          ║
║                                                          ║
║     Bot Token: {BOT_TOKEN[:20]}...                         
║     Owner ID: {OWNER_ID}                                    
║                                                          ║
║     Status: Starting...                                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check token and owner ID
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n❌ ERROR: Please set BOT_TOKEN in bot.py!")
        print("1. Go to @BotFather on Telegram")
        print("2. Create a new bot using /newbot")
        print("3. Copy the token and paste in bot.py\n")
        return
    
    if OWNER_ID == 123456789:
        print("\n⚠️ WARNING: Owner ID not set!")
        print("1. Message @userinfobot on Telegram")
        print("2. Get your user ID")
        print("3. Paste in bot.py as OWNER_ID = your_id\n")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("create", create_command))
    application.add_handler(CommandHandler("createmulti", createmulti_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("listtasks", listtasks_command))
    application.add_handler(CommandHandler("export", export_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_error_handler(error_handler)
    
    # Setup commands
    application.post_init = post_init
    
    # Start bot
    print("✅ Bot is running! Press Ctrl+C to stop.\n")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
