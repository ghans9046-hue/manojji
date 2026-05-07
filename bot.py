from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
import random
import time
import re
import os
import json
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

# ====================== CONFIGURATION ======================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8768410197:AAG8-HxVGEpwoFBAEOUtqm6_tivQh6Z873A")  # CHANGE THIS
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
        'year': str(random.randint(1970, 2000))
    }

def get_random_mouse_movement():
    """Generate random mouse movement script"""
    return f"""
    const moveMouse = () => {{
        const x = Math.random() * window.innerWidth;
        const y = Math.random() * window.innerHeight;
        const event = new MouseEvent('mousemove', {{
            view: window,
            bubbles: true,
            cancelable: true,
            clientX: x,
            clientY: y
        }});
        document.dispatchEvent(event);
    }};
    setInterval(moveMouse, {random.randint(3000, 7000)});
    """

def get_webgl_spoof_script():
    """Spoof WebGL fingerprint"""
    return """
    // Spoof WebGL Vendor
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Intel Inc.';
        }
        if (parameter === 37446) {
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter(parameter);
    };
    
    // Spoof Canvas fingerprint
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type) {
        if (type === 'image/png' && this.width === 220 && this.height === 220) {
            const context = this.getContext('2d');
            const imageData = context.getImageData(0, 0, this.width, this.height);
            for (let i = 0; i < imageData.data.length; i += 4) {
                imageData.data[i] = imageData.data[i] ^ 1;
            }
            context.putImageData(imageData, 0, 0);
        }
        return originalToDataURL.apply(this, arguments);
    };
    """

def get_plugins_spoof():
    """Spoof Chrome plugins"""
    return """
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            const plugins = [
                {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                {name: 'Native Client', filename: 'internal-nacl-plugin'}
            ];
            plugins.length = plugins.length;
            plugins.item = (i) => plugins[i];
            plugins.namedItem = (name) => plugins.find(p => p.name === name);
            plugins.refresh = () => {};
            return plugins;
        }
    });
    
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en', 'hi-IN']
    });
    """

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    return random.choice(user_agents)

async def send_otp_and_create_account(login_value, password, is_phone=True):
    """Send OTP and wait for verification"""
    driver = None
    try:
        print(f"[+] Starting for {login_value}")
        
        options = webdriver.ChromeOptions()
        
        # ============ IMPROVED STEALTH OPTIONS ============
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-site-isolation-trials')
        
        # Real browser - NOT headless
        # options.add_argument('--headless=new')  # COMMENTED - headless gets detected
        
        # Window size like real user
        options.add_argument(f'--window-size={random.randint(1200, 1600)},{random.randint(800, 900)}')
        
        # User Agent
        user_agent = get_random_user_agent()
        options.add_argument(f'--user-agent={user_agent}')
        
        # Disable automation flags
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Language
        options.add_argument('--lang=en-US,en,hi')
        
        # Hardware concurrency (like real CPU)
        options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
        
        # Disable notifications
        options.add_argument('--disable-notifications')
        
        # Real profile
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # ============ EXECUTE STEALTH SCRIPTS ============
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script(get_plugins_spoof())
        driver.execute_script(get_webgl_spoof_script())
        driver.execute_script(get_random_mouse_movement())
        
        # Spoof additional properties
        driver.execute_script("""
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0});
            Object.defineProperty( navigator, 'connection', {
                get: () => ({
                    effectiveType: '4g',
                    rtt: 50,
                    downlink: 10,
                    saveData: false
                })
            });
        """)
        
        # Random delay like human
        time.sleep(random.uniform(2, 4))
        
        driver.get("https://www.facebook.com/r.php")
        wait = WebDriverWait(driver, 45)
        time.sleep(random.uniform(3, 5))
        
        # Random details
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        dob = get_random_dob()
        gender = random.choice(['2', '1'])
        
        # Fill form with human-like typing
        first_name_field = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
        for char in first_name:
            first_name_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        last_name_field = driver.find_element(By.NAME, "lastname")
        for char in last_name:
            last_name_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        if is_phone:
            phone_field = driver.find_element(By.NAME, "reg_email__")
            for char in login_value:
                phone_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.1))
        else:
            email_field = driver.find_element(By.NAME, "reg_email__")
            for char in login_value:
                email_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.1))
            time.sleep(1)
            confirm_email_field = driver.find_element(By.NAME, "reg_email_confirmation__")
            for char in login_value:
                confirm_email_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.1))
        
        password_field = driver.find_element(By.NAME, "reg_passwd__")
        for char in password:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.1))
        
        # Birthday with random delay
        time.sleep(random.uniform(1, 2))
        day_select = Select(wait.until(EC.presence_of_element_located((By.ID, "day"))))
        day_select.select_by_value(dob['day'])
        time.sleep(random.uniform(0.5, 1))
        
        month_select = Select(driver.find_element(By.ID, "month"))
        month_select.select_by_value(dob['month'])
        time.sleep(random.uniform(0.5, 1))
        
        year_select = Select(driver.find_element(By.ID, "year"))
        year_select.select_by_value(dob['year'])
        time.sleep(random.uniform(0.5, 1))
        
        # Gender
        gender_radio = driver.find_element(By.XPATH, f"//input[@value='{gender}']")
        gender_radio.click()
        
        # Random scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 200);")
        time.sleep(random.uniform(1, 2))
        
        # Submit
        submit_btn = driver.find_element(By.NAME, "websubmit")
        submit_btn.click()
        
        print("[+] Form submitted, waiting for OTP page...")
        
        # Wait longer for OTP page
        time.sleep(random.uniform(10, 15))
        
        # Store everything
        user_data['temp_driver'] = driver
        user_data['temp_first_name'] = first_name
        user_data['temp_last_name'] = last_name
        user_data['temp_dob'] = dob
        user_data['temp_gender'] = gender
        user_data['temp_login'] = login_value
        user_data['temp_pass'] = password
        user_data['temp_is_phone'] = is_phone
        
        return True, "OTP sent successfully! Check your phone/email."
        
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
        wait = WebDriverWait(driver, 45)
        
        # Try multiple selectors for OTP input
        code_input = None
        selectors = [
            (By.XPATH, "//input[@type='text' and contains(@id, 'code')]"),
            (By.XPATH, "//input[@type='text' and contains(@name, 'code')]"),
            (By.XPATH, "//input[@autocomplete='one-time-code']"),
            (By.XPATH, "//input[@inputmode='numeric']"),
            (By.XPATH, "//div[contains(text(), 'code')]//following::input[1]"),
            (By.CSS_SELECTOR, "input[type='text']"),
        ]
        
        for selector_type, selector in selectors:
            try:
                code_input = wait.until(EC.presence_of_element_located((selector_type, selector)))
                if code_input:
                    break
            except:
                continue
        
        if code_input:
            code_input.clear()
            time.sleep(random.uniform(0.5, 1))
            for char in verification_code:
                code_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            time.sleep(2)
        
        # Try multiple submit button selectors
        confirm_btn = None
        button_selectors = [
            (By.XPATH, "//button[contains(text(), 'Confirm')]"),
            (By.XPATH, "//button[contains(text(), 'Verify')]"),
            (By.XPATH, "//button[contains(text(), 'Continue')]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.XPATH, "//button[contains(@class, 'confirm')]"),
        ]
        
        for selector_type, selector in button_selectors:
            try:
                confirm_btn = driver.find_element(selector_type, selector)
                if confirm_btn:
                    break
            except:
                continue
        
        if confirm_btn:
            confirm_btn.click()
            print("[+] Confirm button clicked")
        
        # Wait for account creation
        time.sleep(random.uniform(15, 20))
        
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
        if "facebook.com" in current_url and "reg" not in current_url and "confirm" not in current_url.lower():
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

⚠️ WARMUP TIPS:
- Don't add friends immediately
- Wait 48 hours before posting
- Use like a normal user
"""
            return True, result
        else:
            return False, "Verification failed! Wrong OTP or OTP expired. Try again."
        
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return False, f"Error: {str(e)[:150]}"
    finally:
        if driver:
            driver.quit()
            print("[+] Browser closed")
            for key in ['temp_driver', 'temp_first_name', 'temp_last_name', 'temp_dob', 'temp_gender', 'temp_login', 'temp_pass', 'temp_is_phone']:
                user_data.pop(key, None)

# ==================== TELEGRAM BOT HANDLERS (Same as before) ====================

async def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id != CHAT_ID:
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
            "5. Account created!\n\n"
            "⚠️ *NOTE:* Not headless - browser will open!",
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
        f"✅ Saved: `{value}`\n\n🔑 *Send password (min 8 chars):*",
        parse_mode='Markdown'
    )
    return PASSWORD

async def password_handler(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    password = update.message.text.strip()
    
    if len(password) < 8:
        await update.message.reply_text("❌ Password too short! (min 8 chars)", parse_mode='Markdown')
        return PASSWORD
    
    user_data[user_id]['password'] = password
    
    msg = await update.message.reply_text("📱 *Sending OTP request to Facebook...*\n⏳ Please wait 45 seconds...\n\n⚠️ *Browser will open - don't close!*", parse_mode='Markdown')
    
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
        await update.message.reply_text("🔄 Resending OTP... Please wait...\n⚠️ This will restart the process!")
        # For resend, restart from beginning with same credentials
        success, message = await send_otp_and_create_account(
            user_data[user_id]['value'],
            user_data[user_id]['password'],
            user_data[user_id]['type'] == 'phone'
        )
        if success:
            await update.message.reply_text("✅ *OTP RESENT!*\n\nEnter code:", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ *Resend failed!*\n{message}", parse_mode='Markdown')
        return VERIFICATION
    
    if text == "❌ Cancel":
        user_data.pop(user_id, None)
        await update.message.reply_text("❌ Cancelled! Use /start")
        return ConversationHandler.END
    
    if not text.isdigit() or len(text) < 4:
        await update.message.reply_text("❌ Invalid code! Send numbers only:", parse_mode='Markdown')
        return VERIFICATION
    
    msg = await update.message.reply_text("🔄 *Verifying OTP and creating account...*\n⏳ Please wait 2 minutes...", parse_mode='Markdown')
    
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
    print("🤖 FACEBOOK BOT STARTED (REAL BROWSER MODE)")
    print("⚠️ Headless disabled - browser window will open")
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
