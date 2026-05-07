import os
import random
import time
import re
import asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import undetected_chromedriver as uc
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

# ====================== CONFIGURATION ======================
BOT_TOKEN = "8768410197:AAG8-HxVGEpwoFBAEOUtqm6_tivQh6Z873A"
CHAT_ID = "6162078955"
# ============================================================

# States
CHOOSING_METHOD, INPUT_VALUE, PASSWORD, VERIFICATION = range(4)

user_data = {}
temp_accounts = {}

first_names = ["Alan", "Murat", "Azad", "Necati", "Aaron", "Adam", "Alex", "John", "David", "Michael", "James", "Robert", "William", "Richard", "Thomas", "Christopher", "Daniel", "Matthew", "Andrew", "Joseph"]
last_names = ["Smith", "Jones", "Taylor", "Brown", "Wilson", "Davies", "Miller", "Johnson", "Williams", "Davis", "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez"]

def get_random_dob():
    return {
        'day': str(random.randint(1, 28)),
        'month': str(random.randint(1, 12)),
        'year': str(random.randint(1975, 2005))
    }

def random_delay(min_sec=0.5, max_sec=1.5):
    time.sleep(random.uniform(min_sec, max_sec))

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    return random.choice(user_agents)

async def create_facebook_account(login_value, password, is_phone=True):
    driver = None
    try:
        print(f"[+] Starting account creation for {login_value}")
        
        # Chrome options for Railway
        options = uc.ChromeOptions()
        
        # Critical options for Railway to work
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument(f'--user-agent={get_random_user_agent()}')
        options.add_argument('--lang=en-US,en;q=0.9')
        
        # Headless mode for Railway (important!)
        options.add_argument('--headless=new')
        
        # Create driver with specific Chrome version
        driver = uc.Chrome(
            options=options,
            version_main=120,
            use_subprocess=False
        )
        
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
            """
        })
        
        # Go to Facebook signup
        driver.get("https://www.facebook.com/r.php")
        random_delay(2, 4)
        
        wait = WebDriverWait(driver, 45)
        
        # Generate random user details
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        dob = get_random_dob()
        gender = random.choice(['2', '1'])
        
        # Fill first name
        first_name_field = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
        for c in first_name:
            first_name_field.send_keys(c)
            time.sleep(random.uniform(0.05, 0.1))
        random_delay(0.3, 0.6)
        
        # Fill last name
        last_name_field = driver.find_element(By.NAME, "lastname")
        for c in last_name:
            last_name_field.send_keys(c)
            time.sleep(random.uniform(0.05, 0.1))
        random_delay(0.3, 0.6)
        
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
            # Try to fill confirm email if exists
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
        
        # Select birthday
        day_select = Select(wait.until(EC.presence_of_element_located((By.ID, "day"))))
        day_select.select_by_value(dob['day'])
        random_delay(0.2, 0.4)
        
        month_select = Select(driver.find_element(By.ID, "month"))
        month_select.select_by_value(dob['month'])
        random_delay(0.2, 0.4)
        
        year_select = Select(driver.find_element(By.ID, "year"))
        year_select.select_by_value(dob['year'])
        random_delay(0.2, 0.4)
        
        # Select gender
        gender_radio = driver.find_element(By.XPATH, f"//input[@value='{gender}']")
        gender_radio.click()
        random_delay(0.5, 1)
        
        # Submit the form
        submit_btn = driver.find_element(By.NAME, "websubmit")
        submit_btn.click()
        
        print("[+] Form submitted successfully!")
        random_delay(8, 12)
        
        # Store account info
        account_info = {
            'first_name': first_name,
            'last_name': last_name,
            'dob': dob,
            'gender': gender,
            'login': login_value,
            'password': password,
            'is_phone': is_phone,
            'driver': driver
        }
        
        return True, "Account creation initiated! Waiting for verification...", account_info
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        return False, f"Error: {str(e)[:200]}", None

async def verify_account_with_driver(driver, verification_code, account_info):
    try:
        wait = WebDriverWait(driver, 30)
        
        # Wait for OTP input field
        time.sleep(3)
        
        # Try multiple selectors for OTP input
        code_input = None
        selectors = [
            "//input[@type='text' and @inputmode='numeric']",
            "//input[@autocomplete='one-time-code']",
            "//input[contains(@id, 'code')]",
            "//input[contains(@name, 'code')]",
            "//input[@type='text']"
        ]
        
        for selector in selectors:
            try:
                code_input = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                if code_input and code_input.is_displayed():
                    break
            except:
                continue
        
        if code_input:
            # Clear and enter code
            code_input.clear()
            for c in verification_code:
                code_input.send_keys(c)
                time.sleep(random.uniform(0.05, 0.1))
            random_delay(1, 2)
        
        # Find and click confirm button
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
        
        random_delay(10, 15)
        
        # Check current URL to see if account was created
        current_url = driver.current_url
        
        # Success conditions
        if "facebook.com" in current_url and "reg" not in current_url and "checkpoint" not in current_url:
            result = f"""
✅ ACCOUNT CREATED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━
{'📞 Phone' if account_info['is_phone'] else '📧 Email'}: {account_info['login']}
🔑 Password: {account_info['password']}
👤 Name: {account_info['first_name']} {account_info['last_name']}
🎂 DOB: {account_info['dob']['day']}/{account_info['dob']['month']}/{account_info['dob']['year']}
⚥ Gender: {'Male' if account_info['gender'] == '2' else 'Female'}
━━━━━━━━━━━━━━━━━━━━━━
"""
            return True, result
        elif "checkpoint" in current_url:
            return False, "Account needs additional verification. Check your email/phone."
        else:
            return False, "Wrong OTP or OTP expired. Please try again."
        
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return False, f"Error: {str(e)[:150]}"
    finally:
        try:
            driver.quit()
        except:
            pass

# ==================== TELEGRAM BOT HANDLERS ====================

async def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id != CHAT_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return ConversationHandler.END
    
    keyboard = [
        [KeyboardButton("📞 Phone Number"), KeyboardButton("📧 Email Address")],
        [KeyboardButton("❌ Cancel")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🤖 *FACEBOOK ACCOUNT CREATOR BOT* 🤖\n\n"
        "*Select signup method:*\n\n"
        "📞 Phone - OTP via SMS\n"
        "📧 Email - OTP via Email",
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
            "Example: `+919876543210`",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        return INPUT_VALUE
    
    elif text == "📧 Email Address":
        user_data[user_id] = {'method': 'email'}
        await update.message.reply_text(
            "📧 *Send email address*\n\n"
            "Example: `user@gmail.com`\n"
            "💡 Tip: Use temp mail like yandex.com",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        return INPUT_VALUE
    
    elif text == "❌ Cancel":
        await update.message.reply_text("❌ Cancelled!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    else:
        await update.message.reply_text("❌ Please use the buttons!")
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
        f"✅ *Saved:* `{value}`\n\n🔑 *Send password (min 6 characters):*",
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
        await update.message.reply_text("❌ Password too short! Minimum 6 characters required.")
        return PASSWORD
    
    user_data[user_id]['password'] = password
    
    msg = await update.message.reply_text(
        "🔄 *Creating Facebook account...*\n"
        "⏳ Please wait 30-45 seconds...\n\n"
        "✨ This will:\n"
        "• Fill registration form\n"
        "• Submit details\n"
        "• Request OTP verification\n\n"
        "_Please wait..._",
        parse_mode='Markdown'
    )
    
    # Create account
    success, message, account_info = await create_facebook_account(
        user_data[user_id]['value'],
        password,
        user_data[user_id]['method'] == 'phone'
    )
    
    await msg.delete()
    
    if success and account_info:
        # Store account info for verification
        temp_accounts[user_id] = account_info
        
        keyboard = [[KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"✅ *OTP SENT!*\n\n"
            f"📱 Facebook sent verification code to your {user_data[user_id]['method']}\n\n"
            f"⏳ *Enter the verification code you received:*\n\n"
            f"💡 Code expires in 2 minutes",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return VERIFICATION
    else:
        await update.message.reply_text(
            f"❌ *Failed!*\n\n{message}\n\n"
            f"💡 *Tips:*\n"
            f"• Check if your {user_data[user_id]['method']} is valid\n"
            f"• Try a different {user_data[user_id]['method']}\n"
            f"• Use /start to try again",
            parse_mode='Markdown'
        )
        return ConversationHandler.END

async def verification_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id != CHAT_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return ConversationHandler.END
    
    text = update.message.text.strip()
    
    if text == "❌ Cancel":
        # Clean up
        if user_id in temp_accounts:
            try:
                temp_accounts[user_id]['driver'].quit()
            except:
                pass
            del temp_accounts[user_id]
        user_data.pop(user_id, None)
        await update.message.reply_text("❌ Cancelled!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    if not text.isdigit() or len(text) < 4:
        await update.message.reply_text("❌ Invalid code! Send numbers only (4-6 digits):")
        return VERIFICATION
    
    if user_id not in temp_accounts:
        await update.message.reply_text("❌ Session expired! Use /start to begin again.")
        return ConversationHandler.END
    
    msg = await update.message.reply_text("🔄 *Verifying OTP and creating account...*\n⏳ Please wait...", parse_mode='Markdown')
    
    # Verify with the stored driver
    success, result = await verify_account_with_driver(
        temp_accounts[user_id]['driver'],
        text,
        temp_accounts[user_id]
    )
    
    await msg.delete()
    
    if success:
        await update.message.reply_text(result, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text(
            "✅ *Success!*\n\nUse /start to create another account.",
            parse_mode='Markdown'
        )
    else:
        keyboard = [[KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"❌ *Verification Failed!*\n\n{result}\n\nUse /start to try again.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # Cleanup
    if user_id in temp_accounts:
        del temp_accounts[user_id]
    user_data.pop(user_id, None)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id in temp_accounts:
        try:
            temp_accounts[user_id]['driver'].quit()
        except:
            pass
        del temp_accounts[user_id]
    user_data.pop(user_id, None)
    await update.message.reply_text("❌ *Cancelled!* Use /start", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    print("\n" + "="*60)
    print("🤖 FACEBOOK ACCOUNT CREATOR BOT - FIXED VERSION")
    print("="*60)
    print(f"Bot Token: {'✓ Loaded' if BOT_TOKEN else '✗ Missing'}")
    print(f"Chat ID: {CHAT_ID}")
    print("="*60)
    print("Bot is running...")
    print("="*60 + "\n")
    
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
