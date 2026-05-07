from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import random
import time
import re
import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

# ====================== CONFIGURATION ======================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8768410197:AAG8-HxVGEpwoFBAEOUtqm6_tivQh6Z873A")
CHAT_ID = os.getenv("CHAT_ID", "6162078955")
PROXY = None  # Proxy daalni hai toh yahan daalo
# ============================================================

# States
PHONE_OR_EMAIL, INPUT_VALUE, PASSWORD, VERIFICATION = range(4)

user_data = {}

first_names = ["Alan", "Murat", "Azad", "Necati", "Aaron", "Adam", "Alex", "John", "David", "Michael", "James", "Robert", "William", "Richard", "Thomas", "Christopher", "Daniel", "Matthew", "Andrew", "Joseph"]
last_names = ["Smith", "Jones", "Taylor", "Brown", "Wilson", "Davies", "Miller", "Johnson", "Williams", "Davis", "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez"]

def get_random_dob():
    return {
        'day': str(random.randint(1, 28)),
        'month': str(random.randint(1, 12)),
        'year': str(random.randint(1970, 2005))
    }

def random_delay(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

async def create_facebook_account_undetected(login_value, password, is_phone=True):
    driver = None
    try:
        print(f"[+] Starting for {login_value}")
        
        options = uc.ChromeOptions()
        if PROXY:
            options.add_argument(f'--proxy-server={PROXY}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless=new')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        driver = uc.Chrome(options=options, version_main=120)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get("https://www.facebook.com/r.php")
        random_delay(2, 3)
        
        wait = WebDriverWait(driver, 45)
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        dob = get_random_dob()
        gender = random.choice(['2', '1'])
        
        # First name
        first_name_field = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
        first_name_field.send_keys(first_name)
        random_delay(0.5, 1)
        
        # Last name
        last_name_field = driver.find_element(By.NAME, "lastname")
        last_name_field.send_keys(last_name)
        random_delay(0.5, 1)
        
        # Email/Phone
        if is_phone:
            phone_field = driver.find_element(By.NAME, "reg_email__")
            phone_field.send_keys(login_value)
        else:
            email_field = driver.find_element(By.NAME, "reg_email__")
            email_field.send_keys(login_value)
            random_delay(1, 2)
            confirm_email_field = driver.find_element(By.NAME, "reg_email_confirmation__")
            confirm_email_field.send_keys(login_value)
        
        random_delay(0.5, 1)
        
        # Password
        password_field = driver.find_element(By.NAME, "reg_passwd__")
        password_field.send_keys(password)
        random_delay(0.5, 1)
        
        # Birthday
        day_select = Select(wait.until(EC.presence_of_element_located((By.ID, "day"))))
        day_select.select_by_value(dob['day'])
        random_delay(0.3, 0.6)
        
        month_select = Select(driver.find_element(By.ID, "month"))
        month_select.select_by_value(dob['month'])
        random_delay(0.3, 0.6)
        
        year_select = Select(driver.find_element(By.ID, "year"))
        year_select.select_by_value(dob['year'])
        random_delay(0.3, 0.6)
        
        # Gender
        gender_radio = driver.find_element(By.XPATH, f"//input[@value='{gender}']")
        gender_radio.click()
        random_delay(0.5, 1)
        
        # Submit
        submit_btn = driver.find_element(By.NAME, "websubmit")
        submit_btn.click()
        
        print("[+] Form submitted")
        random_delay(8, 12)
        
        # Check captcha
        if "checkpoint" in driver.current_url or "captcha" in driver.current_url:
            return False, "Captcha detected! Try with residential proxy.", None
        
        # Store for later
        user_data['temp_driver'] = driver
        user_data['temp_first_name'] = first_name
        user_data['temp_last_name'] = last_name
        user_data['temp_dob'] = dob
        user_data['temp_gender'] = gender
        user_data['temp_login'] = login_value
        user_data['temp_pass'] = password
        
        return True, "OTP sent!", driver
        
    except Exception as e:
        print(f"Error: {e}")
        if driver:
            driver.quit()
        return False, f"Error: {str(e)[:100]}", None

async def verify_and_complete(code):
    driver = user_data.get('temp_driver')
    if not driver:
        return False, "Session expired!"
    
    try:
        wait = WebDriverWait(driver, 30)
        
        # Find OTP input
        code_input = None
        for attempt in range(5):
            try:
                code_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
                break
            except:
                random_delay(1, 2)
        
        if code_input:
            code_input.send_keys(code)
            random_delay(1, 2)
        
        # Click confirm
        confirm_btn = None
        for attempt in range(3):
            try:
                confirm_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Verify')]")
                break
            except:
                random_delay(1, 2)
        
        if confirm_btn:
            confirm_btn.click()
        
        random_delay(10, 15)
        
        first_name = user_data.get('temp_first_name', 'Unknown')
        last_name = user_data.get('temp_last_name', 'Unknown')
        dob = user_data.get('temp_dob', {'day': '1', 'month': '1', 'year': '1990'})
        gender = user_data.get('temp_gender', '2')
        login_value = user_data.get('temp_login', 'Unknown')
        password = user_data.get('temp_pass', 'Unknown')
        
        result = f"""
✅ ACCOUNT CREATED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━
📧 Email/Phone: {login_value}
🔑 Password: {password}
👤 Name: {first_name} {last_name}
🎂 DOB: {dob['day']}/{dob['month']}/{dob['year']}
⚥ Gender: {'Male' if gender == '2' else 'Female'}
━━━━━━━━━━━━━━━━━━━━━━
"""
        return True, result
        
    except Exception as e:
        return False, f"Verification failed: {str(e)[:100]}"
    finally:
        if driver:
            driver.quit()
            for key in ['temp_driver', 'temp_first_name', 'temp_last_name', 'temp_dob', 'temp_gender', 'temp_login', 'temp_pass']:
                user_data.pop(key, None)

# ==================== TELEGRAM BOT ====================

async def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if CHAT_ID and user_id != CHAT_ID and CHAT_ID != "YOUR_CHAT_ID_HERE":
        await update.message.reply_text("❌ Unauthorized!")
        return ConversationHandler.END
    
    keyboard = [
        [KeyboardButton("📞 Phone Number"), KeyboardButton("📧 Email Address")],
        [KeyboardButton("❌ Cancel")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🤖 *FACEBOOK ACCOUNT CREATOR* 🤖\n\n"
        "Choose signup method:\n\n"
        "📞 Phone - OTP via SMS\n"
        "📧 Email - OTP via Email\n\n"
        "👇 *Click button below* 👇",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return PHONE_OR_EMAIL

async def handle_message(update: Update, context: CallbackContext):
    """Smart handler - detects if user skipped buttons"""
    text = update.message.text.strip()
    user_id = str(update.effective_user.id)
    
    # Check current state from context
    current_state = context.user_data.get('state')
    
    # If user is in INPUT_VALUE state and sent direct value
    if current_state == INPUT_VALUE:
        return await input_value_handler(update, context)
    
    # If user is in PASSWORD state
    if current_state == PASSWORD:
        return await password_handler(update, context)
    
    # If user is in VERIFICATION state
    if current_state == VERIFICATION:
        return await verification_handler(update, context)
    
    # Otherwise handle as button choice or direct input
    if text in ["📞 Phone Number", "📧 Email Address", "❌ Cancel"]:
        return await phone_or_email_handler(update, context)
    else:
        # User sent direct phone/email without button
        # Detect if it looks like phone or email
        if re.match(r'^\+?[0-9]{8,15}$', text):
            user_data[user_id] = {'type': 'phone', 'value': text}
            await update.message.reply_text(
                f"✅ Phone saved: `{text}`\n\n🔑 *Send password (min 6 chars):*",
                parse_mode='Markdown'
            )
            context.user_data['state'] = PASSWORD
            return PASSWORD
        elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text):
            user_data[user_id] = {'type': 'email', 'value': text}
            await update.message.reply_text(
                f"✅ Email saved: `{text}`\n\n🔑 *Send password (min 6 chars):*",
                parse_mode='Markdown'
            )
            context.user_data['state'] = PASSWORD
            return PASSWORD
        else:
            await update.message.reply_text(
                "❌ *Invalid input!*\n\n"
                "Please use buttons below or send:\n"
                "• Phone: `+919876543210`\n"
                "• Email: `name@gmail.com`",
                parse_mode='Markdown'
            )
            return PHONE_OR_EMAIL

async def phone_or_email_handler(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = str(update.effective_user.id)
    
    if text == "📞 Phone Number":
        user_data[user_id] = {'type': 'phone'}
        await update.message.reply_text(
            "📞 *Send phone number with country code*\nExample: `+919876543210`",
            parse_mode='Markdown'
        )
        context.user_data['state'] = INPUT_VALUE
        return INPUT_VALUE
    
    elif text == "📧 Email Address":
        user_data[user_id] = {'type': 'email'}
        await update.message.reply_text(
            "📧 *Send email address*\nExample: `jatin@gmail.com`",
            parse_mode='Markdown'
        )
        context.user_data['state'] = INPUT_VALUE
        return INPUT_VALUE
    
    elif text == "❌ Cancel":
        user_data.pop(user_id, None)
        context.user_data.pop('state', None)
        await update.message.reply_text("❌ Cancelled! Use /start")
        return ConversationHandler.END
    
    else:
        # If user sent direct value, pass to input handler
        return await handle_message(update, context)

async def input_value_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    value = update.message.text.strip()
    
    if user_id not in user_data:
        user_data[user_id] = {}
    
    user_type = user_data[user_id].get('type', '')
    
    # Auto-detect type if not set
    if not user_type:
        if re.match(r'^\+?[0-9]{8,15}$', value):
            user_type = 'phone'
            user_data[user_id]['type'] = 'phone'
        elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            user_type = 'email'
            user_data[user_id]['type'] = 'email'
        else:
            await update.message.reply_text(
                "❌ *Invalid!* Send phone `+919876543210` or email `name@gmail.com`",
                parse_mode='Markdown'
            )
            return INPUT_VALUE
    
    # Validate
    if user_type == 'phone':
        if not re.match(r'^\+?[0-9]{8,15}$', value):
            await update.message.reply_text("❌ Invalid phone! Example: `+919876543210`", parse_mode='Markdown')
            return INPUT_VALUE
    else:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            await update.message.reply_text("❌ Invalid email! Example: `jatin@gmail.com`", parse_mode='Markdown')
            return INPUT_VALUE
    
    user_data[user_id]['value'] = value
    
    await update.message.reply_text(
        f"✅ Saved: `{value}`\n\n🔑 *Send password (min 6 chars):*",
        parse_mode='Markdown'
    )
    context.user_data['state'] = PASSWORD
    return PASSWORD

async def password_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    password = update.message.text.strip()
    
    if len(password) < 6:
        await update.message.reply_text("❌ Password too short! (min 6 chars)", parse_mode='Markdown')
        return PASSWORD
    
    if user_id not in user_data:
        user_data[user_id] = {}
    
    user_data[user_id]['password'] = password
    
    await update.message.reply_text("📱 *Sending OTP request...*\n⏳ Please wait 30 seconds...", parse_mode='Markdown')
    
    success, message, driver = await create_facebook_account_undetected(
        user_data[user_id]['value'],
        password,
        user_data[user_id]['type'] == 'phone'
    )
    
    if success:
        keyboard = [[KeyboardButton("🔄 Resend OTP")], [KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"✅ *OTP SENT!*\n\n"
            f"Code sent to your {user_data[user_id]['type']}\n\n"
            f"⏳ *Enter verification code:*\n\n"
            f"👇 *Wrong code? Click Resend OTP* 👇",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        context.user_data['state'] = VERIFICATION
        return VERIFICATION
    else:
        await update.message.reply_text(
            f"❌ *Failed!*\n\n{message}\n\nUse /start to try again",
            parse_mode='Markdown'
        )
        return ConversationHandler.END

async def verification_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    
    if text == "🔄 Resend OTP":
        await update.message.reply_text("🔄 *Resending OTP...*", parse_mode='Markdown')
        
        value = user_data[user_id]['value']
        password = user_data[user_id]['password']
        is_phone = user_data[user_id]['type'] == 'phone'
        
        success, message, driver = await create_facebook_account_undetected(value, password, is_phone)
        
        if success:
            await update.message.reply_text(f"✅ *OTP RESENT!*\n\nCheck your {user_data[user_id]['type']}\nEnter code:", parse_mode='Markdown')
            return VERIFICATION
        else:
            await update.message.reply_text(f"❌ Failed: {message}\nUse /start", parse_mode='Markdown')
            return ConversationHandler.END
    
    if text == "❌ Cancel":
        user_data.pop(user_id, None)
        context.user_data.pop('state', None)
        await update.message.reply_text("❌ Cancelled! Use /start")
        return ConversationHandler.END
    
    if not text.isdigit() or len(text) < 4:
        await update.message.reply_text("❌ Send numbers only (4-6 digits):", parse_mode='Markdown')
        return VERIFICATION
    
    msg = await update.message.reply_text("🔄 *Creating account...*\n⏳ Please wait...", parse_mode='Markdown')
    
    success, result = await verify_and_complete(text)
    
    await msg.delete()
    
    if success:
        remove = ReplyKeyboardRemove()
        await update.message.reply_text(result, parse_mode='Markdown', reply_markup=remove)
        await update.message.reply_text("✅ *ACCOUNT CREATED!*\nUse /start for more", parse_mode='Markdown')
    else:
        keyboard = [[KeyboardButton("🔄 Resend OTP")], [KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(f"❌ *Failed!*\n\n{result}\n\n👇 Try again 👇", parse_mode='Markdown', reply_markup=reply_markup)
        return VERIFICATION
    
    user_data.pop(user_id, None)
    context.user_data.pop('state', None)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    user_data.pop(user_id, None)
    context.user_data.clear()
    remove = ReplyKeyboardRemove()
    await update.message.reply_text("❌ Cancelled! Use /start", reply_markup=remove)
    return ConversationHandler.END

def main():
    print("\n" + "="*50)
    print("🤖 FACEBOOK BOT STARTED - FIXED VERSION")
    print("="*50)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHONE_OR_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            INPUT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_value_handler)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler)],
            VERIFICATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, verification_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
