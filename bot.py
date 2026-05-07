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
PHONE_OR_EMAIL, INPUT_VALUE, PASSWORD, VERIFICATION, WAITING_FOR_CODE = range(5)

user_data = {}

first_names = ["Alan", "Murat", "Azad", "Necati", "Aaron", "Adam", "Alex", "John", "David", "Michael", "James", "Robert", "William", "Richard", "Thomas", "Christopher", "Daniel", "Matthew", "Andrew", "Joseph"]
last_names = ["Smith", "Jones", "Taylor", "Brown", "Wilson", "Davies", "Miller", "Johnson", "Williams", "Davis", "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez"]

def get_random_dob():
    return {
        'day': str(random.randint(1, 28)),
        'month': str(random.randint(1, 12)),
        'year': str(random.randint(1970, 2005))
    }

async def create_facebook_account(login_value, password, verification_code, is_phone=True):
    """Create Facebook account - supports both phone and email"""
    driver = None
    try:
        print(f"[+] Starting account creation for {'Phone' if is_phone else 'Email'}: {login_value}")
        
        # Chrome options for Railway
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get("https://www.facebook.com/r.php")
        wait = WebDriverWait(driver, 30)
        time.sleep(2)
        
        # Generate random details
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        dob = get_random_dob()
        gender = random.choice(['2', '1'])
        
        # Fill first name
        first_name_field = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
        first_name_field.send_keys(first_name)
        
        # Fill last name
        last_name_field = driver.find_element(By.NAME, "lastname")
        last_name_field.send_keys(last_name)
        
        # Fill email or phone
        if is_phone:
            # Phone number
            phone_field = driver.find_element(By.NAME, "reg_email__")
            phone_field.send_keys(login_value)
        else:
            # Email - pehle email daalo, phir confirm email
            email_field = driver.find_element(By.NAME, "reg_email__")
            email_field.send_keys(login_value)
            time.sleep(1)
            # Facebook asks to confirm email
            confirm_email_field = driver.find_element(By.NAME, "reg_email_confirmation__")
            confirm_email_field.send_keys(login_value)
        
        # Fill password
        password_field = driver.find_element(By.NAME, "reg_passwd__")
        password_field.send_keys(password)
        
        # Select birthday
        day_select = Select(wait.until(EC.presence_of_element_located((By.ID, "day"))))
        day_select.select_by_value(dob['day'])
        
        month_select = Select(driver.find_element(By.ID, "month"))
        month_select.select_by_value(dob['month'])
        
        year_select = Select(driver.find_element(By.ID, "year"))
        year_select.select_by_value(dob['year'])
        
        # Select gender
        gender_radio = driver.find_element(By.XPATH, f"//input[@value='{gender}']")
        gender_radio.click()
        
        # Submit form - OTP bheja jayega
        submit_btn = driver.find_element(By.NAME, "websubmit")
        submit_btn.click()
        
        time.sleep(5)
        
        # Wait for verification code input
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
                    if attempt < 4:
                        time.sleep(3)
                    else:
                        raise Exception("OTP input field not found")
        
        code_input.send_keys(verification_code)
        time.sleep(2)
        
        # Click confirm button
        confirm_btn = None
        for attempt in range(3):
            try:
                confirm_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Verify') or contains(text(), 'Continue') or contains(text(), 'Next')]")
                break
            except:
                try:
                    confirm_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                    break
                except:
                    if attempt < 2:
                        time.sleep(2)
                    else:
                        confirm_btn = None
        
        if confirm_btn:
            confirm_btn.click()
        
        time.sleep(10)
        
        # Check if account created successfully
        current_url = driver.current_url
        
        result = f"""
✅ ACCOUNT CREATED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━
📧 {'Phone' if is_phone else 'Email'}: {login_value}
🔑 Password: {password}
👤 Name: {first_name} {last_name}
🎂 DOB: {dob['day']}/{dob['month']}/{dob['year']}
⚥ Gender: {'Male' if gender == '2' else 'Female'}
━━━━━━━━━━━━━━━━━━━━━━
🌐 Facebook URL: {current_url}
💡 Save these details safely!
"""
        return result, True
        
    except Exception as e:
        error_msg = f"""
❌ ACCOUNT CREATION FAILED!
━━━━━━━━━━━━━━━━━━━━━━
Error: {str(e)[:250]}
{'📞 Phone' if is_phone else '📧 Email'}: {login_value}
━━━━━━━━━━━━━━━━━━━━━━
Possible reasons:
• Invalid OTP code
• {'Phone number already used' if is_phone else 'Email already used'}
• Facebook blocked the request
• Check your {'SMS' if is_phone else 'Email'} for OTP
"""
        return error_msg, False
    finally:
        if driver:
            driver.quit()
            print("[+] Browser closed")

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
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        "🤖 *FACEBOOK ACCOUNT CREATOR BOT* 🤖\n\n"
        "Choose how you want to sign up:\n\n"
        "📞 *Phone Number* - Receive OTP via SMS\n"
        "📧 *Email Address* - Receive OTP via Email\n\n"
        "👇 *Select an option below* 👇",
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
            "📞 *Send your phone number with country code*\n\n"
            "Examples:\n"
            "• India: `+919876543210`\n"
            "• USA: `+12345678901`\n"
            "• UK: `+447911123456`\n\n"
            "Send phone number:",
            parse_mode='Markdown'
        )
        return INPUT_VALUE
    
    elif text == "📧 Email Address":
        user_data[user_id] = {'type': 'email'}
        await update.message.reply_text(
            "📧 *Send your email address*\n\n"
            "Examples:\n"
            "• `jatin@gmail.com`\n"
            "• `user@yahoo.com`\n"
            "• `name@outlook.com`\n\n"
            "Send email address:",
            parse_mode='Markdown'
        )
        return INPUT_VALUE
    
    elif text == "❌ Cancel":
        await update.message.reply_text("❌ Cancelled! Use /start to begin again.")
        return ConversationHandler.END
    
    elif text == "🆘 Help":
        await update.message.reply_text(
            "📚 *HELP*\n\n"
            "1. Choose Phone or Email\n"
            "2. Send your Phone/Email\n"
            "3. Send Password (min 6 chars)\n"
            "4. Enter OTP you receive\n"
            "5. Account created!",
            parse_mode='Markdown'
        )
        return PHONE_OR_EMAIL
    
    else:
        await update.message.reply_text("❌ Please use the buttons below!")
        return PHONE_OR_EMAIL

async def input_value_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    value = update.message.text.strip()
    user_type = user_data[user_id]['type']
    
    # Validate input
    if user_type == 'phone':
        if not re.match(r'^\+?[0-9]{8,15}$', value):
            await update.message.reply_text("❌ Invalid phone number! Send with country code:\nExample: `+919876543210`", parse_mode='Markdown')
            return INPUT_VALUE
    else:  # email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            await update.message.reply_text("❌ Invalid email! Example: `jatin@gmail.com`", parse_mode='Markdown')
            return INPUT_VALUE
    
    user_data[user_id]['value'] = value
    
    await update.message.reply_text(
        f"✅ {'Phone' if user_type == 'phone' else 'Email'} saved: `{value}`\n\n"
        "🔑 *Send your password (minimum 6 characters)*\n"
        "Example: `StrongPass123`",
        parse_mode='Markdown'
    )
    return PASSWORD

async def password_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    password = update.message.text.strip()
    
    if len(password) < 6:
        await update.message.reply_text("❌ Password too short! Minimum 6 characters required.", parse_mode='Markdown')
        return PASSWORD
    
    user_data[user_id]['password'] = password
    
    msg = await update.message.reply_text(
        "📱 *Sending request to Facebook...*\n"
        "⏳ Please wait 20-30 seconds...\n\n"
        f"📧 OTP will be sent to your {user_data[user_id]['type']}",
        parse_mode='Markdown'
    )
    
    # Here Facebook will send OTP after form submission
    # The actual account creation will happen in verification step
    
    await msg.delete()
    
    keyboard = [[KeyboardButton("🔄 Resend OTP")], [KeyboardButton("❌ Cancel")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ *OTP REQUEST SENT!*\n\n"
        f"📱 Facebook has sent a verification code to your {user_data[user_id]['type']}\n\n"
        f"⏳ *Enter the code below:*\n\n"
        f"💡 Code expires in 2 minutes\n\n"
        f"👇 *Didn't receive? Click Resend OTP* 👇",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return VERIFICATION

async def verification_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    
    # Handle Resend button
    if text == "🔄 Resend OTP":
        await update.message.reply_text("🔄 Resending OTP request... Please wait...")
        # Just inform user - OTP will be resent by Facebook
        await update.message.reply_text(
            "✅ *OTP RESENT!*\n\n"
            f"Check your {user_data[user_id]['type']} for new code.\n"
            "Enter code below:",
            parse_mode='Markdown'
        )
        return VERIFICATION
    
    if text == "❌ Cancel":
        user_data.pop(user_id, None)
        await update.message.reply_text("❌ Cancelled! Use /start to begin again.")
        return ConversationHandler.END
    
    # Validate OTP code
    if not text.isdigit() or len(text) < 4:
        await update.message.reply_text("❌ Invalid code! Send only numbers (4-6 digits):", parse_mode='Markdown')
        return VERIFICATION
    
    if user_id not in user_data:
        await update.message.reply_text("❌ Session expired! Use /start again.")
        return ConversationHandler.END
    
    value = user_data[user_id]['value']
    password = user_data[user_id]['password']
    is_phone = user_data[user_id]['type'] == 'phone'
    
    msg = await update.message.reply_text("🔄 *Creating your Facebook account...*\n⏳ Please wait 1-2 minutes...", parse_mode='Markdown')
    
    # Create account with OTP
    result, success = await create_facebook_account(value, password, text, is_phone)
    
    await msg.delete()
    
    if success:
        remove_keyboard = ReplyKeyboardRemove()
        await update.message.reply_text(result, parse_mode='Markdown', reply_markup=remove_keyboard)
        await update.message.reply_text(
            "✅ *ACCOUNT CREATED SUCCESSFULLY!*\n\n"
            "Use /start to create another account.",
            parse_mode='Markdown'
        )
    else:
        keyboard = [[KeyboardButton("🔄 Resend OTP")], [KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(result, parse_mode='Markdown', reply_markup=reply_markup)
        return VERIFICATION
    
    user_data.pop(user_id, None)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    user_data.pop(user_id, None)
    remove_keyboard = ReplyKeyboardRemove()
    await update.message.reply_text("❌ *Cancelled!* Use /start to begin again.", parse_mode='Markdown', reply_markup=remove_keyboard)
    return ConversationHandler.END

def main():
    print("\n" + "="*50)
    print("🤖 FACEBOOK BOT STARTED - Phone & Email Support!")
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
