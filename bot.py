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

# States for conversation
PHONE, PASSWORD, VERIFICATION, WAITING_FOR_CODE = range(4)

# Store user data
user_data = {}

# Name lists
first_names = ["Alan", "Murat", "Azad", "Necati", "Aaron", "Adam", "Alex", "John", "David", "Michael", "James", "Robert", "William", "Richard", "Thomas", "Christopher", "Daniel", "Matthew", "Andrew", "Joseph"]
last_names = ["Smith", "Jones", "Taylor", "Brown", "Wilson", "Davies", "Miller", "Johnson", "Williams", "Davis", "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez"]

def get_random_dob():
    return {
        'day': str(random.randint(1, 28)),
        'month': str(random.randint(1, 12)),
        'year': str(random.randint(1980, 2004))
    }

async def send_facebook_otp(phone_number, password):
    """Step 1: Send OTP to phone number"""
    driver = None
    try:
        print(f"[+] Sending OTP request to {phone_number}")
        
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
        
        driver.get("https://www.facebook.com/")
        wait = WebDriverWait(driver, 20)
        
        # Click create new account
        create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Create new account')]")))
        create_btn.click()
        time.sleep(2)
        
        # Generate random details
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        dob = get_random_dob()
        gender = random.choice(['1', '2'])
        
        # Fill form
        first_name_field = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
        first_name_field.send_keys(first_name)
        
        last_name_field = driver.find_element(By.NAME, "lastname")
        last_name_field.send_keys(last_name)
        
        phone_field = driver.find_element(By.NAME, "reg_email__")
        phone_field.send_keys(phone_number)
        
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
        
        # Submit form - THIS SENDS OTP
        submit_btn = driver.find_element(By.NAME, "websubmit")
        submit_btn.click()
        
        # Wait for OTP to be sent
        time.sleep(8)
        
        # Store user details for later use
        user_data['temp_details'] = {
            'first_name': first_name,
            'last_name': last_name,
            'dob': dob,
            'gender': gender,
            'driver': driver  # Store driver for later use
        }
        
        return True, driver, first_name, last_name, dob, gender
        
    except Exception as e:
        print(f"[-] Error sending OTP: {str(e)}")
        if driver:
            driver.quit()
        return False, None, None, None, None, None

async def verify_and_create_account(verification_code, driver, phone_number, password, first_name, last_name, dob, gender):
    """Step 2: Enter verification code and complete account creation"""
    try:
        print(f"[+] Verifying code: {verification_code}")
        
        wait = WebDriverWait(driver, 20)
        
        # Find code input field
        code_input = None
        for attempt in range(3):
            try:
                code_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@name, 'code')]")))
                break
            except:
                try:
                    code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='one-time-code']")))
                    break
                except:
                    if attempt < 2:
                        time.sleep(2)
                    else:
                        raise Exception("Verification code input not found")
        
        code_input.send_keys(verification_code)
        time.sleep(2)
        
        # Click confirm button
        verify_btn = None
        for attempt in range(3):
            try:
                verify_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Verify') or contains(text(), 'Continue')]")
                break
            except:
                try:
                    verify_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                    break
                except:
                    if attempt < 2:
                        time.sleep(2)
                    else:
                        raise Exception("Confirm button not found")
        
        verify_btn.click()
        time.sleep(10)
        
        current_url = driver.current_url
        
        result = f"""
✅ ACCOUNT CREATED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━
📞 Phone: {phone_number}
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
❌ VERIFICATION FAILED!
━━━━━━━━━━━━━━━━━━━━━━
Error: {str(e)[:200]}
Phone: {phone_number}
━━━━━━━━━━━━━━━━━━━━━━
• Check your OTP and try again
• OTP expires in 2 minutes
• Try RESEND CODE button
"""
        return error_msg, False
    finally:
        if driver:
            driver.quit()

# ==================== TELEGRAM BOT HANDLERS ====================

async def start(update: Update, context: CallbackContext):
    """Start command with buttons"""
    user_id = str(update.effective_user.id)
    
    if user_id != CHAT_ID and CHAT_ID != "YOUR_CHAT_ID_HERE":
        await update.message.reply_text("❌ Unauthorized!")
        return ConversationHandler.END
    
    keyboard = [
        [KeyboardButton("✅ START ACCOUNT CREATION")],
        [KeyboardButton("❌ CANCEL"), KeyboardButton("🆘 HELP")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        "🤖 *FB ACCOUNT CREATOR BOT BY JATIIN* 🤖\n\n"
        "I will create a Facebook account for you!\n\n"
        "📌 *Process:*\n"
        "1️⃣ Send phone number (with country code)\n"
        "2️⃣ Send password\n"
        "3️⃣ Facebook sends OTP to your phone\n"
        "4️⃣ Enter OTP to complete\n\n"
        "⚠️ *Requirements:*\n"
        "• Valid phone number (with country code)\n"
        "• Password (min 6 characters)\n"
        "• Must receive SMS\n\n"
        "✅ *Send your phone number now!*\n"
        "Example: `+919876543210`\n\n"
        "👇 *Use buttons below* 👇",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return PHONE

async def button_handler(update: Update, context: CallbackContext):
    """Handle button clicks"""
    text = update.message.text
    
    if text == "✅ START ACCOUNT CREATION":
        return await start(update, context)
    
    elif text == "❌ CANCEL":
        user_id = str(update.effective_user.id)
        user_data.pop(user_id, None)
        await update.message.reply_text("❌ *Cancelled!*", parse_mode='Markdown')
        return ConversationHandler.END
    
    elif text == "🆘 HELP":
        await update.message.reply_text(
            "📚 *HELP*\n\n"
            "1. Send phone: `+919876543210`\n"
            "2. Send password (min 6 chars)\n"
            "3. Wait for Facebook OTP\n"
            "4. Send OTP code\n"
            "5. Account created!",
            parse_mode='Markdown'
        )
        return PHONE
    
    elif text == "🔄 RESEND CODE":
        # Resend OTP
        user_id = str(update.effective_user.id)
        if user_id in user_data and 'driver' in user_data[user_id]:
            # Close old driver
            try:
                user_data[user_id]['driver'].quit()
            except:
                pass
        
        await update.message.reply_text("🔄 *Resending OTP... Please wait...*", parse_mode='Markdown')
        
        phone = user_data[user_id]['phone']
        password = user_data[user_id]['password']
        
        success, driver, fname, lname, dob, gender = await send_facebook_otp(phone, password)
        
        if success:
            user_data[user_id]['driver'] = driver
            user_data[user_id]['first_name'] = fname
            user_data[user_id]['last_name'] = lname
            user_data[user_id]['dob'] = dob
            user_data[user_id]['gender'] = gender
            
            # Show resend button
            keyboard = [[KeyboardButton("🔄 RESEND CODE")], [KeyboardButton("❌ CANCEL")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "✅ *OTP RESENT!*\n\n"
                "📱 Facebook has sent a new SMS to your phone\n"
                "⏳ Enter the 6-digit code below:\n\n"
                "💡 *Code expires in 2 minutes*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return VERIFICATION
        else:
            await update.message.reply_text("❌ Failed to resend OTP. Please /start again.")
            return ConversationHandler.END
    
    return None

async def phone_handler(update: Update, context: CallbackContext):
    """Handle phone number input"""
    user_id = str(update.effective_user.id)
    phone = update.message.text.strip()
    
    if not re.match(r'^\+?[0-9]{8,15}$', phone):
        await update.message.reply_text("❌ *Invalid phone number!*\nExample: `+919876543210`", parse_mode='Markdown')
        return PHONE
    
    user_data[user_id] = {'phone': phone}
    
    await update.message.reply_text(
        f"✅ Phone: `{phone}`\n\n🔑 *Send password (min 6 characters):*",
        parse_mode='Markdown'
    )
    return PASSWORD

async def password_handler(update: Update, context: CallbackContext):
    """Handle password input and send OTP"""
    user_id = str(update.effective_user.id)
    password = update.message.text.strip()
    
    if len(password) < 6:
        await update.message.reply_text("❌ *Password too short!* (min 6 chars)", parse_mode='Markdown')
        return PASSWORD
    
    user_data[user_id]['password'] = password
    
    # Send processing message
    msg = await update.message.reply_text("📱 *Sending OTP request to Facebook...*\n⏳ Please wait 30 seconds...", parse_mode='Markdown')
    
    # Send OTP to phone
    success, driver, fname, lname, dob, gender = await send_facebook_otp(
        user_data[user_id]['phone'], 
        password
    )
    
    await msg.delete()
    
    if success:
        user_data[user_id]['driver'] = driver
        user_data[user_id]['first_name'] = fname
        user_data[user_id]['last_name'] = lname
        user_data[user_id]['dob'] = dob
        user_data[user_id]['gender'] = gender
        
        # Show keyboard with RESEND button
        keyboard = [[KeyboardButton("🔄 RESEND CODE")], [KeyboardButton("❌ CANCEL")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "✅ *OTP SENT SUCCESSFULLY!*\n\n"
            "📱 Facebook has sent an SMS to your phone\n"
            "⏳ *Enter the 6-digit verification code:*\n\n"
            "💡 Code expires in 2 minutes\n\n"
            "👇 *Wrong OTP? Click RESEND CODE* 👇",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return VERIFICATION
    else:
        await update.message.reply_text(
            "❌ *Failed to send OTP!*\n\n"
            "Possible reasons:\n"
            "• Invalid phone number\n"
            "• Network issue\n"
            "• Facebook blocked request\n\n"
            "🔄 Try again with /start",
            parse_mode='Markdown'
        )
        return ConversationHandler.END

async def verification_handler(update: Update, context: CallbackContext):
    """Handle verification code and create account"""
    user_id = str(update.effective_user.id)
    code = update.message.text.strip()
    
    if not code.isdigit() or len(code) < 4:
        await update.message.reply_text("❌ *Invalid code!* Send only numbers:", parse_mode='Markdown')
        return VERIFICATION
    
    if user_id not in user_data:
        await update.message.reply_text("❌ Session expired! Use /start")
        return ConversationHandler.END
    
    phone = user_data[user_id]['phone']
    password = user_data[user_id]['password']
    driver = user_data[user_id].get('driver')
    fname = user_data[user_id].get('first_name')
    lname = user_data[user_id].get('last_name')
    dob = user_data[user_id].get('dob')
    gender = user_data[user_id].get('gender')
    
    msg = await update.message.reply_text("🔄 *Verifying OTP and creating account...*\n⏳ Please wait...", parse_mode='Markdown')
    
    result, success = await verify_and_create_account(code, driver, phone, password, fname, lname, dob, gender)
    
    await msg.delete()
    
    if success:
        # Remove keyboard
        remove_keyboard = ReplyKeyboardRemove()
        await update.message.reply_text(result, parse_mode='Markdown', reply_markup=remove_keyboard)
        await update.message.reply_text(
            "✅ *ACCOUNT CREATED!*\nUse /start to create another account.",
            parse_mode='Markdown'
        )
    else:
        # Keep RESEND button
        keyboard = [[KeyboardButton("🔄 RESEND CODE")], [KeyboardButton("❌ CANCEL")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(result, parse_mode='Markdown', reply_markup=reply_markup)
        return VERIFICATION
    
    user_data.pop(user_id, None)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    """Cancel conversation"""
    user_id = str(update.effective_user.id)
    
    # Close driver if exists
    if user_id in user_data and 'driver' in user_data[user_id]:
        try:
            user_data[user_id]['driver'].quit()
        except:
            pass
    
    user_data.pop(user_id, None)
    remove_keyboard = ReplyKeyboardRemove()
    await update.message.reply_text("❌ *Cancelled!*", parse_mode='Markdown', reply_markup=remove_keyboard)
    return ConversationHandler.END

def main():
    print("\n" + "="*50)
    print("🤖 FACEBOOK BOT WITH RESEND BUTTON STARTED!")
    print("="*50)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Text("✅ START ACCOUNT CREATION"), button_handler)
        ],
        states={
            PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, phone_handler),
                MessageHandler(filters.Text("❌ CANCEL"), button_handler),
                MessageHandler(filters.Text("🆘 HELP"), button_handler)
            ],
            PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler),
                MessageHandler(filters.Text("❌ CANCEL"), button_handler)
            ],
            VERIFICATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, verification_handler),
                MessageHandler(filters.Text("🔄 RESEND CODE"), button_handler),
                MessageHandler(filters.Text("❌ CANCEL"), button_handler)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
