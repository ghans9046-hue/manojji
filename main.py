#DECODED BY NETZ - YANDEX VERSION (WORKING)
import os
import sys
import re
import random
import string
import time
import json
import platform
import requests
import subprocess
from typing import Set, Optional
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from faker import Faker
import pyotp
import logging

from urllib.request import Request, urlopen

# Setup logging
logging.basicConfig(level=logging.INFO, filename="app.log", format="%(asctime)s - %(levelname)s - %(message)s")

# ANSI color codes
W = '\033[97m'
G = '\033[92m'
R = '\033[91m'
V = '\033[1;34m'
B = '\033[1;30m'
RESET = '\033[0m'

ua = UserAgent()

# YANDEX CREDENTIALS
YANDEX_EMAIL = "jerryxd@yandex.com"
YANDEX_PASS = "kshxbeousfpcbxgq"

def generate_yandex_email(base_email=YANDEX_EMAIL, account_name=None):
    if account_name is None:
        account_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    local_part = base_email.split('@')[0]
    domain = base_email.split('@')[1]
    return f"{local_part}+{account_name}@{domain}"

def save_to_file(data: str, file_path: str):
    full_path = file_path
    os.makedirs(os.path.dirname(full_path) or ".", exist_ok=True)
    with open(full_path, "a", encoding="utf-8") as f:
        f.write(data + "\n")

def install_dependencies():
    try:
        import pyotp
    except ImportError:
        logging.warning("pyotp not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyotp"])
        except Exception as e:
            logging.error(f"Failed to install pyotp: {e}")
            print(f"{R}Failed to install pyotp: {e}{W}")
            sys.exit(1)

def clear_screen():
    os.system('cls' if platform.system().lower() == 'windows' else 'clear')

# Device information
try:
    android_version = subprocess.check_output('getprop ro.build.version.release', shell=True).decode('utf-8').strip()
    model = subprocess.check_output('getprop ro.product.model', shell=True).decode('utf-8').strip()
    build = subprocess.check_output('getprop ro.build.id', shell=True).decode('utf-8').strip()
    fbmf = subprocess.check_output('getprop ro.product.manufacturer', shell=True).decode('utf-8').strip()
    fbbd = subprocess.check_output('getprop ro.product.brand', shell=True).decode('utf-8').strip()
    fbca = subprocess.check_output('getprop ro.product.cpu.abilist', shell=True).decode('utf-8').replace(',', ':').strip()
    fbdm = f"{{density=2.25,height={subprocess.check_output('getprop ro.hwui.text_large_cache_height', shell=True).decode('utf-8').strip()},width={subprocess.check_output('getprop ro.hwui.text_large_cache_width', shell=True).decode('utf-8').strip()}}}"
    try:
        fbcr = subprocess.check_output('getprop gsm.operator.alpha', shell=True).decode('utf-8').split(',')[0].strip()
    except:
        fbcr = 'ZONG'
except:
    android_version, model, build, fbmf, fbbd, fbca, fbdm, fbcr = '10', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'arm64-v8a', '{density=2.25,height=720,width=1280}', 'ZONG'

device = {
    'android_version': android_version,
    'model': model,
    'build': build,
    'fblc': 'en_US',
    'fbmf': fbmf,
    'fbbd': fbbd,
    'fbdv': model,
    'fbsv': android_version,
    'fbca': fbca,
    'fbdm': fbdm
}

def ugenX():
    ualist = [ua.random for _ in range(50)]
    return str(random.choice(ualist))

ugen = []
for xd in range(500):
    rr = random.randint
    build_b = random.choice(["001","002","003","011","012","014","015","020","021","022","023","024"])
    bl_typ = random.choice(["TKQ1","SKQ1","TP1A","RKQ1","SP1A","RP1A","PPR1","QP1A"])
    oppo = random.choice(["CPH2461","CPH2451","PCGM00","PBBM00","PFZM10","PGGM10"])
    redmi = random.choice(["2211133G","M2004J19C","22041219I","Redmi Note 7","Redmi Note 8"])
    infinix = random.choice(["Infinix X669C","Infinix X6823","Infinix X676C"])
    
    um2 = f"Mozilla/5.0 (Linux; Android {str(rr(6,12))}; {oppo} Build/{bl_typ}.{str(rr(120000,220000))}.{build_b}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{str(rr(80,114))}.0.{str(rr(4200,5400))}.{str(rr(70,150))} Mobile Safari/537.36"
    um1 = f"Mozilla/5.0 (Linux; Android {str(rr(6,12))}; {redmi} Build/{bl_typ}.{str(rr(120000,220000))}.{build_b}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{str(rr(80,114))}.0.{str(rr(4200,5400))}.{str(rr(70,150))} Mobile Safari/537.36"
    um3 = f"Mozilla/5.0 (Linux; Android {str(rr(6,12))}; {infinix}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{str(rr(100,114))}.0.{str(rr(4900,5700))}.{str(rr(70,150))} Mobile Safari/537.36"
    
    ugen.append(um2)
    ugen.append(um1)
    ugen.append(um3)

for generate in range(100):
    a = random.randrange(1, 9)
    b = random.randrange(1, 9)
    c = random.randrange(73, 100)
    d = random.randrange(4200, 4900)
    e = random.randrange(40, 150)
    uaku = f'Mozilla/5.0 (Linux; Android {a}.{b}; Pixel {b}) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{c}.0.{d}.{e} Mobile Safari/537.36'
    ugen.append(uaku)

# Names
first_names_male = [
'Juan', 'Jose', 'Miguel', 'Gabriel', 'Rafael', 'Antonio', 'Carlos', 'Luis',
'Marco', 'Paolo', 'Angelo', 'Joshua', 'Christian', 'Mark', 'John', 'James',
'Daniel', 'David', 'Michael', 'Kenneth', 'Ryan', 'Kevin', 'Justin', 'Patrick',
'Paul', 'Francis', 'Anthony', 'Carlos', 'Rafael', 'Samuel', 'Sebastian'
]

first_names_female = [
'Maria', 'Ana', 'Sofia', 'Isabella', 'Gabriela', 'Valentina', 'Camila',
'Angelica', 'Nicole', 'Michelle', 'Christine', 'Sarah', 'Jessica',
'Andrea', 'Patricia', 'Jennifer', 'Karen', 'Ashley', 'Jasmine', 'Princess',
'Angel', 'Joyce', 'Kristine', 'Diane', 'Joanna', 'Carmela', 'Isabel'
]

surnames = [
'Reyes', 'Santos', 'Cruz', 'Bautista', 'Garcia', 'Flores', 'Gonzales',
'Martinez', 'Ramos', 'Mendoza', 'Rivera', 'Torres', 'Fernandez', 'Lopez',
'Castillo', 'Aquino', 'Villanueva', 'Santiago', 'Dela Cruz', 'Perez',
'Castro', 'Mercado', 'Domingo', 'Gutierrez', 'Ramirez', 'Valdez'
]

rpw_first_names = [
'Luna', 'Aurora', 'Mystic', 'Crystal', 'Sapphire', 'Scarlet', 'Violet',
'Rose', 'Athena', 'Venus', 'Nova', 'Stella', 'Serena', 'Raven', 'Jade'
]

rpw_surnames = [
'Shadow', 'Dark', 'Light', 'Star', 'Moon', 'Sun', 'Sky', 'Night', 'Dawn',
'Storm', 'Frost', 'Fire', 'Draven', 'Wraith', 'Hale', 'Voss', 'Lockhart'
]

def get_bd_name():
    first = random.choice(first_names_male + first_names_female)
    last = random.choice(surnames)
    return first, last

def get_rpw_name():
    return random.choice(rpw_first_names), random.choice(rpw_surnames)

def get_pass():
    name_part = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 7)))
    name_part = name_part.capitalize() if random.choice([True, False]) else name_part.lower()
    symbol_part = ''.join(random.choices('!@#$%^&*()_+=', k=random.randint(2, 3)))
    digit_part = ''.join(random.choices(string.digits, k=random.randint(2, 4)))
    parts = [name_part, symbol_part, digit_part]
    random.shuffle(parts)
    return ''.join(parts)

def extractor(data):
    soup = BeautifulSoup(data, "html.parser")
    data_dict = {}
    for inputs in soup.find_all("input"):
        name = inputs.get("name")
        value = inputs.get("value")
        if name:
            data_dict[name] = value
    return data_dict

def register_account_with_otp(ses, name_option="1", gender_option="3", custom_pass=None):
    try:
        # Get registration page
        response = ses.get("https://mbasic.facebook.com/reg", timeout=20)
        form = extractor(response.text)
        
        if not form.get("lsd") and not form.get("fb_dtsg"):
            time.sleep(2)
            response = ses.get("https://mbasic.facebook.com/reg", timeout=20)
            form = extractor(response.text)
            if not form.get("lsd"):
                return None
        
        # Generate name
        if name_option == "2":
            firstname, lastname = get_rpw_name()
        else:
            if gender_option == "1":
                firstname = random.choice(first_names_male)
            elif gender_option == "2":
                firstname = random.choice(first_names_female)
            else:
                firstname = random.choice(first_names_male + first_names_female)
            lastname = random.choice(surnames)
        
        # Gender: 1=Male, 2=Female in form
        if gender_option == "1":
            fb_sex = "1"
        elif gender_option == "2":
            fb_sex = "2"
        else:
            fb_sex = random.choice(["1", "2"])
        
        # Generate email
        account_tag = f"{firstname.lower()}{random.randint(100,999)}"
        email = generate_yandex_email(YANDEX_EMAIL, account_tag)
        pww = custom_pass if custom_pass else get_pass()
        
        # Prepare payload
        payload = {
            'lsd': form.get("lsd", ""),
            'jazoest': form.get("jazoest", ""),
            'm_ts': form.get("m_ts", ""),
            'li': form.get("li", ""),
            'firstname': firstname,
            'lastname': lastname,
            'reg_email__': email,
            'reg_email_conf__': email,
            'birthday_day': str(random.randint(15, 25)),
            'birthday_month': str(random.randint(5, 10)),
            'birthday_year': str(random.randint(1985, 1995)),
            'sex': fb_sex,
            'password': pww,
            'did_submit': '1',
        }
        
        headers = {
            "Host": "mbasic.facebook.com",
            "User-Agent": ugenX(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://mbasic.facebook.com",
            "Referer": "https://mbasic.facebook.com/reg/",
            "Connection": "keep-alive",
        }
        
        # Submit registration
        reg_response = ses.post("https://mbasic.facebook.com/reg/", data=payload, headers=headers, timeout=30)
        
        # Check cookies for success
        cookies = ses.cookies.get_dict()
        
        if "c_user" in cookies:
            # Success! Account created
            cookie_string = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return {
                "name": f"{firstname} {lastname}",
                "email": email,
                "password": pww,
                "uid": cookies["c_user"],
                "cookies": cookie_string,
                "session": ses,
                "needs_otp": False
            }
        
        # Check if confirmation needed
        response_text = reg_response.text
        response_url = reg_response.url
        
        if "checkpoint" in response_url or "confirm" in response_url.lower():
            return {
                "name": f"{firstname} {lastname}",
                "email": email,
                "password": pww,
                "uid": None,
                "needs_otp": True,
                "session": ses
            }
        
        # Check for error messages
        if "blocked" in response_text.lower() or "sorry" in response_text.lower():
            logging.warning(f"Registration blocked: {response_text[:200]}")
            return None
        
        return None
        
    except Exception as e:
        logging.error(f"Registration error: {e}")
        return None

def submit_otp(ses, otp_code):
    try:
        # Try to find confirmation form
        response = ses.get("https://mbasic.facebook.com/checkpoint/", timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for form with code input
        form = soup.find('form')
        if not form:
            return False
        
        action = form.get('action', '')
        if not action.startswith('http'):
            action = 'https://mbasic.facebook.com' + action
        
        fields = {}
        for inp in form.find_all('input'):
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                fields[name] = value
        
        # Set OTP code
        for key in ['code', 'confirm_code', 'approvals_code', 'otp']:
            if key in fields:
                fields[key] = otp_code
                break
        else:
            fields['code'] = otp_code
        
        fields['submit'] = 'Submit'
        
        confirm_res = ses.post(action, data=fields, timeout=15)
        cookies = ses.cookies.get_dict()
        
        return 'c_user' in cookies
        
    except Exception as e:
        logging.error(f"OTP submission error: {e}")
        return False
