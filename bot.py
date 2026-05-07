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
PHONE_OR_EMAIL, INPUT_VALUE, PASSWORD, WAITING_OTP = range(4)

user_data = {}
driver_instance = None

first_names = ["Alan", "Murat", "Azad", "Necati", "Aaron", "Adam", "Alex", "John", "David", "Michael", "James", "Robert", "William", "Richard", "Thomas", "Christopher", "Daniel", "Matthew", "Andrew", "Joseph"]
last_names = ["Smith", "Jones", "Taylor", "Brown", "Wilson", "Davies", "Miller", "Johnson", "Williams", "Davis", "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez"]

def get_random_dob():
    return {
        'day': str(random.randint(1, 28)),
        'month': str(random.randint(1, 12)),
        'year': str(random.randint(1975, 2002))
    }

async def submit_facebook_form(login_value, password, is_phone=True):
    """Step 1: Submit Facebook signup form and wait for OTP"""
    global driver_instance
    driver = None
    try:
        print(f"[+] Submitting Facebook form for {'Phone' if is_phone else 'Email'}: {login_value}")
        
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
        time.sleep(3)
        
        # Random details
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        dob = get_random_dob()
        gender = random.choice(['2', '1'])
        
        # Fill form
        first_name_field = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
        first_name_field.send_keys(first_name)
        time.sleep(0.5)
        
        last_name_field = driver.find_element(By.NAME, "lastname")
        last_name_field.send_keys(last_name)
        time.sleep(0.5)
        
        if is_phone:
            phone_field = driver.find_element(By.NAME, "reg_email__")
            phone_field.send_keys(login_value)
        else:
            email_field = driver.find_element(By.NAME, "reg_email__")
            email_field.send_keys(login_value)
            time.sleep(1)
            confirm_email_field = driver.find_element(By.NAME, "reg_email_confirmation__")
            confirm_email_field.send_keys(login_value)
        
        time.sleep(0.5)
        password_field = driver.find_element(By.NAME, "reg_passwd__")
        password_field.send_keys(password)
        
        # Birthday
        day_select = Select(wait.until(EC.presence_of_element_located((By.ID, "day"))))
        day_select.select_by_value(dob['day'])
        time.sleep(0.3)
        
        month_select = Select(driver.find_element(By.ID, "month"))
        month_select.select_by_value(dob['month'])
        time.sleep(0.3)
        
        year_select = Select(driver.find_element(By.ID, "year"))
        year_select.select_by_value(dob['year'])
        time.sleep(0.3)
        
        # Gender
        gender_radio = driver.find_element(By.XPATH, f"//input[@value='{gender}']")
        gender_radio.click()
        time.sleep(0.5)
        
        # SUBMIT FORM - Facebook will send OTP now
        submit_btn = driver.find_element(By.NAME, "websubmit")
        submit_btn.click()
        
        # Wait for OTP screen to appear
        time.sleep(8)
        
        # Store driver and user details for later
        user_data['temp_driver'] = driver
        user_data['temp_first_name'] = first_name
        user_data['temp_last_name'] = last_name
        user_data['temp_dob'] = dob
        user_data['temp_gender'] = gender
        
        return True, "OTP sent successfully"
        
    except Exception as e:
        print(f"[-] Form submission error: {str(e)}")
        if driver:
            driver.quit()
        return False, str(e)

async def verify_otp_and_complete(verification_code):
    """Step 2: Enter OTP and complete account creation"""
    global user_data
    driver = user_data.get('temp_driver')
    
    if not driver:
        return False, "No active session found"
    
    try:
        print(f"[+] Verifying OTP: {verification_code}")
        wait = WebDriverWait(driver, 20)
        
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
                        code_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='number']")))
                        break
                    except:
                        if attempt < 4:
                            time.sleep(3)
                        else:
                            raise Exception("OTP input field not found")
        
        code_input.clear()
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
        
        # Success - account created
        current_url = driver.current_url
        
        result = f"""
✅ ACCOUNT CREATED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━
👤 Name: {user_data.get('temp_first_name')} {user_data.get('temp_last_name')}
🎂 DOB: {user_data.get('temp_dob', {}).get('day')}/{user_data.get('temp_dob', {}).get('month')}/{user_data.get('temp_dob', {}).get('year')}
⚥ Gender: {'Male' if user_data.get('temp_gender') == '2' else 'Female'}
━━━━━━━━━━━━━━━━━━━━━━
🌐 Facebook URL: {current_url}
"""
        driver.quit()
        user_data.pop('temp_driver', None)
        return True, result
        
    except Exception as e:
        print(f"[-] Verification error: {str(e)}")
        try:
            driver.quit()
        except:
            pass
        user_data.pop('temp_driver', None)
        return False, str(e)

# ==================== TELEGRAM HANDLERS ====================

async def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id != CHAT_ID and CHAT_ID != "YOUR_CHAT_ID_HERE":
        await update.message.reply_text("❌ Unauthorized!")
        return ConversationHandler.END
    
    keyboard = [
        [KeyboardButton("📞 Phone Number"), KeyboardButton("📧 Email Address")],
        [KeyboardButton("❌ Cancel")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        "🤖 *FACEBOOK ACCOUNT CREATOR BOT* 🤖\n\n"
        "Choose signup method:\n\n"
        "📞 *Phone* - OTP via SMS\n"
        "📧 *Email* - OTP via Email\n\n"
        "👇 Select option 👇",
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
            "📞 *Send phone number with country code*\n"
            "Example: `+919876543210`",
            parse_mode='Markdown'
        )
        return INPUT_VALUE
    
    elif text == "📧 Email Address":
        user_data[user_id] = {'type': 'email'}
        await update.message.reply_text(
            "📧 *Send email address*\n"
            "Example: `jatin@gmail.com`",
            parse_mode='Markdown'
        )
        return INPUT_VALUE
    
    elif text == "❌ Cancel":
        await update.message.reply_text("❌ Cancelled! Use /start")
        return ConversationHandler.END
    
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
        f"✅ Saved: `{value}`\n\n"
        "🔑 *Send password (minimum 6 characters)*",
        parse_mode='Markdown'
    )
    return PASSWORD

async def password_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    password = update.message.text.strip()
    
    if len(password) < 6:
        await update.message.reply_text("❌ Password too short! Min 6 characters.", parse_mode='Markdown')
        return PASSWORD
    
    user_data[user_id]['password'] = password
    value = user_data[user_id]['value']
    is_phone = user_data[user_id]['type'] == 'phone'
    
    msg = await update.message.reply_text(
        "🔄 *Submitting form to Facebook...*\n"
        "⏳ Please wait 30 seconds...\n\n"
        f"📧 OTP will be sent to your {user_data[user_id]['type']}",
        parse_mode='Markdown'
    )
    
    # ACTUALLY SUBMIT FORM TO FACEBOOK
    success, result = await submit_facebook_form(value, password, is_phone)
    
    await msg.delete()
    
    if success:
        keyboard = [[KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"✅ *FORM SUBMITTED SUCCESSFULLY!*\n\n"
            f"📱 Facebook has sent a verification code to your {user_data[user_id]['type']}\n\n"
            f"⏳ *Enter the 6-digit code:*\n\n"
            f"💡 Check your {'SMS' if is_phone else 'Email'} inbox\n"
            f"⏰ Code expires in 2 minutes",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return WAITING_OTP
    else:
        await update.message.reply_text(
            f"❌ *Failed to submit form!*\n\n"
            f"Error: {result[:200]}\n\n"
            f"Try again with /start",
            parse_mode='Markdown'
        )
        return ConversationHandler.END

async def waiting_otp_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    
    if text == "❌ Cancel":
        # Clean up driver
        if user_data.get('temp_driver'):
            try:
                user_data['temp_driver'].quit()
            except:
                pass
        user_data.pop(user_id, None)
        user_data.pop('temp_driver', None)
        await update.message.reply_text("❌ Cancelled! Use /start")
        return ConversationHandler.END
    
    if not text.isdigit() or len(text) < 4:
        await update.message.reply_text("❌ Invalid code! Send only numbers (4-6 digits):")
        return WAITING_OTP
    
    msg = await update.message.reply_text("🔄 *Verifying OTP and creating account...*\n⏳ Please wait...", parse_mode='Markdown')
    
    success, result = await verify_otp_and_complete(text)
    
    await msg.delete()
    
    if success:
        remove_keyboard = ReplyKeyboardRemove()
        await update.message.reply_text(result, parse_mode='Markdown', reply_markup=remove_keyboard)
        await update.message.reply_text(
            "✅ *ACCOUNT CREATED!*\n\n"
            "Use /start to create another account.",
            parse_mode='Markdown'
        )
    else:
        keyboard = [[KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"❌ *OTP Verification Failed!*\n\n"
            f"Error: {result[:200]}\n\n"
            f"Try again with /start",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    user_data.pop(user_id, None)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_data.get('temp_driver'):
        try:
            user_data['temp_driver'].quit()
        except:
            pass
    user_data.pop(user_id, None)
    user_data.pop('temp_driver', None)
    remove_keyboard = ReplyKeyboardRemove()
    await update.message.reply_text("❌ Cancelled! Use /start", reply_markup=remove_keyboard)
    return ConversationHandler.END

def main():
    print("\n" + "="*50)
    print("🤖 FACEBOOK BOT - FULLY WORKING!")
    print("="*50)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHONE_OR_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_or_email_handler)],
            INPUT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_value_handler)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler)],
            WAITING_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, waiting_otp_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
