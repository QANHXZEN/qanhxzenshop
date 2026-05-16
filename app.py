from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json, os, secrets, string, requests, smtplib, random as rnd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from time import time

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(32)

# ===== CONFIG =====
BOT_TOKEN = "8466851320:AAGc77X4DnPQRNkw7rVUhlpJVIcBlOcSlDA"
CHAT_ID = "8588555065"
OWNER_ID = 8588555065
LINK4M_API_KEY = "65c47d157fbdff4d79625e57"
RENDER_URL = "https://qanhxzenshop.onrender.com"

EMAIL_SENDER = "qanhxzenshopfeedback@gmail.com"
EMAIL_PASSWORD = "lmyj wgyp tfzo qxkj"

# ===== DATABASE FILES =====
USERS_FILE = "/tmp/users_db.json"
KEYS_FILE = "/tmp/keys_db.json"
TRANSACTIONS_FILE = "/tmp/transactions_db.json"
PENDING_FILE = "/tmp/pending_db.json"
VERIFY_FILE = "/tmp/verify_db.json"

def load_json(filename, default={}):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except: pass
    return default

def save_json(filename, data):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, ensure_ascii=False)
    except: pass

# Load data từ file
users_db = load_json(USERS_FILE, {})
keys_db = load_json(KEYS_FILE, {"free_keys": {}, "licenses": {}, "used_keys": {}, "keys_history": []})
transactions_db = load_json(TRANSACTIONS_FILE, [])
pending_registrations = load_json(PENDING_FILE, {})
pending_verify = load_json(VERIFY_FILE, {})

def save_all_data():
    save_json(USERS_FILE, users_db)
    save_json(KEYS_FILE, keys_db)
    save_json(TRANSACTIONS_FILE, transactions_db)
    save_json(PENDING_FILE, pending_registrations)
    save_json(VERIFY_FILE, pending_verify)

def generate_key():
    c = string.ascii_uppercase + string.digits
    r = lambda l: ''.join(secrets.choice(c) for _ in range(l))
    return f"QANH-{r(10)}-{r(10)}-{r(10)}-{r(5)}"

def generate_verify_code():
    return ''.join([str(rnd.randint(0, 9)) for _ in range(6)])

def save_key_local(key, key_type, email=""):
    """LƯU KEY VÀO DATABASE CỦA WEB"""
    today = datetime.now().strftime("%Y-%m-%d")
    if key_type in ['free', 'free_verified']:
        expire = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        keys_db.setdefault("free_keys", {})[key] = {
            "created_by": OWNER_ID,
            "expire": expire,
            "email": email,
            "date": today,
            "verified": True,
            "created_at": datetime.now().isoformat()
        }
    elif key_type == 'week':
        expire = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        keys_db.setdefault("licenses", {})[key] = {
            "created_by": OWNER_ID,
            "expire_date": expire,
            "email": email,
            "created_at": datetime.now().isoformat()
        }
    elif key_type == 'month':
        expire = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        keys_db.setdefault("licenses", {})[key] = {
            "created_by": OWNER_ID,
            "expire_date": expire,
            "email": email,
            "created_at": datetime.now().isoformat()
        }
    elif key_type == 'forever':
        keys_db.setdefault("licenses", {})[key] = {
            "created_by": OWNER_ID,
            "expire_date": None,
            "email": email,
            "created_at": datetime.now().isoformat()
        }
    
    keys_db.setdefault("keys_history", []).append({
        "key": key,
        "type": key_type,
        "email": email,
        "created_at": datetime.now().isoformat()
    })
    save_all_data()

def save_transaction(email, trans_type, amount, key="", status="success"):
    """LƯU LỊCH SỬ GIAO DỊCH"""
    transactions_db.append({
        "email": email,
        "type": trans_type,
        "amount": amount,
        "key": key,
        "status": status,
        "time": datetime.now().isoformat()
    })
    if len(transactions_db) > 1000:
        transactions_db.pop(0)
    save_all_data()

def send_key_to_bot(key, key_type):
    """Gửi lệnh /taokey cho bot Telegram"""
    try:
        cmds = {'free': 'free 1ngay', 'week': '1w', 'month': 'vip 1thang', 'forever': 'vip vinhvien'}
        cmd = cmds.get(key_type, 'free 1ngay')
        
        # Gửi message CHỨA LỆNH /taokey
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        res = requests.post(url, json={
            'chat_id': CHAT_ID,
            'text': f'/taokey {cmd}'
        }, timeout=10)
        
        print(f"Bot response: {res.json()}")
        return True
    except Exception as e:
        print(f"Lỗi gửi key: {e}")
        return False

def send_verification_email(to_email, code):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = "QANH SHOP - Mã Xác Minh Email"
        body = f"""
        <div style="background:linear-gradient(135deg,#0a0a1a,#1a1a3e);color:#fff;padding:35px;font-family:Arial;text-align:center;border-radius:20px">
            <h2 style="color:#6C5CE7;font-size:26px">QANH SHOP</h2>
            <p style="color:#ccc">Mã xác minh của bạn:</p>
            <div style="font-size:38px;color:#00D68F;background:#000;padding:18px;border-radius:12px;margin:20px;letter-spacing:8px;border:2px dashed #00D68F">{code}</div>
            <p style="color:#FF6B6B">⚠️ Mã hết hạn sau 1 phút</p>
        </div>
        """
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# ===== UI TEMPLATES =====
def get_login_html():
    return r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đăng Nhập - QANH SHOP</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root{--primary:#6C5CE7;--primary-dark:#5A4BD1;--gold:#FFD700;--green:#00D68F;--red:#FF6B6B;--blue:#45AAF2;--bg:#0F0F1A;--card:#1A1A2E;--card2:#16213E;--text:#E0E0E0;--muted:#8E8E9A}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Plus Jakarta Sans',Arial,sans-serif;color:var(--text);min-height:100vh;background:var(--bg);display:flex;justify-content:center;align-items:center;padding:20px}
        .bg-shapes{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;overflow:hidden;pointer-events:none}
        .bg-shape{position:absolute;border-radius:50%;opacity:0.04}
        .bg-shape:nth-child(1){width:600px;height:600px;background:var(--primary);top:-200px;right:-200px;animation:float1 20s infinite}
        .bg-shape:nth-child(2){width:400px;height:400px;background:var(--blue);bottom:-100px;left:-100px;animation:float2 18s infinite}
        .bg-shape:nth-child(3){width:300px;height:300px;background:var(--gold);top:40%;left:50%;animation:float3 22s infinite}
        @keyframes float1{0%,100%{transform:translate(0,0)rotate(0deg)}50%{transform:translate(50px,-50px)rotate(10deg)}}
        @keyframes float2{0%,100%{transform:translate(0,0)rotate(0deg)}50%{transform:translate(-40px,40px)rotate(-10deg)}}
        @keyframes float3{0%,100%{transform:translate(0,0)scale(1)}50%{transform:translate(-30px,-30px)scale(1.2)}}
        .container{position:relative;z-index:1;background:var(--card);border-radius:28px;padding:45px 35px;max-width:440px;width:100%;border:1px solid rgba(255,255,255,0.06);box-shadow:0 25px 80px rgba(0,0,0,0.5);animation:slideUp 0.6s}
        @keyframes slideUp{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:translateY(0)}}
        .logo-icon{width:65px;height:65px;background:linear-gradient(135deg,var(--primary),var(--primary-dark));border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:32px;margin:0 auto 20px;box-shadow:0 15px 35px rgba(108,92,231,0.3)}
        .title{font-size:26px;font-weight:800;color:#fff;text-align:center;margin-bottom:5px}
        .subtitle{color:var(--muted);text-align:center;margin-bottom:30px;font-size:14px}
        .input-group{margin-bottom:18px}
        .input-group label{display:block;color:var(--muted);margin-bottom:8px;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1.5px}
        .input-wrapper input{width:100%;padding:15px 18px;border-radius:14px;border:2px solid rgba(255,255,255,0.06);background:var(--card2);color:#fff;font-size:15px;font-weight:500;transition:0.3s;font-family:'Plus Jakarta Sans',sans-serif}
        .input-wrapper input:focus{border-color:var(--primary);outline:none;box-shadow:0 0 20px rgba(108,92,231,0.15);background:#1E1E3A}
        .captcha-box{background:rgba(108,92,231,0.04);border:1px dashed rgba(108,92,231,0.2);border-radius:14px;padding:18px;text-align:center;margin:18px 0}
        .captcha-text{font-size:30px;font-weight:800;background:linear-gradient(135deg,var(--primary),var(--blue));-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:6px;margin:8px 0;user-select:none}
        .captcha-box input{width:100%;padding:12px;border-radius:10px;border:2px solid rgba(255,255,255,0.08);background:#000;color:#fff;text-align:center;font-size:18px;letter-spacing:5px;font-weight:600}
        .refresh-link{color:var(--blue);cursor:pointer;font-size:12px;margin-top:8px;display:inline-block}
        .btn{display:block;width:100%;padding:16px;border:none;border-radius:14px;font-size:16px;font-weight:700;cursor:pointer;text-align:center;transition:0.3s;font-family:'Plus Jakarta Sans',sans-serif}
        .btn-primary{background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;box-shadow:0 10px 30px rgba(108,92,231,0.35)}
        .btn-primary:hover{transform:translateY(-2px);box-shadow:0 15px 40px rgba(108,92,231,0.45)}
        .btn-primary:disabled{opacity:0.5;cursor:not-allowed;transform:none}
        .link-text{color:var(--muted);text-align:center;margin-top:22px;font-size:14px}
        .link-text a{color:var(--primary);cursor:pointer;text-decoration:none;font-weight:600}
        .alert{background:rgba(255,107,107,0.08);border:1px solid rgba(255,107,107,0.2);border-radius:12px;padding:12px;margin:10px 0;color:var(--red);font-size:13px;text-align:center}
        .success-box{background:rgba(0,214,143,0.08);border:1px solid rgba(0,214,143,0.2);border-radius:12px;padding:12px;margin:10px 0;color:var(--green);font-size:13px}
        .hidden{display:none!important}
        .loading{display:inline-block;width:20px;height:20px;border:2px solid rgba(255,255,255,0.2);border-top:2px solid #fff;border-radius:50%;animation:spin 0.7s linear infinite;margin-right:8px;vertical-align:middle}
        @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
        .timer-text{color:#ff9f43;font-size:13px;text-align:center;margin-top:10px}
    </style>
</head>
<body>
<div class="bg-shapes"><div class="bg-shape"></div><div class="bg-shape"></div><div class="bg-shape"></div></div>

<div id="loginContainer" class="container">
    <div class="logo-icon">⚡</div>
    <div class="title">Chào Mừng Trở Lại</div>
    <p class="subtitle">Đăng nhập để tiếp tục sử dụng dịch vụ</p>
    <div id="loginForm">
        <div class="input-group"><label>Email hoặc tên tài khoản</label><div class="input-wrapper"><input type="text" id="loginUser" placeholder="Nhập email hoặc tên tài khoản..." autocomplete="off"></div></div>
        <div class="input-group"><label>Mật khẩu</label><div class="input-wrapper"><input type="password" id="loginPass" placeholder="Nhập mật khẩu..." autocomplete="off"></div></div>
        <div class="captcha-box"><p style="color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:2px">Xác minh bảo mật</p><div class="captcha-text" id="captchaText"></div><input type="text" id="captchaInput" placeholder="Nhập mã captcha..." maxlength="5" autocomplete="off"><span class="refresh-link" onclick="generateCaptcha()">🔄 Đổi mã khác</span></div>
        <button class="btn btn-primary" id="btnLogin" onclick="doLogin()">ĐĂNG NHẬP</button>
        <div id="loginMsg"></div>
        <p class="link-text">Chưa có tài khoản? <a onclick="showRegister()">Tạo tài khoản mới</a></p>
    </div>
</div>

<div id="registerContainer" class="container hidden">
    <div class="logo-icon">🚀</div>
    <div class="title">Tạo Tài Khoản</div>
    <p class="subtitle">Đăng ký để nhận key và nạp tiền</p>
    <div id="registerForm">
        <div class="input-group"><label>Email</label><div class="input-wrapper"><input type="email" id="regEmail" placeholder="Nhập email..." autocomplete="off"></div></div>
        <div class="input-group"><label>Tên tài khoản</label><div class="input-wrapper"><input type="text" id="regUsername" placeholder="Nhập tên tài khoản..." autocomplete="off"></div></div>
        <div class="input-group"><label>Mật khẩu</label><div class="input-wrapper"><input type="password" id="regPass" placeholder="Ít nhất 6 ký tự..." autocomplete="off"></div></div>
        <div class="input-group"><label>Nhập lại mật khẩu</label><div class="input-wrapper"><input type="password" id="regPass2" placeholder="Nhập lại mật khẩu..." autocomplete="off"></div></div>
        <div class="input-group"><label>Số điện thoại <span style="color:var(--muted);font-size:10px">(không bắt buộc)</span></label><div class="input-wrapper"><input type="tel" id="regPhone" placeholder="Nhập số điện thoại..." autocomplete="off"></div></div>
        <div class="captcha-box"><p style="color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:2px">Xác minh bảo mật</p><div class="captcha-text" id="captchaTextReg"></div><input type="text" id="captchaInputReg" placeholder="Nhập mã captcha..." maxlength="5" autocomplete="off"><span class="refresh-link" onclick="generateCaptchaReg()">🔄 Đổi mã khác</span></div>
        <button class="btn btn-primary" id="btnRegister" onclick="doRegister()">TẠO TÀI KHOẢN</button>
        <div id="regMsg"></div>
        <p class="link-text">Đã có tài khoản? <a onclick="showLogin()">Đăng nhập ngay</a></p>
    </div>
    <div id="verifyEmailForm" class="hidden">
        <div style="font-size:55px;text-align:center;margin:10px 0">📧</div>
        <div class="title" style="font-size:20px">Xác Minh Email</div>
        <p style="color:var(--muted);text-align:center;margin:15px 0">Mã <b style="color:var(--primary)">6 chữ số</b> đã gửi đến:<br><b style="color:var(--blue)" id="verifyEmailDisplay"></b></p>
        <div class="input-wrapper"><input type="text" id="verifyCode" placeholder="------" maxlength="6" autocomplete="off" style="text-align:center;font-size:24px;letter-spacing:8px;font-weight:700"></div>
        <p class="timer-text" id="verifyTimer">⏰ Còn 60 giây</p>
        <button class="btn btn-primary" id="btnVerify" onclick="verifyEmail()" style="margin-top:15px">XÁC NHẬN</button>
        <button class="btn" style="background:rgba(255,255,255,0.05);color:var(--muted);margin-top:8px;font-size:14px" onclick="resendCode()">📧 GỬI LẠI MÃ</button>
        <div id="verifyMsg"></div>
        <p class="link-text"><a onclick="showLogin()">← Quay lại</a></p>
    </div>
</div>

<script>
var API=window.location.origin;
var captchaAnswer='',captchaAnswerReg='',pendingEmail='';
var verifyTimerInterval=null,verifySeconds=60;
function generateCaptcha(){var c='ABCDEFGHJKLMNPQRSTUVWXYZ23456789',code='';for(var i=0;i<5;i++)code+=c[Math.floor(Math.random()*c.length)];captchaAnswer=code;document.getElementById('captchaText').innerText=code;document.getElementById('captchaInput').value='';}
function generateCaptchaReg(){var c='ABCDEFGHJKLMNPQRSTUVWXYZ23456789',code='';for(var i=0;i<5;i++)code+=c[Math.floor(Math.random()*c.length)];captchaAnswerReg=code;document.getElementById('captchaTextReg').innerText=code;document.getElementById('captchaInputReg').value='';}
function showRegister(){document.getElementById('loginContainer').classList.add('hidden');document.getElementById('registerContainer').classList.remove('hidden');document.getElementById('registerForm').classList.remove('hidden');document.getElementById('verifyEmailForm').classList.add('hidden');if(verifyTimerInterval)clearInterval(verifyTimerInterval);generateCaptchaReg();}
function showLogin(){document.getElementById('registerContainer').classList.add('hidden');document.getElementById('loginContainer').classList.remove('hidden');document.getElementById('verifyEmailForm').classList.add('hidden');if(verifyTimerInterval)clearInterval(verifyTimerInterval);generateCaptcha();}
function startVerifyTimer(){verifySeconds=60;updateTimer();if(verifyTimerInterval)clearInterval(verifyTimerInterval);verifyTimerInterval=setInterval(function(){verifySeconds--;updateTimer();if(verifySeconds<=0){clearInterval(verifyTimerInterval);document.getElementById('verifyTimer').innerHTML='<span style="color:#f44">❌ Mã hết hạn!</span>';document.getElementById('btnVerify').disabled=true;}},1000);}
function updateTimer(){var el=document.getElementById('verifyTimer');if(verifySeconds>10)el.innerHTML='⏰ Còn <b>'+verifySeconds+'</b> giây';else el.innerHTML='⚠️ Còn <b style="color:#ff9f43">'+verifySeconds+'</b> giây';}
function doLogin(){var user=document.getElementById('loginUser').value.trim(),pass=document.getElementById('loginPass').value.trim(),captcha=document.getElementById('captchaInput').value.trim(),msg=document.getElementById('loginMsg');if(!user||!pass||!captcha){msg.innerHTML='<div class="alert">⚠️ Vui lòng điền đầy đủ!</div>';return;}if(captcha.toUpperCase()!==captchaAnswer){msg.innerHTML='<div class="alert">❌ Mã captcha không đúng!</div>';generateCaptcha();return;}var btn=document.getElementById('btnLogin');btn.disabled=true;btn.innerHTML='<span class="loading"></span> ĐANG XỬ LÝ...';msg.innerHTML='';fetch(API+'/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user:user,password:pass})}).then(function(r){return r.json()}).then(function(d){if(d.status==='success'){localStorage.setItem('qanh_user',JSON.stringify(d.user));msg.innerHTML='<div class="success-box">✅ Đăng nhập thành công!</div>';setTimeout(function(){window.location.href='/shop'},1000)}else{msg.innerHTML='<div class="alert">❌ '+(d.message||'Thất bại!')+'</div>';generateCaptcha();btn.disabled=false;btn.innerHTML='ĐĂNG NHẬP'}}).catch(function(){msg.innerHTML='<div class="alert">❌ Lỗi kết nối!</div>';btn.disabled=false;btn.innerHTML='ĐĂNG NHẬP'});}
function doRegister(){var email=document.getElementById('regEmail').value.trim(),username=document.getElementById('regUsername').value.trim(),pass=document.getElementById('regPass').value.trim(),pass2=document.getElementById('regPass2').value.trim(),phone=document.getElementById('regPhone').value.trim(),captcha=document.getElementById('captchaInputReg').value.trim(),msg=document.getElementById('regMsg');if(!email||!username||!pass||!pass2||!captcha){msg.innerHTML='<div class="alert">⚠️ Điền đầy đủ!</div>';return;}if(pass!==pass2){msg.innerHTML='<div class="alert">❌ Mật khẩu không khớp!</div>';return;}if(pass.length<6){msg.innerHTML='<div class="alert">❌ Mật khẩu ít nhất 6 ký tự!</div>';return;}if(captcha.toUpperCase()!==captchaAnswerReg){msg.innerHTML='<div class="alert">❌ Mã captcha không đúng!</div>';generateCaptchaReg();return;}var btn=document.getElementById('btnRegister');btn.disabled=true;btn.innerHTML='<span class="loading"></span> ĐANG XỬ LÝ...';msg.innerHTML='';fetch(API+'/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,username:username,password:pass,phone:phone})}).then(function(r){return r.json()}).then(function(d){if(d.status==='success'){pendingEmail=email;document.getElementById('verifyEmailDisplay').innerText=email;document.getElementById('registerForm').classList.add('hidden');document.getElementById('verifyEmailForm').classList.remove('hidden');document.getElementById('verifyCode').value='';document.getElementById('btnVerify').disabled=false;startVerifyTimer();document.getElementById('verifyMsg').innerHTML='<div class="success-box">✅ Mã 6 số đã gửi!</div>';}else{msg.innerHTML='<div class="alert">❌ '+(d.message||'Thất bại!')+'</div>';generateCaptchaReg();}btn.disabled=false;btn.innerHTML='TẠO TÀI KHOẢN';}).catch(function(){msg.innerHTML='<div class="alert">❌ Lỗi kết nối!</div>';btn.disabled=false;btn.innerHTML='TẠO TÀI KHOẢN'});}
function verifyEmail(){var code=document.getElementById('verifyCode').value.trim(),msg=document.getElementById('verifyMsg');if(!code||code.length!==6){msg.innerHTML='<div class="alert">⚠️ Nhập đủ 6 chữ số!</div>';return;}if(verifySeconds<=0){msg.innerHTML='<div class="alert">❌ Mã hết hạn!</div>';return;}var btn=document.getElementById('btnVerify');btn.disabled=true;btn.innerHTML='<span class="loading"></span> ĐANG XÁC MINH...';fetch(API+'/api/verify-email',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:pendingEmail,code:code})}).then(function(r){return r.json()}).then(function(d){if(d.status==='success'){localStorage.setItem('qanh_user',JSON.stringify(d.user));clearInterval(verifyTimerInterval);msg.innerHTML='<div class="success-box">✅ Thành công!</div>';setTimeout(function(){window.location.href='/shop'},1500)}else{msg.innerHTML='<div class="alert">❌ '+(d.message||'Sai!')+'</div>';btn.disabled=false;btn.innerHTML='XÁC NHẬN'}}).catch(function(){msg.innerHTML='<div class="alert">❌ Lỗi!</div>';btn.disabled=false;btn.innerHTML='XÁC NHẬN'});}
function resendCode(){if(!pendingEmail)return;var btn=document.getElementById('btnVerify');btn.disabled=true;btn.innerHTML='<span class="loading"></span> ĐANG GỬI...';document.getElementById('verifyCode').value='';fetch(API+'/api/resend-code',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:pendingEmail})}).then(function(r){return r.json()}).then(function(d){if(d.status==='success'){startVerifyTimer();document.getElementById('verifyMsg').innerHTML='<div class="success-box">✅ Đã gửi lại!</div>'}else{document.getElementById('verifyMsg').innerHTML='<div class="alert">❌ Lỗi!</div>'}btn.disabled=false;btn.innerHTML='XÁC NHẬN'});}
generateCaptcha();generateCaptchaReg();
</script>
</body>
</html>"""

def get_shop_html():
    return r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QANH SHOP - Key Uy Tín</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root{--primary:#6C5CE7;--primary-dark:#5A4BD1;--gold:#FFD700;--green:#00D68F;--red:#FF6B6B;--blue:#45AAF2;--purple:#A855F7;--orange:#FF9F43;--bg:#0F0F1A;--card:#1A1A2E;--card2:#16213E;--text:#E0E0E0;--muted:#8E8E9A}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Plus Jakarta Sans',Arial,sans-serif;color:var(--text);min-height:100vh;background:var(--bg)}
        .navbar{position:sticky;top:0;z-index:100;background:rgba(15,15,26,0.85);backdrop-filter:blur(25px);padding:15px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(108,92,231,0.15);flex-wrap:wrap;gap:10px}
        .navbar .logo{font-size:22px;font-weight:800;background:linear-gradient(135deg,var(--primary),var(--blue));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .navbar .user-info{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
        .navbar .balance{background:rgba(108,92,231,0.08);border:1px solid rgba(108,92,231,0.25);border-radius:30px;padding:8px 16px;color:var(--primary);font-weight:600;cursor:pointer;font-size:13px;transition:0.3s}
        .navbar .balance:hover{background:rgba(108,92,231,0.15)}
        .navbar .btn-nav{background:var(--primary);color:#fff;border:none;border-radius:30px;padding:9px 20px;font-weight:600;cursor:pointer;font-size:13px;transition:0.3s;font-family:'Plus Jakarta Sans',sans-serif}
        .navbar .btn-nav:hover{background:var(--primary-dark);transform:scale(1.03)}
        .navbar .btn-admin{background:var(--purple)}
        .container{max-width:540px;margin:0 auto;padding:25px 15px}
        .card{background:var(--card);border-radius:20px;padding:25px;margin-bottom:20px;border:1px solid rgba(255,255,255,0.04);transition:0.3s;position:relative;overflow:hidden}
        .card:hover{border-color:rgba(108,92,231,0.2);transform:translateY(-2px);box-shadow:0 20px 50px rgba(0,0,0,0.4)}
        .card h2{color:#fff;margin-bottom:8px;font-size:18px;font-weight:700;display:flex;align-items:center;gap:10px}
        .card .price{font-size:38px;font-weight:800;background:linear-gradient(135deg,var(--primary),var(--blue));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .card .duration{color:var(--muted);margin:3px 0;font-size:13px}
        .card ul{list-style:none;margin:12px 0}
        .card ul li{padding:5px 0;color:var(--muted);font-size:13px}
        .card ul li::before{content:"✦ ";color:var(--primary)}
        .btn-card{display:block;width:100%;padding:15px;border:none;border-radius:14px;font-size:15px;font-weight:700;cursor:pointer;text-align:center;margin-top:12px;transition:0.3s;font-family:'Plus Jakarta Sans',sans-serif}
        .btn-card:hover{transform:translateY(-2px)}
        .btn-card:disabled{opacity:0.5;cursor:not-allowed;transform:none}
        .btn-green{background:linear-gradient(135deg,#00D68F,#00B377);color:#fff;box-shadow:0 8px 25px rgba(0,214,143,0.25)}
        .btn-gold{background:linear-gradient(135deg,#FFD700,#FFA500);color:#000;box-shadow:0 8px 25px rgba(255,165,0,0.3)}
        .btn-blue{background:linear-gradient(135deg,#45AAF2,#2D8FD5);color:#fff;box-shadow:0 8px 25px rgba(69,170,242,0.25)}
        .btn-purple{background:linear-gradient(135deg,#A855F7,#8B3FE0);color:#fff;box-shadow:0 8px 25px rgba(168,85,247,0.25)}
        .btn-primary{background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;box-shadow:0 8px 25px rgba(108,92,231,0.3)}
        .btn-recharge{background:linear-gradient(135deg,#00D68F,#00B377);color:#fff;font-size:17px;padding:18px;font-weight:800;box-shadow:0 10px 30px rgba(0,214,143,0.3)}
        .badge{display:inline-block;padding:4px 12px;border-radius:25px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px}
        .badge-free{background:rgba(0,214,143,0.12);color:var(--green)}
        .badge-vip-card{background:rgba(108,92,231,0.12);color:var(--primary)}
        .badge-hot{background:rgba(255,159,67,0.12);color:var(--orange);animation:pulse 2s infinite}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
        .section-title{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:2px;margin:25px 0 10px;text-align:center}
        select,input[type="text"],input[type="number"]{width:100%;padding:14px 16px;margin:7px 0;border-radius:12px;border:2px solid rgba(255,255,255,0.05);background:var(--card2);color:#fff;font-size:14px;font-weight:500;font-family:'Plus Jakarta Sans',sans-serif;transition:0.3s}
        select:focus,input:focus{border-color:var(--primary);outline:none;box-shadow:0 0 15px rgba(108,92,231,0.1)}
        select option{background:var(--card);color:#fff}
        .card-accent{position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--primary),var(--blue),var(--green));border-radius:20px 20px 0 0}
        .card-gold-accent{position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--gold),var(--orange));border-radius:20px 20px 0 0}
        .modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;justify-content:center;align-items:center;backdrop-filter:blur(5px)}
        .modal.active{display:flex}
        .modal-content{background:var(--card);border-radius:24px;padding:30px;width:90%;max-width:440px;text-align:center;max-height:85vh;overflow-y:auto;border:1px solid rgba(255,255,255,0.06);box-shadow:0 30px 80px rgba(0,0,0,0.6);animation:modalIn 0.3s}
        @keyframes modalIn{from{opacity:0;transform:scale(0.9)translateY(30px)}to{opacity:1;transform:scale(1)translateY(0)}}
        .modal-content h3{font-size:22px;font-weight:700;margin-bottom:15px}
        .close-btn{float:right;color:var(--muted);font-size:24px;cursor:pointer;background:none;border:none}
        .close-btn:hover{color:#fff}
        .key-display{font-size:15px;color:var(--green);font-family:'Courier New',monospace;background:rgba(0,0,0,0.5);padding:18px;border-radius:14px;margin:15px 0;word-break:break-all;border:2px dashed rgba(0,214,143,0.3)}
        .copy-btn{background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;border:none;padding:14px;border-radius:14px;cursor:pointer;font-weight:700;font-size:15px;width:100%;margin-top:10px;font-family:'Plus Jakarta Sans',sans-serif;transition:0.3s}
        .copy-btn:hover{transform:translateY(-2px)}
        .alert-box{background:rgba(255,107,107,0.06);border:1px solid rgba(255,107,107,0.2);border-radius:14px;padding:14px;margin:10px 0;color:var(--red);font-size:13px}
        .success-box{background:rgba(0,214,143,0.06);border:1px solid rgba(0,214,143,0.2);border-radius:14px;padding:14px;margin:10px 0;color:var(--green);font-size:13px}
        .loading{display:inline-block;width:24px;height:24px;border:3px solid rgba(255,255,255,0.1);border-top:3px solid var(--primary);border-radius:50%;animation:spin 0.7s linear infinite;margin:10px auto}
        @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
        .toast{position:fixed;top:20px;right:20px;z-index:10000;padding:14px 22px;border-radius:14px;color:#fff;font-weight:600;font-size:14px;animation:slideIn 0.4s;box-shadow:0 10px 40px rgba(0,0,0,0.5);font-family:'Plus Jakarta Sans',sans-serif}
        .toast-success{background:var(--green);color:#000}
        .toast-error{background:var(--red)}
        @keyframes slideIn{from{transform:translateX(120%)}to{transform:translateX(0)}}
        .info-text{color:var(--muted);font-size:12px;margin-top:8px;text-align:center}
        .hidden{display:none!important}
        .history-table{width:100%;border-collapse:collapse;font-size:12px;margin-top:10px}
        .history-table th{background:rgba(108,92,231,0.2);color:var(--primary);padding:10px;text-align:center;font-weight:600}
        .history-table td{padding:10px;border-bottom:1px solid rgba(255,255,255,0.05);text-align:center;color:var(--muted)}
        .history-table tr:hover{background:rgba(108,92,231,0.05)}
    </style>
</head>
<body>
<div class="navbar">
    <div class="logo">QANH SHOP</div>
    <div class="user-info">
        <span class="balance" id="balanceDisplay" onclick="document.getElementById('rechargeSection').scrollIntoView({behavior:'smooth'})">💰 0đ</span>
        <button class="btn-nav" id="userBtn" onclick="logout()">👤 TÀI KHOẢN</button>
        <button class="btn-nav btn-admin hidden" id="adminBtn" onclick="showAdminModal()">⚙️ ADMIN</button>
    </div>
</div>

<div class="container">
    <!-- NẠP TIỀN -->
    <div class="card" id="rechargeSection"><div class="card-accent"></div>
        <h2>💳 Nạp Tiền Vào Tài Khoản</h2>
        <select id="rcType"><option value="">Chọn nhà mạng</option><option value="VIETTEL">📱 Viettel</option><option value="MOBIFONE">📱 Mobifone</option><option value="VINAPHONE">📱 Vinaphone</option></select>
        <select id="rcAmount"><option value="">Chọn mệnh giá</option><option value="10000">10.000đ</option><option value="20000">20.000đ</option><option value="50000">50.000đ</option><option value="100000">100.000đ</option><option value="200000">200.000đ</option><option value="500000">500.000đ</option></select>
        <input type="text" id="rcPin" placeholder="🔢 Nhập mã thẻ...">
        <input type="text" id="rcSerial" placeholder="📝 Nhập số serial...">
        <button class="btn-card btn-recharge" onclick="recharge()">💳 NẠP TIỀN NGAY</button>
        <div id="rcResult" style="margin-top:12px;text-align:center"></div>
    </div>
    
    <!-- MIỄN PHÍ -->
    <div class="section-title">🎁 GÓI MIỄN PHÍ</div>
    <div class="card" style="border-color:rgba(0,214,143,0.15)"><div class="card-accent" style="background:linear-gradient(90deg,var(--green),var(--blue))"></div>
        <h2>🆓 KEY FREE <span class="badge badge-free">MIỄN PHÍ</span></h2>
        <div class="price" style="background:linear-gradient(135deg,var(--green),#00B377);-webkit-background-clip:text;-webkit-text-fill-color:transparent">0đ</div>
        <div class="duration">⏰ 1 ngày</div>
        <ul><li>Dùng thử miễn phí</li><li>Tính năng cơ bản</li><li>Cần xác thực link4m</li></ul>
        <button class="btn-card btn-green" onclick="window.open('/Getkey.php','_blank')">🎁 NHẬN KEY FREE</button>
    </div>
    
    <!-- VIP -->
    <div class="section-title">👑 GÓI VIP</div>
    <div class="card" style="border-color:rgba(168,85,247,0.15)"><div class="card-accent" style="background:linear-gradient(90deg,var(--purple),var(--primary))"></div>
        <h2>💎 KEY 1 TUẦN <span class="badge badge-hot">HOT</span></h2>
        <div class="price" style="background:linear-gradient(135deg,var(--purple),var(--primary));-webkit-background-clip:text;-webkit-text-fill-color:transparent">50.000đ</div>
        <div class="duration">⏰ 7 ngày</div>
        <ul><li>Tất cả tính năng VIP</li><li>Không giới hạn link</li><li>Tốc độ ưu tiên</li></ul>
        <button class="btn-card btn-purple" onclick="buyKey('week')">💳 MUA NGAY</button>
    </div>
    <div class="card" style="border-color:rgba(69,170,242,0.15)"><div class="card-accent" style="background:linear-gradient(90deg,var(--blue),var(--primary))"></div>
        <h2>🔑 KEY 1 THÁNG <span class="badge badge-vip-card">VIP</span></h2>
        <div class="price" style="background:linear-gradient(135deg,var(--blue),var(--primary));-webkit-background-clip:text;-webkit-text-fill-color:transparent">150.000đ</div>
        <div class="duration">⏰ 30 ngày</div>
        <ul><li>Tất cả tính năng VIP</li><li>Hỗ trợ 24/7</li><li>Ưu tiên xử lý</li></ul>
        <button class="btn-card btn-blue" onclick="buyKey('month')">💳 MUA NGAY</button>
    </div>
    <div class="card" style="border-color:rgba(255,215,0,0.2);box-shadow:0 0 40px rgba(255,215,0,0.05)"><div class="card-gold-accent"></div>
        <h2>👑 KEY VĨNH VIỄN <span class="badge badge-vip-card" style="background:rgba(255,215,0,0.12);color:var(--gold)">PREMIUM</span></h2>
        <div class="price" style="background:linear-gradient(135deg,var(--gold),var(--orange));-webkit-background-clip:text;-webkit-text-fill-color:transparent">250.000đ</div>
        <div class="duration">⏰ Không giới hạn</div>
        <ul><li>Tất cả Premium</li><li>Update trọn đời</li><li>Hỗ trợ VIP 24/7</li></ul>
        <button class="btn-card btn-gold" onclick="buyKey('forever')">💳 MUA NGAY</button>
    </div>
    
    <!-- LỊCH SỬ GIAO DỊCH -->
    <div class="section-title">📋 LỊCH SỬ GIAO DỊCH</div>
    <div class="card">
        <div style="overflow-x:auto">
            <table class="history-table">
                <thead><tr><th>Loại</th><th>Key/Số tiền</th><th>Thời gian</th><th>TT</th></tr></thead>
                <tbody id="historyBody"><tr><td colspan="4">Chưa có giao dịch</td></tr></tbody>
            </table>
        </div>
    </div>
</div>

<!-- MODALS -->
<div class="modal" id="keyModal"><div class="modal-content">
    <span class="close-btn" onclick="document.getElementById('keyModal').classList.remove('active')">✕</span>
    <h3 style="color:var(--green)">✅ THÀNH CÔNG!</h3>
    <p id="keyMessage" style="color:var(--muted);margin:10px 0"></p>
    <div class="key-display" id="keyDisplay"></div>
    <button class="copy-btn" onclick="copyKey()">📋 COPY KEY</button>
    <p class="info-text">💡 Dùng <b>/kichhoat KEY</b> trong bot Telegram</p>
</div></div>

<div class="modal" id="confirmBuyModal"><div class="modal-content">
    <span class="close-btn" onclick="document.getElementById('confirmBuyModal').classList.remove('active')">✕</span>
    <h3>⚠️ XÁC NHẬN MUA</h3>
    <div class="alert-box"><p><b id="confirmKeyType"></b></p><p>Giá: <b id="confirmKeyPrice"></b></p><p>Số dư: <b id="confirmBalance"></b></p></div>
    <button class="btn-card btn-primary" style="margin-top:5px" onclick="confirmBuy()">✅ XÁC NHẬN</button>
    <button class="btn-card" style="background:rgba(255,255,255,0.05);color:var(--muted);margin-top:8px" onclick="document.getElementById('confirmBuyModal').classList.remove('active')">❌ HỦY</button>
</div></div>

<div class="modal" id="adminModal"><div class="modal-content">
    <span class="close-btn" onclick="document.getElementById('adminModal').classList.remove('active')">✕</span>
    <h3>⚙️ ADMIN PANEL</h3>
    <input type="text" id="adminTargetEmail" placeholder="📧 Email người dùng...">
    <input type="number" id="adminSetBalance" placeholder="💰 Số dư mới...">
    <button class="btn-card btn-primary" style="margin-top:5px" onclick="adminSetBalance()">💾 CẬP NHẬT</button>
    <hr style="border-color:rgba(255,255,255,0.05);margin:15px 0">
    <button class="btn-card btn-green" onclick="adminQuickFreeKey()">🎁 TẠO KEY FREE</button>
</div></div>

<script>
var API=window.location.origin;
var currentUser=null,pendingBuy=null;
var keyPrices={week:50000,month:150000,forever:250000};
var keyNames={week:'💎 KEY 1 TUẦN',month:'🔑 KEY 1 THÁNG',forever:'👑 KEY VĨNH VIỄN'};
try{currentUser=JSON.parse(localStorage.getItem('qanh_user'))||null;}catch(e){}
if(!currentUser){window.location.href='/login';}
function updateUI(){
    if(!currentUser)return;
    document.getElementById('userBtn').innerText='👤 '+currentUser.name;
    document.getElementById('balanceDisplay').innerText='💰 '+(currentUser.balance||0).toLocaleString()+'đ';
    if(currentUser.isAdmin)document.getElementById('adminBtn').classList.remove('hidden');
    loadHistory();
}
function showToast(msg,type){var t=document.createElement('div');t.className='toast toast-'+(type||'success');t.innerText=msg;document.body.appendChild(t);setTimeout(function(){t.style.opacity='0';setTimeout(function(){t.remove()},300)},2500);}
function logout(){localStorage.removeItem('qanh_user');window.location.href='/login';}
function recharge(){if(!currentUser)return;var telco=document.getElementById('rcType').value,amount=parseInt(document.getElementById('rcAmount').value),pin=document.getElementById('rcPin').value.trim(),serial=document.getElementById('rcSerial').value.trim();if(!telco||!amount||!pin||!serial){showToast('⚠️ Điền đầy đủ!','error');return;}document.getElementById('rcResult').innerHTML='<div class="loading"></div><p style="color:var(--primary)">Đang xử lý...</p>';fetch('https://api.shoppay.vn/card/charge',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({partner_id:'70406595609',partner_key:'add9c7d61cb54ff1b447e2188c71a8c2',telco:telco,amount:amount,pin:pin,serial:serial})}).then(function(r){return r.json()}).then(function(d){if(d.status===1){currentUser.balance=(currentUser.balance||0)+amount;localStorage.setItem('qanh_user',JSON.stringify(currentUser));updateUI();document.getElementById('rcResult').innerHTML='<div class="success-box">✅ Nạp '+amount.toLocaleString()+'đ!</div>';document.getElementById('rcPin').value='';document.getElementById('rcSerial').value='';fetch(API+'/api/save-transaction?type=recharge&amount='+amount+'&email='+encodeURIComponent(currentUser.email));}else{document.getElementById('rcResult').innerHTML='<div class="alert-box">❌ '+(d.message||'Lỗi')+'</div>';}}).catch(function(){document.getElementById('rcResult').innerHTML='<div class="alert-box">❌ Lỗi kết nối!</div>';});}
function buyKey(type){if(!currentUser)return;var p=keyPrices[type];if((currentUser.balance||0)<p){showToast('❌ Không đủ!','error');return;}pendingBuy=type;document.getElementById('confirmKeyType').innerText=keyNames[type];document.getElementById('confirmKeyPrice').innerText=p.toLocaleString()+'đ';document.getElementById('confirmBalance').innerText=(currentUser.balance||0).toLocaleString()+'đ';document.getElementById('confirmBuyModal').classList.add('active');}
function confirmBuy(){if(!pendingBuy)return;var type=pendingBuy,p=keyPrices[type];pendingBuy=null;document.getElementById('confirmBuyModal').classList.remove('active');currentUser.balance-=p;localStorage.setItem('qanh_user',JSON.stringify(currentUser));updateUI();fetch(API+'/api/buy-key?type='+type+'&email='+encodeURIComponent(currentUser.email)).then(function(r){return r.json()}).then(function(d){if(d.status==='success'){document.getElementById('keyDisplay').innerText=d.key;document.getElementById('keyMessage').innerText='Mua '+keyNames[type]+' thành công! Key đã lưu!';document.getElementById('keyModal').classList.add('active');}else{currentUser.balance+=p;localStorage.setItem('qanh_user',JSON.stringify(currentUser));updateUI();showToast('❌ Lỗi!','error');}}).catch(function(){currentUser.balance+=p;localStorage.setItem('qanh_user',JSON.stringify(currentUser));updateUI();});}
function copyKey(){var k=document.getElementById('keyDisplay').innerText;navigator.clipboard.writeText(k).then(function(){showToast('✅ Đã copy!')}).catch(function(){prompt('Copy:',k)});}
function showAdminModal(){if(!currentUser||!currentUser.isAdmin)return;document.getElementById('adminModal').classList.add('active');}
function adminSetBalance(){var e=document.getElementById('adminTargetEmail').value.trim(),a=parseInt(document.getElementById('adminSetBalance').value);if(!e||isNaN(a))return;fetch(API+'/api/admin-set-balance',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,amount:a})}).then(function(r){return r.json()}).then(function(d){showToast(d.message||'✅ OK!');document.getElementById('adminModal').classList.remove('active');});}
function adminQuickFreeKey(){document.getElementById('adminModal').classList.remove('active');fetch(API+'/api/create-key?type=free&email='+encodeURIComponent(currentUser.email)).then(function(r){return r.json()}).then(function(d){if(d.status==='success'){document.getElementById('keyDisplay').innerText=d.key;document.getElementById('keyMessage').innerText='Key Free Admin!';document.getElementById('keyModal').classList.add('active');}});}
function loadHistory(){
    if(!currentUser)return;
    fetch(API+'/api/get-history?email='+encodeURIComponent(currentUser.email))
    .then(function(r){return r.json()})
    .then(function(d){
        var hb=document.getElementById('historyBody');
        if(!d.transactions||d.transactions.length===0){hb.innerHTML='<tr><td colspan="4">Chưa có giao dịch</td></tr>';return;}
        var html='';
        for(var i=d.transactions.length-1;i>=Math.max(0,d.transactions.length-10);i--){
            var t=d.transactions[i];
            html+='<tr><td>'+(t.type==='recharge'?'💳 Nạp':t.type==='buy_key'?'🔑 Mua Key':'🆓 Free')+'</td><td>'+(t.key||t.amount.toLocaleString()+'đ')+'</td><td>'+new Date(t.time).toLocaleString()+'</td><td style="color:'+(t.status==='success'?'var(--green)':'var(--red)')+'">'+(t.status==='success'?'✅':'❌')+'</td></tr>';
        }
        hb.innerHTML=html;
    });
}
updateUI();
</script>
</body>
</html>""" + """</html>"""

# ===== ROUTES =====
@app.route('/')
@app.route('/login')
def login_page():
    return get_login_html()

@app.route('/shop')
def shop_page():
    return get_shop_html()

@app.route('/Getkey.php')
def getkey_page():
    return r"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><title>Nhận Key Free</title>
<style>:root{--primary:#6C5CE7;--gold:#FFD700;--green:#00D68F;--bg:#0F0F1A;--card:#1A1A2E}
*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Plus Jakarta Sans',Arial;color:#fff;min-height:100vh;background:var(--bg);display:flex;justify-content:center;align-items:center;padding:20px}
.container{background:var(--card);border-radius:24px;padding:35px 30px;max-width:500px;width:100%;border:1px solid rgba(108,92,231,0.15);box-shadow:0 25px 80px rgba(0,0,0,0.5);text-align:center}
.logo{font-size:30px;font-weight:800;background:linear-gradient(135deg,var(--primary),#45AAF2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:5px}
.subtitle{color:#8E8E9A;margin-bottom:25px}.step-container{background:rgba(0,0,0,0.3);border-radius:16px;padding:22px;margin:15px 0}
.step-title{font-size:18px;color:var(--primary);margin-bottom:10px;font-weight:700}
.key-display{font-size:18px;color:var(--green);font-family:monospace;background:rgba(0,0,0,0.5);padding:16px;border-radius:12px;margin:15px 0;border:2px dashed rgba(0,214,143,0.3);word-break:break-all}
.btn{display:block;width:100%;padding:15px;border:none;border-radius:14px;font-size:16px;font-weight:700;cursor:pointer;text-align:center;margin:10px 0;transition:0.3s;font-family:'Plus Jakarta Sans',sans-serif}
.btn-primary{background:linear-gradient(135deg,var(--primary),#5A4BD1);color:#fff;box-shadow:0 10px 30px rgba(108,92,231,0.3)}
.btn-gold{background:linear-gradient(135deg,#FFD700,#FFA500);color:#000}
.hidden{display:none!important}.loading{display:inline-block;width:30px;height:30px;border:3px solid rgba(255,255,255,0.1);border-top:3px solid var(--primary);border-radius:50%;animation:spin 0.7s linear infinite;margin:10px}
@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
.step-dot{width:40px;height:40px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:18px;margin:0 10px}
.step-dot.active{background:var(--primary);color:#fff}.step-dot.done{background:var(--green);color:#fff}.step-dot.wait{background:rgba(255,255,255,0.06);color:#8E8E9A}
</style></head><body><div class="container">
<div class="logo">QANH KEY</div><p class="subtitle">Nhận Key Free - Xác thực qua Link4m</p>
<div style="margin:15px 0"><span class="step-dot active" id="dot1">1</span><span style="color:#555">→</span><span class="step-dot wait" id="dot2">2</span><span style="color:#555">→</span><span class="step-dot wait" id="dot3">✓</span></div>
<div id="step1" class="step-container"><div class="step-title">📌 Bước 1: Mở Link Xác Thực</div><p style="color:#8E8E9A">Nhấn nút để mở link. <b>Hoàn thành NHIỆM VỤ</b> trên link4m để nhận key.</p><button class="btn btn-primary" id="btnVerify" onclick="startVerify()">🔗 MỞ LINK XÁC THỰC</button><p style="color:#8E8E9A;font-size:11px;margin-top:8px">⚠️ Bạn phải xem HẾT nội dung, link4m phải ghi nhận!</p></div>
<div id="step2" class="step-container hidden"><div class="step-title">⏳ Bước 2: Đang Kiểm Tra Xác Thực</div><div class="loading"></div><p style="color:#ff9f43;font-size:13px">⚠️ Đang kiểm tra link4m... Đừng tắt trang!</p><p style="color:#8E8E9A;font-size:11px">Hệ thống đang chờ link4m xác nhận bạn đã hoàn thành</p></div>
<div id="step3" class="step-container hidden"><div class="step-title">✅ Bước 3: Nhận Key Thành Công!</div><p style="color:var(--green)">Link4m đã xác nhận! Key của bạn:</p><div class="key-display" id="keyDisplay">...</div><button class="btn btn-gold" onclick="copyKey()">📋 COPY KEY</button><p style="color:#8E8E9A;font-size:11px;margin-top:8px">💡 Dùng /kichhoat KEY trong bot Telegram</p></div>
</div>
<script>
var API=window.location.origin;var verifyToken=null,checkInterval=null,myKey=null;
function startVerify(){var btn=document.getElementById('btnVerify');btn.disabled=true;btn.innerText='⏳ ĐANG TẠO...';fetch(API+'/api/get-free-link?email=user_'+Date.now()).then(function(r){return r.json()}).then(function(d){if(d.status==='success'&&d.link4m){verifyToken=d.token;window.open(d.link4m,'_blank');document.getElementById('step1').classList.add('hidden');document.getElementById('step2').classList.remove('hidden');document.getElementById('dot1').className='step-dot done';document.getElementById('dot2').className='step-dot active';startCheck();}else{alert('Lỗi: '+(d.message||'Không thể tạo link!'));btn.disabled=false;btn.innerText='🔗 MỞ LINK XÁC THỰC';}}).catch(function(){btn.disabled=false;btn.innerText='🔗 MỞ LINK XÁC THỰC';});}
function startCheck(){var count=0;checkInterval=setInterval(function(){count++;fetch(API+'/api/check-verify?token='+verifyToken).then(function(r){return r.json()}).then(function(d){if(d.status==='verified'&&d.key){clearInterval(checkInterval);myKey=d.key;document.getElementById('step2').classList.add('hidden');document.getElementById('step3').classList.remove('hidden');document.getElementById('dot2').className='step-dot done';document.getElementById('dot3').className='step-dot active';document.getElementById('keyDisplay').innerText=d.key;}else if(count>=180){clearInterval(checkInterval);document.getElementById('step2').innerHTML='<div class="step-title">❌ Hết Thời Gian</div><p style="color:#FF6B6B">Không thể xác nhận! Vui lòng thử lại.</p><button class="btn btn-primary" onclick="location.reload()">🔄 THỬ LẠI</button>';}});},3000);}
function copyKey(){if(!myKey)return;navigator.clipboard.writeText(myKey).then(function(){alert('✅ Đã copy! /kichhoat '+myKey.substring(0,20)+'...');}).catch(function(){prompt('Copy:',myKey);});}
</script></body></html>"""

# ===== API ROUTES =====
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    email = data.get('email', '').strip().lower()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    phone = data.get('phone', '')
    if not email or not username or not password:
        return jsonify({"status": "error", "message": "Thiếu thông tin!"})
    if email in users_db:
        return jsonify({"status": "error", "message": "Email đã được sử dụng!"})
    code = generate_verify_code()
    pending_registrations[email] = {"username": username, "password": password, "phone": phone, "code": code, "time": time()}
    save_all_data()
    send_verification_email(email, code)
    return jsonify({"status": "success", "message": "Mã xác minh đã gửi!"})

@app.route('/api/resend-code', methods=['POST'])
def api_resend_code():
    data = request.json
    email = data.get('email', '').strip().lower()
    if email not in pending_registrations:
        return jsonify({"status": "error", "message": "Không tìm thấy!"})
    code = generate_verify_code()
    pending_registrations[email]["code"] = code
    pending_registrations[email]["time"] = time()
    save_all_data()
    send_verification_email(email, code)
    return jsonify({"status": "success"})

@app.route('/api/verify-email', methods=['POST'])
def api_verify_email():
    data = request.json
    email = data.get('email', '').strip().lower()
    code = data.get('code', '')
    if email not in pending_registrations:
        return jsonify({"status": "error", "message": "Không tìm thấy yêu cầu!"})
    pending = pending_registrations[email]
    if time() - pending["time"] > 60:
        del pending_registrations[email]
        save_all_data()
        return jsonify({"status": "error", "message": "Mã hết hạn!"})
    if pending["code"] != code:
        return jsonify({"status": "error", "message": "Mã không đúng!"})
    users_db[email] = {"name": pending["username"], "email": email, "password": pending["password"], "phone": pending["phone"], "balance": 0, "isAdmin": False, "isVip": False}
    del pending_registrations[email]
    save_all_data()
    return jsonify({"status": "success", "user": users_db[email]})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user_input = data.get('user', '').strip().lower()
    password = data.get('password', '')
    if user_input in ['admin@qanhshop.com', 'admin'] and password == 'QanhAdmin@2025#Secret!':
        return jsonify({"status": "success", "user": {"name": "Admin", "email": "admin@qanhshop.com", "balance": 999999999, "isAdmin": True, "isVip": True}})
    for email, u in users_db.items():
        if email == user_input or u.get('name', '').lower() == user_input:
            if u['password'] == password:
                return jsonify({"status": "success", "user": u})
            return jsonify({"status": "error", "message": "Sai mật khẩu!"})
    return jsonify({"status": "error", "message": "Tài khoản không tồn tại!"})

@app.route('/api/buy-key')
def api_buy_key():
    key_type = request.args.get('type', 'week')
    email = request.args.get('email', '')
    key = generate_key()
    
    # LƯU KEY VÀO DATABASE WEB
    save_key_local(key, key_type, email)
    # Gửi lệnh cho bot
    send_key_to_bot(key, key_type)
    # Lưu giao dịch
    prices = {'week': 50000, 'month': 150000, 'forever': 250000}
    save_transaction(email, 'buy_key', prices.get(key_type, 0), key, 'success')
    
    return jsonify({"status": "success", "key": key})

@app.route('/api/create-key')
def api_create_key():
    key = generate_key()
    email = request.args.get('email', 'admin')
    save_key_local(key, 'free', email)
    send_key_to_bot(key, 'free')
    save_transaction(email, 'free_key', 0, key, 'success')
    return jsonify({"status": "success", "key": key})

@app.route('/api/get-free-link')
def api_get_free_link():
    email = request.args.get('email', 'user')
    token = secrets.token_hex(16)
    callback_url = RENDER_URL + "/verify/" + token
    try:
        api_url = f"https://link4m.co/api-shorten/v2?api={LINK4M_API_KEY}&url={callback_url}"
        res = requests.get(api_url, timeout=10)
        link_data = res.json()
        if link_data.get('status') == 'success':
            pending_verify[token] = {"email": email, "time": time(), "verified": False, "key": None}
            save_all_data()
            return jsonify({"status": "success", "link4m": link_data.get('shortenedUrl'), "token": token})
    except: pass
    return jsonify({"status": "error", "message": "Lỗi tạo link!"})

@app.route('/verify/<token>')
def verify_page(token):
    if token not in pending_verify:
        return "<h1>⚠️ Link không hợp lệ!</h1>", 404
    
    email = pending_verify[token].get("email", "")
    key = generate_key()
    
    # LƯU KEY
    save_key_local(key, 'free', email)
    send_key_to_bot(key, 'free')
    save_transaction(email, 'free_key_verified', 0, key, 'success')
    
    pending_verify[token]["verified"] = True
    pending_verify[token]["key"] = key
    save_all_data()
    
    return f"""<!DOCTYPE html><html><head><meta charset='UTF-8'><title>✅ Xác Thực</title>
<style>body{{background:#0F0F1A;color:#fff;text-align:center;padding:50px;font-family:'Plus Jakarta Sans',Arial}}h2{{color:#00D68F}}.key{{color:#00D68F;background:#000;padding:18px;border-radius:14px;border:2px dashed rgba(0,214,143,0.3);font-family:monospace;font-size:18px;margin:15px 0;word-break:break-all}}button{{background:#6C5CE7;color:#fff;padding:14px 28px;border:none;border-radius:12px;font-weight:700;font-size:16px;cursor:pointer}}</style></head>
<body><h2>✅ HOÀN THÀNH NHIỆM VỤ!</h2><div class='key'>{key}</div>
<button onclick="navigator.clipboard.writeText('{key}')">📋 COPY KEY</button>
<p style='color:#8E8E9A;margin-top:15px'>💡 Dùng <b>/kichhoat {key[:20]}...</b> trong bot</p>
<script>setTimeout(function(){{if(window.opener&&!window.opener.closed)window.opener.location.reload()}},2000);</script></body></html>"""

@app.route('/api/check-verify')
def api_check_verify():
    token = request.args.get('token', '')
    if token in pending_verify and pending_verify[token].get("verified"):
        return jsonify({"status": "verified", "key": pending_verify[token]["key"]})
    return jsonify({"status": "pending"})

@app.route('/api/save-transaction')
def api_save_transaction():
    email = request.args.get('email', '')
    trans_type = request.args.get('type', '')
    amount = request.args.get('amount', 0)
    save_transaction(email, trans_type, int(amount), '', 'success')
    return jsonify({"status": "success"})

@app.route('/api/get-history')
def api_get_history():
    email = request.args.get('email', '')
    user_transactions = [t for t in transactions_db if t.get('email') == email]
    user_keys = [k for k in keys_db.get("keys_history", []) if k.get('email') == email]
    return jsonify({"transactions": user_transactions, "keys": user_keys})

@app.route('/api/admin-set-balance', methods=['POST'])
def api_admin_set_balance():
    data = request.json
    email = data.get('email', '').strip().lower()
    amount = data.get('amount', 0)
    if email in users_db:
        users_db[email]['balance'] = amount
        save_all_data()
        save_transaction(email, 'admin_set_balance', amount, '', 'success')
        return jsonify({"status": "success", "message": f"Đã cập nhật {email}: {amount}đ"})
    return jsonify({"status": "error", "message": "Không tìm thấy!"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)