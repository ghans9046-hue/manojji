import os
import random
import time
import re
import asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from dotenv import load_dotenv
import requests
import json

# Load environment variables (optional, for other vars)
load_dotenv()

# ====================== CONFIGURATION ======================
# Token and Chat ID hardcoded as requested
BOT_TOKEN = "8768410197:AAG8-HxVGEpwoFBAEOUtqm6_tivQh6Z873A"
CHAT_ID = "6162078955"
# ============================================================

# States
CHOOSING_METHOD, INPUT_VALUE, PASSWORD, VERIFICATION = range(4)

user_data = {}
otp_cache = {}

first_names = ["Alan", "Murat", "Azad", "Necati", "Aaron", "Adam", "Alex", "John", "David", "Michael", "James", "Robert", "William", "Richard", "Thomas", "Christopher", "Daniel", "Matthew", "Andrew", "Joseph"]
last_names = ["Smith", "Jones", "Taylor", "Brown", "Wilson", "Davies", "Miller", "Johnson", "Williams", "Davis", "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez"]

# Proxy list (add your proxies here)
PROXIES = [
    # "http://user:pass@ip:port",
]

def get_random_dob():
    return {
        'day': str(random.randint(1, 28)),
        'month': str(random.randint(1, 12)),
        'year': str(random.randint(1970, 2005))
    }

def random_delay(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    return random.choice(user_agents)

def get_random_proxy():
    if PROXIES:
        return random.choice(PROXIES)
    return None

async def create_facebook_account(login_value, password, is_phone=True):
    driver = None
    try:
        print(f"[+] Starting account creation for {login_value}")
        
        # Use undetected-chromedriver
        options = uc.ChromeOptions()
        
        # Essential options for Railway
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-features=NetworkService,NetworkServiceInProcess')
        options.add_argument('--disable-infobars')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--window-size=1920,1080')
        
        # Random user agent
        options.add_argument(f'--user-agent={get_random_user_agent()}')
        
        # Accept languages
        options.add_argument('--lang=en-US,en;q=0.9')
        
        # Add proxy if available
        proxy = get_random_proxy()
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        # Create undetected driver
        driver = uc.Chrome(options=options, version_main=120)
        
        # Execute stealth scripts
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                window.chrome = {
                    runtime: {}
                };
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """
        })
        
        # Go to Facebook
        driver.get("https://www.facebook.com/r.php")
        random_delay(3, 5)
        
        wait = WebDriverWait(driver, 60)
        
        # Random details
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        dob = get_random_dob()
        gender = random.choice(['2', '1'])
        
        # Fill first name
        first_name_field = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
        for c in first_name:
            first_name_field.send_keys(c)
            time.sleep(random.uniform(0.05, 0.1))
        random_delay(0.5, 1)
        
        # Fill last name
        last_name_field = driver.find_element(By.NAME, "lastname")
        for c in last_name:
            last_name_field.send_keys(c)
            time.sleep(random.uniform(0.05, 0.1))
        random_delay(0.5, 1)
        
        # Fill email or phone
        if is_phone:
            phone_field = driver.find_element(By.NAME, "reg_email__")
            for c in login_value:
                phone_field.send_keys(c)
                time.sleep(random.uniform(0.03, 0.08))
        else:
            email_field = driver.find_element(By.NAME, "reg_email__")
            for c in login_value:
                email_field.send_keys(c)
                time.sleep(random.uniform(0.03, 0.08))
            random_delay(1, 2)
            try:
                confirm_email_field = driver.find_element(By.NAME, "reg_email_confirmation__")
                for c in login_value:
                    confirm_email_field.send_keys(c)
                    time.sleep(random.uniform(0.03, 0.08))
            except:
                pass
        
        random_delay(0.5, 1)
        
        # Fill password
        password_field = driver.find_element(By.NAME, "reg_passwd__")
        for c in password:
            password_field.send_keys(c)
            time.sleep(random.uniform(0.05, 0.1))
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
        
        print("[+] Form submitted, OTP should be sent...")
        random_delay(8, 12)
        
        # Store data for verification
        user_data['temp_driver'] = driver
        user_data['temp_first_name'] = first_name
        user_data['temp_last_name'] = last_name
        user_data['temp_dob'] = dob
        user_data['temp_gender'] = gender
        user_data['temp_login'] = login_value
        user_data['temp_pass'] = password
        user_data['temp_is_phone'] = is_phone
        
        return True, "OTP sent! Check your email/phone.", driver
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        return False, f"Error: {str(e)[:150]}", None

async def verify_account(verification_code):
    driver = user_data.get('temp_driver')
    
    if not driver:
        return False, "Session expired! Please start over."
    
    try:
        wait = WebDriverWait(driver, 30)
        
        # Try multiple selectors for OTP input
        code_input = None
        selectors = [
            "//input[@type='text']",
            "//input[@autocomplete='one-time-code']",
            "//input[contains(@id, 'code')]",
            "//input[contains(@name, 'code')]",
            "//input[@inputmode='numeric']"
        ]
        
        for selector in selectors:
            try:
                code_input = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                if code_input and code_input.is_displayed():
                    break
            except:
                continue
        
        if code_input:
            code_input.clear()
            for c in verification_code:
                code_input.send_keys(c)
                time.sleep(random.uniform(0.05, 0.1))
            random_delay(1, 2)
        
        # Click confirm button
        confirm_btn = None
        confirm_selectors = [
            "//button[contains(text(), 'Confirm')]",
            "//button[contains(text(), 'Verify')]",
            "//button[contains(text(), 'Continue')]",
            "//button[@type='submit']",
            "//div[@role='button'][contains(text(), 'Confirm')]"
        ]
        
        for selector in confirm_selectors:
            try:
                confirm_btn = driver.find_element(By.XPATH, selector)
                if confirm_btn and confirm_btn.is_displayed():
                    break
            except:
                continue
        
        if confirm_btn:
            confirm_btn.click()
        
        random_delay(12, 18)
        
        current_url = driver.current_url
        
        first_name = user_data.get('temp_first_name', 'Unknown')
        last_name = user_data.get('temp_last_name', 'Unknown')
        dob = user_data.get('temp_dob', {'day': '1', 'month': '1', 'year': '1990'})
        gender = user_data.get('temp_gender', '2')
        login_value = user_data.get('temp_login', 'Unknown')
        password = user_data.get('temp_pass', 'Unknown')
        is_phone = user_data.get('temp_is_phone', True)
        
        # Check if account created successfully
        if "facebook.com" in current_url and "reg" not in current_url and "checkpoint" not in current_url and "confirm" not in current_url:
            result = f"""
✅ ACCOUNT CREATED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━
{'📞 Phone' if is_phone else '📧 Email'}: {login_value}
🔑 Password: {password}
👤 Name: {first_name} {last_name}
🎂 DOB: {dob['day']}/{dob['month']}/{dob['year']}
⚥ Gender: {'Male' if gender == '2' else 'Female'}
━━━━━━━━━━━━━━━━━━━━━━
🌟 Account created! Save these details.
"""
            return True, result
        elif "checkpoint" in current_url:
            return False, "Account needs verification. Check your email/phone for additional confirmation."
        else:
            return False, "Wrong OTP or OTP expired. Click Resend OTP to try again."
        
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return False, f"Error: {str(e)[:150]}"
    finally:
        try:
            if driver:
                driver.quit()
        except:
            pass
        for key in ['temp_driver', 'temp_first_name', 'temp_last_name', 'temp_dob', 'temp_gender', 'temp_login', 'temp_pass', 'temp_is_phone']:
            user_data.pop(key, None)

# ==================== TELEGRAM BOT HANDLERS ====================

async def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id != CHAT_ID:
        await update.message.reply_text("❌ Unauthorized! You are not allowed to use this bot.")
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
    return CHOOSING_METHOD

async def choosing_method_handler(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = str(update.effective_user.id)
    
    if user_id != CHAT_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return ConversationHandler.END
    
    if text == "📞 Phone Number":
        user_data[user_id] = {'method': 'phone'}
        await update.message.reply_text(
            "📞 *Send phone number with country code*\n\n"
            "Example: `+919876543210`\n\n"
            "Send number:",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        return INPUT_VALUE
    
    elif text == "📧 Email Address":
        user_data[user_id] = {'method': 'email'}
        await update.message.reply_text(
            "📧 *Send email address*\n\n"
            "Example: `user@gmail.com`\n\n"
            "Send email:",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        return INPUT_VALUE
    
    elif text == "❌ Cancel":
        await update.message.reply_text("❌ Cancelled!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    elif text == "🆘 Help":
        await update.message.reply_text(
            "📚 *HELP*\n\n"
            "1. Choose Phone or Email\n"
            "2. Send your Phone/Email\n"
            "3. Send Password (6+ chars)\n"
            "4. Enter OTP code\n"
            "5. Account created!\n\n"
            "*Note:* This may take 1-2 minutes per account.",
            parse_mode='Markdown'
        )
        return CHOOSING_METHOD
    
    else:
        await update.message.reply_text(
            "❌ Please use the buttons below!",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📞 Phone Number"), KeyboardButton("📧 Email Address")],
                 [KeyboardButton("❌ Cancel"), KeyboardButton("🆘 Help")]], 
                resize_keyboard=True
            )
        )
        return CHOOSING_METHOD

async def input_value_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id != CHAT_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return ConversationHandler.END
    
    value = update.message.text.strip()
    method = user_data[user_id]['method']
    
    if method == 'phone':
        if not re.match(r'^\+?[0-9]{8,15}$', value):
            await update.message.reply_text("❌ Invalid phone! Example: `+919876543210`", parse_mode='Markdown')
            return INPUT_VALUE
    else:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            await update.message.reply_text("❌ Invalid email! Example: `user@gmail.com`", parse_mode='Markdown')
            return INPUT_VALUE
    
    user_data[user_id]['value'] = value
    
    await update.message.reply_text(
        f"✅ Saved: `{value}`\n\n🔑 *Send password (min 6 characters):*",
        parse_mode='Markdown'
    )
    return PASSWORD

async def password_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id != CHAT_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return ConversationHandler.END
    
    password = update.message.text.strip()
    
    if len(password) < 6:
        await update.message.reply_text("❌ Password too short! Minimum 6 characters required.", parse_mode='Markdown')
        return PASSWORD
    
    user_data[user_id]['password'] = password
    
    msg = await update.message.reply_text("📱 *Sending OTP request to Facebook...*\n⏳ Please wait 45-60 seconds...\n\n*Using real browser simulation...*", parse_mode='Markdown')
    
    success, message, driver = await create_facebook_account(
        user_data[user_id]['value'],
        password,
        user_data[user_id]['method'] == 'phone'
    )
    
    try:
        await msg.delete()
    except:
        pass
    
    if success:
        keyboard = [[KeyboardButton("🔄 Resend OTP")], [KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"✅ *OTP SENT!*\n\n"
            f"📱 Facebook sent verification code to your {user_data[user_id]['method']}\n\n"
            f"⏳ *Enter the verification code you received:*\n\n"
            f"💡 Code expires in 2 minutes\n\n"
            f"👇 *Wrong code? Click Resend OTP* 👇",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return VERIFICATION
    else:
        await update.message.reply_text(
            f"❌ *Failed to send OTP!*\n\n{message}\n\n"
            f"💡 Tips:\n"
            f"• Make sure your {user_data[user_id]['method']} is valid\n"
            f"• Check spam folder if using email\n"
            f"• Try again with /start\n"
            f"• Use a different {user_data[user_id]['method']}",
            parse_mode='Markdown'
        )
        return ConversationHandler.END

async def verification_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id != CHAT_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return ConversationHandler.END
    
    text = update.message.text.strip()
    
    if text == "🔄 Resend OTP":
        await update.message.reply_text("🔄 *Resending OTP...* Please wait...", parse_mode='Markdown')
        
        value = user_data[user_id]['value']
        password = user_data[user_id]['password']
        is_phone = user_data[user_id]['method'] == 'phone'
        
        success, message, driver = await create_facebook_account(value, password, is_phone)
        
        if success:
            await update.message.reply_text(
                f"✅ *OTP RESENT!*\n\nCheck your {user_data[user_id]['method']} for new code.\nEnter code below:",
                parse_mode='Markdown'
            )
            return VERIFICATION
        else:
            await update.message.reply_text(f"❌ Failed to resend: {message}\nUse /start", parse_mode='Markdown')
            return ConversationHandler.END
    
    if text == "❌ Cancel":
        user_data.pop(user_id, None)
        await update.message.reply_text("❌ Cancelled!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    if not text.isdigit() or len(text) < 4:
        await update.message.reply_text("❌ Invalid code! Send numbers only (4-6 digits):", parse_mode='Markdown')
        return VERIFICATION
    
    msg = await update.message.reply_text("🔄 *Verifying OTP and creating account...*\n⏳ Please wait 1-2 minutes...", parse_mode='Markdown')
    
    success, result = await verify_account(text)
    
    try:
        await msg.delete()
    except:
        pass
    
    if success:
        await update.message.reply_text(result, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text(
            "✅ *ACCOUNT CREATED SUCCESSFULLY!*\n\nUse /start to create another account.",
            parse_mode='Markdown'
        )
    else:
        keyboard = [[KeyboardButton("🔄 Resend OTP")], [KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"❌ *Verification Failed!*\n\n{result}\n\n👇 *Click Resend OTP to try again* 👇",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return VERIFICATION
    
    user_data.pop(user_id, None)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    user_data.pop(user_id, None)
    await update.message.reply_text("❌ *Cancelled!* Use /start", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    print("\n" + "="*60)
    print("🤖 FACEBOOK BOT - HARDCODED VERSION")
    print("="*60)
    print(f"Bot Token: {'Set' if BOT_TOKEN else 'Not Set'}")
    print(f"Chat ID: {CHAT_ID}")
    print("="*60 + "\n")
    
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Please set BOT_TOKEN!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, choosing_method_handler)],
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
