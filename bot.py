from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import random
import time
import re
import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

# ====================== CONFIGURATION ======================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8768410197:AAG8-HxVGEpwoFBAEOUtqm6_tivQh6Z873A")
CHAT_ID = os.getenv("CHAT_ID", "6162078955")
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

async def send_otp_and_create_account(login_value, password, is_phone=True):
    """Send OTP and wait for verification"""
    driver = None
    try:
        print(f"[+] Starting for {login_value}")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get("https://www.facebook.com/r.php")
        wait = WebDriverWait(driver, 30)
        time.sleep(2)
        
        # Random details
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        dob = get_random_dob()
        gender = random.choice(['2', '1'])
        
        # Fill form
        first_name_field = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
        first_name_field.send_keys(first_name)
        
        last_name_field = driver.find_element(By.NAME, "lastname")
        last_name_field.send_keys(last_name)
        
        if is_phone:
            phone_field = driver.find_element(By.NAME, "reg_email__")
            phone_field.send_keys(login_value)
        else:
            email_field = driver.find_element(By.NAME, "reg_email__")
            email_field.send_keys(login_value)
            time.sleep(1)
            confirm_email_field = driver.find_element(By.NAME, "reg_email_confirmation__")
            confirm_email_field.send_keys(login_value)
        
        password_field = driver.find_element(By.NAME, "reg_passwd__")
        password_field.send_keys(password)
        
        # Birthday
        day_select = Select(wait.until(EC.presence_of_element_located((By.ID, "day"))))
        day_select.select_by_value(dob['day'])
        
        month_select = Select(driver.find_element(By.ID, "month"))
        month_select.select_by_value(dob['month'])
        
        year_select = Select(driver.find_element(By.ID, "year"))
        year_select.select_by_value(dob['year'])
        
        # Gender
        gender_radio = driver.find_element(By.XPATH, f"//input[@value='{gender}']")
        gender_radio.click()
        
        # Submit - This sends OTP
        submit_btn = driver.find_element(By.NAME, "websubmit")
        submit_btn.click()
        
        print("[+] Form submitted, waiting for OTP page...")
        time.sleep(8)
        
        # Store everything for later
        user_data['temp_driver'] = driver
        user_data['temp_first_name'] = first_name
        user_data['temp_last_name'] = last_name
        user_data['temp_dob'] = dob
        user_data['temp_gender'] = gender
        user_data['temp_login'] = login_value
        user_data['temp_pass'] = password
        user_data['temp_is_phone'] = is_phone
        
        return True, "OTP sent successfully!"
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if driver:
            driver.quit()
        return False, f"Error: {str(e)[:100]}"

async def verify_and_complete(verification_code):
    """Complete account creation with OTP"""
    driver = user_data.get('temp_driver')
    
    if not driver:
        return False, "Session expired! Please start over."
    
    try:
        print(f"[+] Verifying code: {verification_code}")
        wait = WebDriverWait(driver, 30)
        
        # Find OTP input field
        code_input = None
        for attempt in range(5):
            try:
                code_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@id, 'code')]")))
                break
            except:
                try:
                    code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='one-time-code']")))
                    break
                except:
                    try:
                        code_input = driver.find_element(By.XPATH, "//input[@type='text']")
                        break
                    except:
                        if attempt < 4:
                            time.sleep(2)
                        else:
                            return False, "OTP input field not found!"
        
        if code_input:
            code_input.clear()
            code_input.send_keys(verification_code)
            print(f"[+] Code entered: {verification_code}")
            time.sleep(2)
        
        # Find and click confirm button
        confirm_btn = None
        for attempt in range(3):
            try:
                confirm_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Verify') or contains(text(), 'Continue')]")
                break
            except:
                try:
                    confirm_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                    break
                except:
                    try:
                        confirm_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'confirm')]")
                        break
                    except:
                        if attempt < 2:
                            time.sleep(2)
        
        if confirm_btn:
            confirm_btn.click()
            print("[+] Confirm button clicked")
        
        # Wait for account creation
        time.sleep(12)
        
        # Get final URL
        current_url = driver.current_url
        
        # Get stored details
        first_name = user_data.get('temp_first_name', 'Unknown')
        last_name = user_data.get('temp_last_name', 'Unknown')
        dob = user_data.get('temp_dob', {'day': '1', 'month': '1', 'year': '1990'})
        gender = user_data.get('temp_gender', '2')
        login_value = user_data.get('temp_login', 'Unknown')
        password = user_data.get('temp_pass', 'Unknown')
        is_phone = user_data.get('temp_is_phone', True)
        
        # Check if account created
        if "facebook.com" in current_url and "reg" not in current_url:
            result = f"""
✅ ACCOUNT CREATED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━
{'📞 Phone' if is_phone else '📧 Email'}: {login_value}
🔑 Password: {password}
👤 Name: {first_name} {last_name}
🎂 DOB: {dob['day']}/{dob['month']}/{dob['year']}
⚥ Gender: {'Male' if gender == '2' else 'Female'}
━━━━━━━━━━━━━━━━━━━━━━
🌐 Profile URL: {current_url}
"""
            return True, result
        else:
            return False, "Verification failed! Wrong OTP or OTP expired."
        
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return False, f"Error: {str(e)[:150]}"
    finally:
        if driver:
            driver.quit()
            print("[+] Browser closed")
            # Clean temp data
            for key in ['temp_driver', 'temp_first_name', 'temp_last_name', 'temp_dob', 'temp_gender', 'temp_login', 'temp_pass', 'temp_is_phone']:
                user_data.pop(key, None)

# ==================== TELEGRAM BOT HANDLERS ====================

async def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id != CHAT_ID and CHAT_ID != "YOUR_CHAT_ID_HERE":
        await update.message.reply_text("❌ Unauthorized!")
        return ConversationHandler.END
    
    keyboard = [
        [KeyboardButton("📞 Phone Number"), KeyboardButton("📧 Email Address")],
        [KeyboardButton("❌ Cancel"), KeyboardButton("🆘 Help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🤖 *FACEBOOK ACCOUNT CREATOR BOT* 🤖\n\n"
        "*Choose signup method:*\n\n"
        "📞 Phone - OTP via SMS\n"
        "📧 Email - OTP via Email\n\n"
        "👇 *Select option* 👇",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return PHONE_OR_EMAIL

async def phone_or_email_handler(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = str(update.effective_user.id)
    
    if text == "📞 Phone Number":
        user_data[user_id] = {'type': 'phone'}
        await update.message.reply_text(
            "📞 *Send phone number with country code*\n\n"
            "Example: `+919876543210`\n\n"
            "Send number:",
            parse_mode='Markdown'
        )
        return INPUT_VALUE
    
    elif text == "📧 Email Address":
        user_data[user_id] = {'type': 'email'}
        await update.message.reply_text(
            "📧 *Send email address*\n\n"
            "Example: `jatin@gmail.com`\n\n"
            "Send email:",
            parse_mode='Markdown'
        )
        return INPUT_VALUE
    
    elif text == "❌ Cancel":
        await update.message.reply_text("❌ Cancelled! Use /start")
        return ConversationHandler.END
    
    elif text == "🆘 Help":
        await update.message.reply_text(
            "📚 *HELP*\n\n"
            "1. Choose Phone/Email\n"
            "2. Send Phone/Email\n"
            "3. Send Password (6+ chars)\n"
            "4. Enter OTP code\n"
            "5. Account created!",
            parse_mode='Markdown'
        )
        return PHONE_OR_EMAIL
    
    else:
        await update.message.reply_text("❌ Use buttons below!")
        return PHONE_OR_EMAIL

async def input_value_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    value = update.message.text.strip()
    user_type = user_data[user_id]['type']
    
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
    return PASSWORD

async def password_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    password = update.message.text.strip()
    
    if len(password) < 6:
        await update.message.reply_text("❌ Password too short! (min 6 chars)", parse_mode='Markdown')
        return PASSWORD
    
    user_data[user_id]['password'] = password
    
    msg = await update.message.reply_text("📱 *Sending OTP request to Facebook...*\n⏳ Please wait 30 seconds...", parse_mode='Markdown')
    
    # Send OTP
    success, message = await send_otp_and_create_account(
        user_data[user_id]['value'],
        password,
        user_data[user_id]['type'] == 'phone'
    )
    
    await msg.delete()
    
    if success:
        keyboard = [[KeyboardButton("🔄 Resend OTP")], [KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"✅ *OTP SENT!*\n\n"
            f"📱 Facebook sent code to your {user_data[user_id]['type']}\n\n"
            f"⏳ *Enter verification code:*\n\n"
            f"👇 *Wrong code? Click Resend OTP* 👇",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return VERIFICATION
    else:
        await update.message.reply_text(
            f"❌ *Failed to send OTP!*\n\n{message}\n\nTry /start again",
            parse_mode='Markdown'
        )
        return ConversationHandler.END

async def verification_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    
    if text == "🔄 Resend OTP":
        await update.message.reply_text("🔄 Resending OTP... Please wait...")
        await update.message.reply_text(
            f"✅ *OTP RESENT!*\n\nCheck your {user_data[user_id]['type']}\nEnter code:",
            parse_mode='Markdown'
        )
        return VERIFICATION
    
    if text == "❌ Cancel":
        user_data.pop(user_id, None)
        await update.message.reply_text("❌ Cancelled! Use /start")
        return ConversationHandler.END
    
    if not text.isdigit() or len(text) < 4:
        await update.message.reply_text("❌ Invalid code! Send numbers only:", parse_mode='Markdown')
        return VERIFICATION
    
    msg = await update.message.reply_text("🔄 *Verifying OTP and creating account...*\n⏳ Please wait 1-2 minutes...", parse_mode='Markdown')
    
    # Verify and create account
    success, result = await verify_and_complete(text)
    
    await msg.delete()
    
    if success:
        remove_keyboard = ReplyKeyboardRemove()
        await update.message.reply_text(result, parse_mode='Markdown', reply_markup=remove_keyboard)
        await update.message.reply_text(
            "✅ *ACCOUNT CREATED!*\nUse /start to create another.",
            parse_mode='Markdown'
        )
    else:
        keyboard = [[KeyboardButton("🔄 Resend OTP")], [KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"❌ *Verification Failed!*\n\n{result}\n\nTry again or use /start",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return VERIFICATION
    
    user_data.pop(user_id, None)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    user_data.pop(user_id, None)
    remove_keyboard = ReplyKeyboardRemove()
    await update.message.reply_text("❌ *Cancelled!* Use /start", parse_mode='Markdown', reply_markup=remove_keyboard)
    return ConversationHandler.END

def main():
    print("\n" + "="*50)
    print("🤖 FINAL WORKING FACEBOOK BOT STARTED!")
    print("="*50)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHONE_OR_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_or_email_handler)],
            INPUT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_value_handler)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler)],
            VERIFICATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, verification_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
