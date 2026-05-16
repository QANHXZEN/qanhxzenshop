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

BOT_TOKEN = "8466851320:AAGc77X4DnPQRNkw7rVUhlpJVIcBlOcSlDA"
CHAT_ID = "8588555065"
OWNER_ID = 8588555065
LINK4M_API_KEY = "65c47d157fbdff4d79625e57"
RENDER_URL = "https://qanhxzenshop.onrender.com"

EMAIL_SENDER = "qanhxzenshopfeedback@gmail.com"
EMAIL_PASSWORD = "lmyj wgyp tfzo qxkj"

pending_registrations = {}
pending_verify = {}
users_db = {}

def generate_key():
    c = string.ascii_uppercase + string.digits
    r = lambda l: ''.join(secrets.choice(c) for _ in range(l))
    return f"QANH-{r(10)}-{r(10)}-{r(10)}-{r(5)}"

def generate_verify_code():
    return ''.join([str(rnd.randint(0, 9)) for _ in range(6)])

def save_key_to_bot(key, key_type):
    try:
        cmds = {'free': 'free 1ngay', 'week': '1w', 'month': 'vip 1thang', 'forever': 'vip vinhvien'}
        cmd = cmds.get(key_type, 'free 1ngay')
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                json={'chat_id': CHAT_ID, 'text': f'/taokey {cmd}'}, timeout=10)
        return True
    except Exception as e:
        print(f"Save key error: {e}")
        return False

def send_verification_email(to_email, code):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = "QANH SHOP - Mã Xác Minh Email"
        body = f"""
        <div style="background:#0f0c29;color:#fff;padding:30px;font-family:Arial;text-align:center;border-radius:15px">
            <h2 style="color:#FFD700">QANH SHOP</h2>
            <p>Mã xác minh của bạn:</p>
            <div style="font-size:36px;color:#00ff00;background:#000;padding:15px;border-radius:10px;margin:20px;letter-spacing:8px">{code}</div>
            <p style="color:#ff6600">Mã hết hạn sau 1 phút</p>
        </div>
        """
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ===== LOGIN HTML =====
LOGIN_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QANH SHOP - Đăng Nhập</title>
    <style>
        :root{--gold:#FFD700;--green:#00ff88;--red:#ff4757;--blue:#00d4ff;--purple:#a855f7}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Segoe UI',Arial;color:#fff;min-height:100vh;background:#0a0a1a;display:flex;justify-content:center;align-items:center;padding:20px}
        .bg-animation{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0}
        .bg-circle{position:absolute;border-radius:50%;opacity:0.06;animation:float 20s infinite}
        .bg-circle:nth-child(1){width:400px;height:400px;background:var(--purple);top:-100px;left:-100px}
        .bg-circle:nth-child(2){width:300px;height:300px;background:var(--blue);bottom:-50px;right:-50px;animation-delay:-7s}
        .bg-circle:nth-child(3){width:200px;height:200px;background:var(--gold);top:50%;left:50%;animation-delay:-14s}
        @keyframes float{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(30px,-30px) scale(1.1)}66%{transform:translate(-20px,20px) scale(0.9)}}
        .container{position:relative;z-index:1;background:#1a1a2e;border-radius:24px;padding:35px 30px;max-width:440px;width:100%;border:1px solid rgba(255,215,0,0.2);box-shadow:0 20px 60px rgba(0,0,0,0.5);animation:slideUp 0.5s}
        @keyframes slideUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
        .logo{font-size:32px;background:linear-gradient(135deg,var(--gold),#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;font-weight:700;margin-bottom:5px}
        .subtitle{color:#8899aa;text-align:center;margin-bottom:25px;font-size:14px}
        .input-group{margin-bottom:16px}
        .input-group label{display:block;color:#aabbcc;margin-bottom:6px;font-size:13px;font-weight:600}
        .input-group input{width:100%;padding:14px 16px;border-radius:12px;border:2px solid rgba(255,255,255,0.08);background:#16213e;color:#fff;font-size:15px;transition:0.3s}
        .input-group input:focus{border-color:var(--gold);outline:none;box-shadow:0 0 15px rgba(255,215,0,0.1)}
        .captcha-box{background:rgba(0,0,0,0.3);border:1px dashed #555;border-radius:12px;padding:18px;text-align:center;margin:18px 0}
        .captcha-text{font-size:28px;color:var(--gold);font-weight:700;letter-spacing:5px;margin:10px 0;user-select:none}
        .captcha-box input{width:100%;padding:10px;border-radius:8px;border:1px solid #555;background:#000;color:#fff;text-align:center;font-size:18px;letter-spacing:4px}
        .refresh-btn{background:none;border:none;color:var(--blue);cursor:pointer;font-size:12px;margin-top:8px}
        .btn{display:block;width:100%;padding:15px;border:none;border-radius:12px;font-size:16px;font-weight:700;cursor:pointer;text-align:center;transition:0.3s;text-transform:uppercase}
        .btn-gold{background:linear-gradient(135deg,var(--gold),#FFA500);color:#000;box-shadow:0 10px 30px rgba(255,165,0,0.3)}
        .btn:hover{transform:translateY(-2px)}
        .btn:disabled{opacity:0.5;cursor:not-allowed;transform:none}
        .link-text{color:#667788;text-align:center;margin-top:20px;font-size:14px}
        .link-text a{color:var(--gold);cursor:pointer;text-decoration:underline;font-weight:600}
        .alert{background:rgba(255,71,87,0.1);border:1px solid var(--red);border-radius:10px;padding:12px;margin:10px 0;color:var(--red);font-size:13px;text-align:center}
        .success-box{background:rgba(0,255,136,0.1);border:1px solid var(--green);border-radius:10px;padding:12px;margin:10px 0;color:var(--green);font-size:13px;text-align:center}
        .hidden{display:none!important}
        .loading{display:inline-block;width:20px;height:20px;border:2px solid #333;border-top:2px solid var(--gold);border-radius:50%;animation:spin 0.8s linear infinite;margin-right:8px;vertical-align:middle}
        @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
        .timer-text{color:#ff6600;font-size:13px;text-align:center;margin-top:10px}
        .verify-input{text-align:center;font-size:26px!important;letter-spacing:6px!important;font-weight:700!important}
    </style>
</head>
<body>
<div class="bg-animation"><div class="bg-circle"></div><div class="bg-circle"></div><div class="bg-circle"></div></div>

<div id="loginContainer" class="container">
    <div class="logo">QANH</div>
    <p class="subtitle">Đăng nhập để tiếp tục</p>
    <div id="loginForm">
        <div class="input-group"><label>Email hoặc tên tài khoản</label><input type="text" id="loginUser" placeholder="Nhập email hoặc tên tài khoản..." autocomplete="off"></div>
        <div class="input-group"><label>Mật khẩu</label><input type="password" id="loginPass" placeholder="Nhập mật khẩu..." autocomplete="off"></div>
        <div class="captcha-box">
            <p style="color:#aaa;font-size:12px">Xác minh bạn không phải robot</p>
            <div class="captcha-text" id="captchaText"></div>
            <input type="text" id="captchaInput" placeholder="Nhập mã captcha..." maxlength="5" autocomplete="off">
            <button class="refresh-btn" onclick="generateCaptcha()">🔄 Đổi mã khác</button>
        </div>
        <button class="btn btn-gold" id="btnLogin" onclick="doLogin()">ĐĂNG NHẬP</button>
        <div id="loginMsg"></div>
        <p class="link-text">Chưa có tài khoản? <a onclick="showRegister()">Đăng ký ngay</a></p>
    </div>
</div>

<div id="registerContainer" class="container hidden">
    <div class="logo">QANH</div>
    <p class="subtitle">Tạo tài khoản mới</p>
    <div id="registerForm">
        <div class="input-group"><label>Email</label><input type="email" id="regEmail" placeholder="Nhập email..." autocomplete="off"></div>
        <div class="input-group"><label>Tên tài khoản</label><input type="text" id="regUsername" placeholder="Nhập tên tài khoản..." autocomplete="off"></div>
        <div class="input-group"><label>Mật khẩu</label><input type="password" id="regPass" placeholder="Ít nhất 6 ký tự..." autocomplete="off"></div>
        <div class="input-group"><label>Nhập lại mật khẩu</label><input type="password" id="regPass2" placeholder="Nhập lại mật khẩu..." autocomplete="off"></div>
        <div class="input-group"><label>Số điện thoại <span style="color:#667;font-size:11px">(không bắt buộc)</span></label><input type="tel" id="regPhone" placeholder="Nhập số điện thoại..." autocomplete="off"></div>
        <div class="captcha-box">
            <p style="color:#aaa;font-size:12px">Xác minh bạn không phải robot</p>
            <div class="captcha-text" id="captchaTextReg"></div>
            <input type="text" id="captchaInputReg" placeholder="Nhập mã captcha..." maxlength="5" autocomplete="off">
            <button class="refresh-btn" onclick="generateCaptchaReg()">🔄 Đổi mã khác</button>
        </div>
        <button class="btn btn-gold" id="btnRegister" onclick="doRegister()">ĐĂNG KÝ</button>
        <div id="regMsg"></div>
        <p class="link-text">Đã có tài khoản? <a onclick="showLogin()">Đăng nhập</a></p>
    </div>
    <div id="verifyEmailForm" class="hidden">
        <div style="text-align:center;font-size:50px;margin:10px 0">📧</div>
        <h3 style="color:var(--gold);text-align:center;margin:10px 0">Xác Minh Email</h3>
        <p style="color:#aabbcc;text-align:center;margin:15px 0;line-height:1.7">Mã xác minh <b style="color:var(--gold)">6 chữ số</b> đã gửi đến:<br><b style="color:var(--blue)" id="verifyEmailDisplay"></b></p>
        <input type="text" id="verifyCode" class="verify-input" placeholder="------" maxlength="6" autocomplete="off" style="width:100%;padding:14px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:#000;color:#fff">
        <p class="timer-text" id="verifyTimer">⏰ Còn 60 giây</p>
        <button class="btn btn-gold" id="btnVerify" onclick="verifyEmail()" style="margin-top:15px">XÁC NHẬN</button>
        <button class="btn" style="background:rgba(255,255,255,0.1);color:#fff;margin-top:8px;font-size:14px" onclick="resendCode()">📧 GỬI LẠI MÃ</button>
        <div id="verifyMsg"></div>
        <p class="link-text"><a onclick="showLogin()">← Quay lại đăng nhập</a></p>
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
function updateTimer(){var el=document.getElementById('verifyTimer');if(verifySeconds>10)el.innerHTML='⏰ Còn <b>'+verifySeconds+'</b> giây';else if(verifySeconds>0)el.innerHTML='⚠️ Còn <b style="color:#ff6600">'+verifySeconds+'</b> giây';}

function doLogin(){
    var user=document.getElementById('loginUser').value.trim(),pass=document.getElementById('loginPass').value.trim(),captcha=document.getElementById('captchaInput').value.trim(),msg=document.getElementById('loginMsg');
    if(!user||!pass||!captcha){msg.innerHTML='<div class="alert">⚠️ Điền đầy đủ!</div>';return;}
    if(captcha.toUpperCase()!==captchaAnswer){msg.innerHTML='<div class="alert">❌ Mã captcha không đúng!</div>';generateCaptcha();return;}
    var btn=document.getElementById('btnLogin');btn.disabled=true;btn.innerHTML='<span class="loading"></span> ĐANG ĐĂNG NHẬP...';msg.innerHTML='';
    fetch(API+'/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user:user,password:pass})})
    .then(function(r){return r.json()}).then(function(d){
        if(d.status==='success'){localStorage.setItem('qanh_user',JSON.stringify(d.user));msg.innerHTML='<div class="success-box">✅ Đăng nhập thành công!</div>';setTimeout(function(){window.location.href='/shop'},1000)}
        else{msg.innerHTML='<div class="alert">❌ '+(d.message||'Thất bại!')+'</div>';generateCaptcha();btn.disabled=false;btn.innerHTML='ĐĂNG NHẬP'}
    }).catch(function(){msg.innerHTML='<div class="alert">❌ Lỗi kết nối!</div>';btn.disabled=false;btn.innerHTML='ĐĂNG NHẬP'});
}

function doRegister(){
    var email=document.getElementById('regEmail').value.trim(),username=document.getElementById('regUsername').value.trim(),pass=document.getElementById('regPass').value.trim(),pass2=document.getElementById('regPass2').value.trim(),phone=document.getElementById('regPhone').value.trim(),captcha=document.getElementById('captchaInputReg').value.trim(),msg=document.getElementById('regMsg');
    if(!email||!username||!pass||!pass2||!captcha){msg.innerHTML='<div class="alert">⚠️ Điền đầy đủ!</div>';return;}
    if(pass!==pass2){msg.innerHTML='<div class="alert">❌ Mật khẩu không khớp!</div>';return;}
    if(pass.length<6){msg.innerHTML='<div class="alert">❌ Mật khẩu ít nhất 6 ký tự!</div>';return;}
    if(captcha.toUpperCase()!==captchaAnswerReg){msg.innerHTML='<div class="alert">❌ Mã captcha không đúng!</div>';generateCaptchaReg();return;}
    var btn=document.getElementById('btnRegister');btn.disabled=true;btn.innerHTML='<span class="loading"></span> ĐANG ĐĂNG KÝ...';msg.innerHTML='';
    fetch(API+'/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,username:username,password:pass,phone:phone})})
    .then(function(r){return r.json()}).then(function(d){
        if(d.status==='success'){pendingEmail=email;document.getElementById('verifyEmailDisplay').innerText=email;document.getElementById('registerForm').classList.add('hidden');document.getElementById('verifyEmailForm').classList.remove('hidden');document.getElementById('verifyCode').value='';document.getElementById('btnVerify').disabled=false;startVerifyTimer();document.getElementById('verifyMsg').innerHTML='<div class="success-box">✅ Mã 6 số đã gửi!</div>';}
        else{msg.innerHTML='<div class="alert">❌ '+(d.message||'Thất bại!')+'</div>';generateCaptchaReg();}
        btn.disabled=false;btn.innerHTML='ĐĂNG KÝ';
    }).catch(function(){msg.innerHTML='<div class="alert">❌ Lỗi kết nối!</div>';btn.disabled=false;btn.innerHTML='ĐĂNG KÝ'});
}

function verifyEmail(){
    var code=document.getElementById('verifyCode').value.trim(),msg=document.getElementById('verifyMsg');
    if(!code||code.length!==6){msg.innerHTML='<div class="alert">⚠️ Nhập đủ 6 chữ số!</div>';return;}
    if(verifySeconds<=0){msg.innerHTML='<div class="alert">❌ Mã hết hạn!</div>';return;}
    var btn=document.getElementById('btnVerify');btn.disabled=true;btn.innerHTML='<span class="loading"></span> ĐANG XÁC MINH...';
    fetch(API+'/api/verify-email',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:pendingEmail,code:code})})
    .then(function(r){return r.json()}).then(function(d){
        if(d.status==='success'){localStorage.setItem('qanh_user',JSON.stringify(d.user));clearInterval(verifyTimerInterval);msg.innerHTML='<div class="success-box">✅ Thành công!</div>';setTimeout(function(){window.location.href='/shop'},1500)}
        else{msg.innerHTML='<div class="alert">❌ '+(d.message||'Sai!')+'</div>';btn.disabled=false;btn.innerHTML='XÁC NHẬN'}
    }).catch(function(){msg.innerHTML='<div class="alert">❌ Lỗi!</div>';btn.disabled=false;btn.innerHTML='XÁC NHẬN'});
}

function resendCode(){
    if(!pendingEmail)return;
    var btn=document.getElementById('btnVerify');btn.disabled=true;btn.innerHTML='<span class="loading"></span> ĐANG GỬI...';document.getElementById('verifyCode').value='';
    fetch(API+'/api/resend-code',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:pendingEmail})})
    .then(function(r){return r.json()}).then(function(d){
        if(d.status==='success'){startVerifyTimer();document.getElementById('verifyMsg').innerHTML='<div class="success-box">✅ Đã gửi lại!</div>'}
        else{document.getElementById('verifyMsg').innerHTML='<div class="alert">❌ Lỗi!</div>'}
        btn.disabled=false;btn.innerHTML='XÁC NHẬN';
    });
}

generateCaptcha();generateCaptchaReg();
</script>
</body>
</html>"""

# ===== SHOP HTML =====
SHOP_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QANH SHOP - Key Uy Tín</title>
    <style>
        :root{--gold:#FFD700;--green:#00ff88;--red:#ff4757;--blue:#00d4ff;--purple:#a855f7;--bg:#0a0a1a;--card:#1a1a2e}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Segoe UI',Arial;color:#fff;min-height:100vh;background:var(--bg)}
        .navbar{position:sticky;top:0;z-index:100;background:rgba(10,10,26,0.9);backdrop-filter:blur(20px);padding:15px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,215,0,0.15);flex-wrap:wrap;gap:10px}
        .navbar .logo{font-size:24px;font-weight:700;background:linear-gradient(135deg,var(--gold),#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .navbar .balance{background:rgba(255,215,0,0.08);border:1px solid rgba(255,215,0,0.3);border-radius:25px;padding:8px 16px;color:var(--gold);font-weight:600;cursor:pointer;font-size:13px}
        .navbar .btn-nav{background:var(--gold);color:#000;border:none;border-radius:25px;padding:8px 20px;font-weight:700;cursor:pointer;font-size:13px;transition:0.3s}
        .navbar .btn-nav:hover{transform:scale(1.05)}
        .navbar .btn-admin{background:var(--purple);color:#fff}
        .container{max-width:520px;margin:0 auto;padding:25px 15px}
        .card{background:var(--card);border-radius:18px;padding:22px;margin-bottom:18px;border:1px solid rgba(255,255,255,0.06);transition:0.3s}
        .card:hover{border-color:rgba(255,215,0,0.2);transform:translateY(-2px);box-shadow:0 15px 40px rgba(0,0,0,0.4)}
        .card h2{color:var(--gold);margin-bottom:8px;font-size:18px;display:flex;align-items:center;gap:10px}
        .card .price{font-size:34px;font-weight:700;color:var(--gold)}
        .card .duration{color:#8899aa;margin:5px 0;font-size:13px}
        .card ul{list-style:none;margin:10px 0}
        .card ul li{padding:5px 0;color:#aabbcc;font-size:13px}
        .card ul li::before{content:"✦ ";color:var(--gold)}
        .btn-card{display:block;width:100%;padding:15px;border:none;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;text-align:center;margin-top:12px;transition:0.3s;text-transform:uppercase}
        .btn-card:hover{transform:translateY(-2px)}
        .btn-card:disabled{opacity:0.5;cursor:not-allowed;transform:none}
        .btn-green{background:linear-gradient(135deg,#00cc66,#009944);color:#fff;box-shadow:0 8px 25px rgba(0,200,100,0.25)}
        .btn-gold{background:linear-gradient(135deg,var(--gold),#FFA500);color:#000;box-shadow:0 8px 25px rgba(255,165,0,0.3)}
        .btn-blue{background:linear-gradient(135deg,#0077ff,#0055cc);color:#fff;box-shadow:0 8px 25px rgba(0,100,255,0.25)}
        .btn-purple{background:linear-gradient(135deg,#9933ff,#6600cc);color:#fff;box-shadow:0 8px 25px rgba(153,51,255,0.25)}
        .btn-recharge{background:linear-gradient(135deg,#00ff88,#00cc66);color:#000;font-size:17px;padding:16px;box-shadow:0 8px 25px rgba(0,255,136,0.3)}
        .badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:10px;font-weight:700;text-transform:uppercase}
        .badge-free{background:rgba(0,255,136,0.15);color:var(--green)}
        .badge-vip{background:rgba(255,215,0,0.15);color:var(--gold)}
        .badge-hot{background:rgba(255,102,0,0.15);color:#ff6600;animation:pulse 1.5s infinite}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.6}}
        select,input[type="text"]{width:100%;padding:13px 15px;margin:7px 0;border-radius:10px;border:2px solid rgba(255,255,255,0.08);background:#16213e;color:#fff;font-size:14px;transition:0.3s}
        select:focus,input:focus{border-color:var(--gold);outline:none}
        select option{background:#1a1a2e;color:#fff}
        .modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:1000;justify-content:center;align-items:center}
        .modal.active{display:flex}
        .modal-content{background:var(--card);border-radius:20px;padding:30px;width:90%;max-width:440px;text-align:center;max-height:85vh;overflow-y:auto;border:1px solid rgba(255,215,0,0.2);animation:modalIn 0.3s}
        @keyframes modalIn{from{opacity:0;transform:scale(0.9)translateY(20px)}to{opacity:1;transform:scale(1)translateY(0)}}
        .modal-content h3{color:var(--gold);margin-bottom:15px;font-size:22px}
        .close-btn{float:right;color:#889;font-size:26px;cursor:pointer;background:none;border:none}
        .close-btn:hover{color:#fff}
        .key-display{font-size:15px;color:var(--green);font-family:monospace;background:rgba(0,0,0,0.5);padding:18px;border-radius:12px;margin:15px 0;word-break:break-all;border:2px dashed rgba(0,255,136,0.4)}
        .copy-btn{background:var(--gold);color:#000;border:none;padding:14px;border-radius:12px;cursor:pointer;font-weight:700;font-size:16px;width:100%;margin-top:10px;text-transform:uppercase}
        .copy-btn:hover{background:#fff}
        .alert-box{background:rgba(255,71,87,0.1);border:1px solid var(--red);border-radius:12px;padding:14px;margin:10px 0;color:var(--red);font-size:13px}
        .success-box{background:rgba(0,255,136,0.1);border:1px solid var(--green);border-radius:12px;padding:14px;margin:10px 0;color:var(--green);font-size:13px}
        .loading{display:inline-block;width:24px;height:24px;border:3px solid rgba(255,255,255,0.1);border-top:3px solid var(--gold);border-radius:50%;animation:spin 0.8s linear infinite;margin:10px auto}
        @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
        .toast{position:fixed;top:20px;right:20px;z-index:10000;padding:14px 20px;border-radius:12px;color:#fff;font-weight:600;font-size:14px;animation:slideIn 0.4s}
        .toast-success{background:var(--green);color:#000}
        .toast-error{background:var(--red)}
        @keyframes slideIn{from{transform:translateX(120%)}to{transform:translateX(0)}}
        .info-text{color:#667788;font-size:12px;margin-top:8px;text-align:center}
        .hidden{display:none!important}
        .recharge-card{border-color:rgba(0,255,136,0.2)}
        .recharge-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--green),var(--blue))}
        .forever-card{box-shadow:0 0 30px rgba(255,215,0,0.1)}
    </style>
</head>
<body>
<div class="navbar">
    <div class="logo">QANH SHOP</div>
    <div class="user-info">
        <span class="balance" id="balanceDisplay" onclick="document.getElementById('rechargeSection').scrollIntoView({behavior:'smooth'})">💰 0đ</span>
        <button class="btn-nav" id="userBtn" onclick="logout()">👤 USER</button>
        <button class="btn-nav btn-admin hidden" id="adminBtn" onclick="showAdminModal()">⚙️ ADMIN</button>
    </div>
</div>

<div class="container">
    <div class="card recharge-card" id="rechargeSection" style="position:relative;overflow:hidden">
        <h2>💳 NẠP TIỀN VÀO TÀI KHOẢN</h2>
        <select id="rcType"><option value="">Chọn nhà mạng</option><option value="VIETTEL">📱 Viettel</option><option value="MOBIFONE">📱 Mobifone</option><option value="VINAPHONE">📱 Vinaphone</option></select>
        <select id="rcAmount"><option value="">Chọn mệnh giá</option><option value="10000">10.000đ</option><option value="20000">20.000đ</option><option value="50000">50.000đ</option><option value="100000">100.000đ</option><option value="200000">200.000đ</option><option value="500000">500.000đ</option></select>
        <input type="text" id="rcPin" placeholder="🔢 Nhập mã thẻ...">
        <input type="text" id="rcSerial" placeholder="📝 Nhập số serial...">
        <button class="btn-card btn-recharge" onclick="recharge()">💳 NẠP TIỀN NGAY</button>
        <div id="rcResult" style="margin-top:10px;text-align:center"></div>
    </div>

    <div class="card" style="border-color:rgba(0,255,136,0.3)">
        <h2>🆓 KEY FREE <span class="badge badge-free">MIỄN PHÍ</span></h2>
        <div class="price">0đ</div><div class="duration">⏰ 1 ngày</div>
        <ul><li>Dùng thử miễn phí</li><li>Tất cả tính năng cơ bản</li></ul>
        <button class="btn-card btn-green" onclick="window.open('/Getkey.php','_blank')">🎁 NHẬN KEY FREE</button>
        <p class="info-text">⚠️ Cần hoàn thành nhiệm vụ trên link4m</p>
    </div>

    <div class="card" style="border-color:rgba(168,85,247,0.3)">
        <h2>💎 KEY 1 TUẦN <span class="badge badge-hot">HOT</span></h2>
        <div class="price">50.000đ</div><div class="duration">⏰ 7 ngày</div>
        <ul><li>Tất cả tính năng VIP</li><li>Không giới hạn link</li></ul>
        <button class="btn-card btn-purple" onclick="buyKey('week')">💳 MUA NGAY</button>
    </div>

    <div class="card" style="border-color:rgba(0,132,255,0.3)">
        <h2>🔑 KEY 1 THÁNG <span class="badge badge-vip">VIP</span></h2>
        <div class="price">150.000đ</div><div class="duration">⏰ 30 ngày</div>
        <ul><li>Tất cả tính năng VIP</li><li>Hỗ trợ 24/7</li></ul>
        <button class="btn-card btn-blue" onclick="buyKey('month')">💳 MUA NGAY</button>
    </div>

    <div class="card forever-card" style="border-color:rgba(255,215,0,0.4)">
        <h2>👑 KEY VĨNH VIỄN <span class="badge badge-vip">PREMIUM</span></h2>
        <div class="price">250.000đ</div><div class="duration">⏰ Không giới hạn</div>
        <ul><li>Tất cả Premium</li><li>Update trọn đời</li></ul>
        <button class="btn-card btn-gold" onclick="buyKey('forever')">💳 MUA NGAY</button>
    </div>
</div>

<div class="modal" id="keyModal"><div class="modal-content">
    <span class="close-btn" onclick="document.getElementById('keyModal').classList.remove('active')">✕</span>
    <h3 style="color:var(--green)">✅ THÀNH CÔNG!</h3>
    <p id="keyMessage" style="color:#ccc;margin:10px 0"></p>
    <div class="key-display" id="keyDisplay"></div>
    <button class="copy-btn" onclick="copyKey()">📋 COPY KEY</button>
    <p class="info-text">💡 Dùng <b>/kichhoat KEY</b> trong bot Telegram</p>
</div></div>

<div class="modal" id="confirmBuyModal"><div class="modal-content">
    <span class="close-btn" onclick="document.getElementById('confirmBuyModal').classList.remove('active')">✕</span>
    <h3>⚠️ XÁC NHẬN MUA</h3>
    <div class="alert-box"><p><b id="confirmKeyType"></b></p><p>Giá: <b id="confirmKeyPrice"></b></p><p>Số dư: <b id="confirmBalance"></b></p></div>
    <button class="btn-card btn-gold" style="margin-top:5px" onclick="confirmBuy()">✅ XÁC NHẬN</button>
    <button class="btn-card" style="background:#444;color:#fff;margin-top:8px" onclick="document.getElementById('confirmBuyModal').classList.remove('active')">❌ HỦY</button>
</div></div>

<div class="modal" id="adminModal"><div class="modal-content">
    <span class="close-btn" onclick="document.getElementById('adminModal').classList.remove('active')">✕</span>
    <h3>⚙️ ADMIN</h3>
    <input type="text" id="adminTargetEmail" placeholder="📧 Email">
    <input type="number" id="adminSetBalance" placeholder="💰 Số dư">
    <button class="btn-card btn-gold" onclick="adminSetBalance()">💾 CẬP NHẬT</button>
    <hr style="border-color:rgba(255,255,255,0.1);margin:15px 0">
    <button class="btn-card btn-green" onclick="adminQuickFreeKey()">🎁 TẠO KEY FREE</button>
</div></div>

<script>
var API=window.location.origin;
var currentUser=null,pendingBuy=null;
var keyPrices={week:50000,month:150000,forever:250000};
var keyNames={week:'💎 KEY 1 TUẦN',month:'🔑 KEY 1 THÁNG',forever:'👑 KEY VĨNH VIỄN'};
try{currentUser=JSON.parse(localStorage.getItem('qanh_user'))||null;}catch(e){}
if(!currentUser){window.location.href='/login';}
function updateUI(){if(!currentUser)return;document.getElementById('userBtn').innerText='👤 '+currentUser.name;document.getElementById('balanceDisplay').innerText='💰 '+(currentUser.balance||0).toLocaleString()+'đ';if(currentUser.isAdmin)document.getElementById('adminBtn').classList.remove('hidden');}
function showToast(msg,type){var t=document.createElement('div');t.className='toast toast-'+(type||'success');t.innerText=msg;document.body.appendChild(t);setTimeout(function(){t.style.opacity='0';setTimeout(function(){t.remove()},300)},2500);}
function logout(){localStorage.removeItem('qanh_user');window.location.href='/login';}
function recharge(){
    if(!currentUser)return;
    var telco=document.getElementById('rcType').value,amount=parseInt(document.getElementById('rcAmount').value),pin=document.getElementById('rcPin').value.trim(),serial=document.getElementById('rcSerial').value.trim();
    if(!telco||!amount||!pin||!serial){showToast('⚠️ Điền đầy đủ!','error');return;}
    document.getElementById('rcResult').innerHTML='<div class="loading"></div><p style="color:var(--gold)">Đang xử lý...</p>';
    fetch('https://api.shoppay.vn/card/charge',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({partner_id:'70406595609',partner_key:'add9c7d61cb54ff1b447e2188c71a8c2',telco:telco,amount:amount,pin:pin,serial:serial})})
    .then(function(r){return r.json()}).then(function(d){
        if(d.status===1){currentUser.balance=(currentUser.balance||0)+amount;localStorage.setItem('qanh_user',JSON.stringify(currentUser));updateUI();document.getElementById('rcResult').innerHTML='<div class="success-box">✅ Nạp '+amount.toLocaleString()+'đ!</div>';document.getElementById('rcPin').value='';document.getElementById('rcSerial').value='';}
        else{document.getElementById('rcResult').innerHTML='<div class="alert-box">❌ '+(d.message||'Lỗi')+'</div>';}
    }).catch(function(){document.getElementById('rcResult').innerHTML='<div class="alert-box">❌ Lỗi kết nối!</div>';});
}
function buyKey(type){
    if(!currentUser)return;
    var price=keyPrices[type];
    if((currentUser.balance||0)<price){showToast('❌ Không đủ!','error');return;}
    pendingBuy=type;
    document.getElementById('confirmKeyType').innerText=keyNames[type];
    document.getElementById('confirmKeyPrice').innerText=price.toLocaleString()+'đ';
    document.getElementById('confirmBalance').innerText=(currentUser.balance||0).toLocaleString()+'đ';
    document.getElementById('confirmBuyModal').classList.add('active');
}
function confirmBuy(){
    if(!pendingBuy)return;
    var type=pendingBuy,price=keyPrices[type];pendingBuy=null;
    document.getElementById('confirmBuyModal').classList.remove('active');
    currentUser.balance-=price;localStorage.setItem('qanh_user',JSON.stringify(currentUser));updateUI();
    fetch(API+'/api/buy-key?type='+type).then(function(r){return r.json()}).then(function(d){
        if(d.status==='success'){document.getElementById('keyDisplay').innerText=d.key;document.getElementById('keyMessage').innerText='Mua '+keyNames[type]+' thành công!';document.getElementById('keyModal').classList.add('active');}
        else{currentUser.balance+=price;localStorage.setItem('qanh_user',JSON.stringify(currentUser));updateUI();}
    }).catch(function(){currentUser.balance+=price;localStorage.setItem('qanh_user',JSON.stringify(currentUser));updateUI();});
}
function copyKey(){var k=document.getElementById('keyDisplay').innerText;navigator.clipboard.writeText(k).then(function(){showToast('✅ Đã copy!')}).catch(function(){prompt('Copy:',k)});}
function showAdminModal(){if(!currentUser||!currentUser.isAdmin)return;document.getElementById('adminModal').classList.add('active');}
function adminSetBalance(){var e=document.getElementById('adminTargetEmail').value.trim(),a=parseInt(document.getElementById('adminSetBalance').value);if(!e||isNaN(a))return;fetch(API+'/api/admin-set-balance',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,amount:a})}).then(function(r){return r.json()}).then(function(d){showToast(d.message||'✅ OK!');document.getElementById('adminModal').classList.remove('active');});}
function adminQuickFreeKey(){document.getElementById('adminModal').classList.remove('active');fetch(API+'/api/create-key?type=free').then(function(r){return r.json()}).then(function(d){if(d.status==='success'){document.getElementById('keyDisplay').innerText=d.key;document.getElementById('keyMessage').innerText='Key Free Admin!';document.getElementById('keyModal').classList.add('active');}});}
updateUI();
</script>
</body>
</html>"""

# ===== GETKEY HTML =====
GETKEY_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nhận Key Free - QANH</title>
    <style>
        :root{--gold:#FFD700;--green:#00ff88;--bg:#0a0a1a;--card:#1a1a2e}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Segoe UI',Arial;color:#fff;min-height:100vh;background:var(--bg);display:flex;justify-content:center;align-items:center;padding:20px}
        .container{background:var(--card);border-radius:24px;padding:35px 30px;max-width:500px;width:100%;border:1px solid rgba(255,215,0,0.2);box-shadow:0 20px 60px rgba(0,0,0,0.5);text-align:center}
        .logo{font-size:30px;color:var(--gold);font-weight:700;margin-bottom:5px}
        .subtitle{color:#8899aa;margin-bottom:25px}
        .step-container{background:rgba(0,0,0,0.3);border-radius:16px;padding:22px;margin:15px 0;border:1px solid rgba(255,255,255,0.06)}
        .step-title{font-size:18px;color:var(--gold);margin-bottom:10px;font-weight:600}
        .step-desc{color:#aabbcc;font-size:14px;margin-bottom:15px;line-height:1.6}
        .key-display{font-size:18px;color:var(--green);font-family:monospace;background:rgba(0,0,0,0.5);padding:16px;border-radius:12px;margin:15px 0;border:2px dashed rgba(0,255,136,0.4);word-break:break-all}
        .btn{display:block;width:100%;padding:15px;border:none;border-radius:12px;font-size:16px;font-weight:700;cursor:pointer;text-align:center;margin:10px 0;transition:0.3s;text-transform:uppercase}
        .btn:hover:not(:disabled){transform:translateY(-2px)}
        .btn:disabled{opacity:0.5;cursor:not-allowed}
        .btn-gold{background:linear-gradient(135deg,#FFD700,#FFA500);color:#000}
        .btn-copy{background:linear-gradient(135deg,#00ff88,#00cc66);color:#000;font-size:18px}
        .hidden{display:none!important}
        .loading{display:inline-block;width:30px;height:30px;border:3px solid rgba(255,255,255,0.1);border-top:3px solid var(--gold);border-radius:50%;animation:spin 0.8s linear infinite;margin:10px}
        @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
        .step-indicator{display:flex;justify-content:center;gap:25px;margin:15px 0}
        .step-dot{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:18px;transition:0.3s}
        .step-dot.active{background:var(--gold);color:#000}
        .step-dot.done{background:var(--green);color:#fff}
        .step-dot.wait{background:rgba(255,255,255,0.08);color:#667}
        .info-text{color:#667788;font-size:12px;margin-top:10px}
    </style>
</head>
<body>
<div class="container">
    <div class="logo">⚡ QANH KEY</div>
    <p class="subtitle">Nhận Key Free cho Bot Telegram</p>
    <div class="step-indicator"><div class="step-dot active" id="dot1">1</div><div style="color:#556">→</div><div class="step-dot wait" id="dot2">2</div><div style="color:#556">→</div><div class="step-dot wait" id="dot3">✓</div></div>
    <div id="step1" class="step-container"><div class="step-title">📌 Bước 1: Xác Thực</div><div class="step-desc">Nhấn nút để mở link. <b>Hoàn thành nhiệm vụ</b> để nhận key.</div><button class="btn btn-gold" id="btnVerify" onclick="startVerify()">🔗 MỞ LINK XÁC THỰC</button></div>
    <div id="step2" class="step-container hidden"><div class="step-title">⏳ Bước 2: Đang Kiểm Tra</div><div class="step-desc">Đang chờ bạn hoàn thành nhiệm vụ...</div><div class="loading"></div><p style="color:#ff6600;font-size:13px">⚠️ Xem HẾT nội dung!</p><button class="btn btn-gold" disabled id="btnChecking">⏳ ĐANG KIỂM TRA...</button></div>
    <div id="step3" class="step-container hidden"><div class="step-title">✅ Bước 3: Nhận Key</div><div class="step-desc">Xác thực thành công!</div><div class="key-display" id="keyDisplay">...</div><button class="btn btn-copy" onclick="copyKey()">📋 COPY KEY</button><p class="info-text">💡 Dùng <b>/kichhoat KEY</b> trong bot</p></div>
</div>
<script>
var API=window.location.origin;var verifyToken=null,checkInterval=null,myKey=null;
function startVerify(){var btn=document.getElementById('btnVerify');btn.disabled=true;btn.innerText='⏳ ĐANG TẠO...';fetch(API+'/api/get-free-link?email=user_'+Date.now()).then(function(r){return r.json()}).then(function(d){if(d.status==='success'&&d.link4m){verifyToken=d.token;window.open(d.link4m,'_blank');document.getElementById('step1').classList.add('hidden');document.getElementById('step2').classList.remove('hidden');document.getElementById('dot1').className='step-dot done';document.getElementById('dot2').className='step-dot active';startCheck();}else{alert('Lỗi!');btn.disabled=false;btn.innerText='🔗 MỞ LINK';}}).catch(function(){btn.disabled=false;btn.innerText='🔗 MỞ LINK';});}
function startCheck(){var count=0;checkInterval=setInterval(function(){count++;fetch(API+'/api/check-verify?token='+verifyToken).then(function(r){return r.json()}).then(function(d){if(d.status==='verified'&&d.key){clearInterval(checkInterval);myKey=d.key;document.getElementById('step2').classList.add('hidden');document.getElementById('step3').classList.remove('hidden');document.getElementById('dot2').className='step-dot done';document.getElementById('dot3').className='step-dot active';document.getElementById('keyDisplay').innerText=d.key;}else if(count>=120){clearInterval(checkInterval);document.getElementById('btnChecking').disabled=false;document.getElementById('btnChecking').innerText='🔄 THỬ LẠI';document.getElementById('btnChecking').className='btn btn-gold';document.getElementById('btnChecking').onclick=function(){location.reload();};}});},5000);}
function copyKey(){if(!myKey)return;navigator.clipboard.writeText(myKey).then(function(){alert('✅ Đã copy!');}).catch(function(){prompt('Copy:',myKey);});}
</script>
</body>
</html>"""

# ===== ROUTES =====
@app.route('/')
@app.route('/login')
def login_page():
    return render_template_string(LOGIN_HTML)

@app.route('/shop')
def shop_page():
    return render_template_string(SHOP_HTML)

@app.route('/Getkey.php')
def getkey_page():
    return render_template_string(GETKEY_HTML)

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
        return jsonify({"status": "error", "message": "Mã hết hạn!"})
    if pending["code"] != code:
        return jsonify({"status": "error", "message": "Mã không đúng!"})
    users_db[email] = {"name": pending["username"], "email": email, "password": pending["password"], "phone": pending["phone"], "balance": 0, "isAdmin": False}
    del pending_registrations[email]
    return jsonify({"status": "success", "user": users_db[email]})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user_input = data.get('user', '').strip().lower()
    password = data.get('password', '')
    if user_input in ['admin@qanhshop.com', 'admin'] and password == 'QanhAdmin@2025#Secret!':
        return jsonify({"status": "success", "user": {"name": "Admin", "email": "admin@qanhshop.com", "balance": 999999999, "isAdmin": True}})
    for email, u in users_db.items():
        if email == user_input or u.get('name', '').lower() == user_input:
            if u['password'] == password:
                return jsonify({"status": "success", "user": u})
            return jsonify({"status": "error", "message": "Sai mật khẩu!"})
    return jsonify({"status": "error", "message": "Tài khoản không tồn tại!"})

@app.route('/api/buy-key')
def api_buy_key():
    key = generate_key()
    save_key_to_bot(key, request.args.get('type', 'week'))
    return jsonify({"status": "success", "key": key})

@app.route('/api/create-key')
def api_create_key():
    key = generate_key()
    save_key_to_bot(key, 'free')
    return jsonify({"status": "success", "key": key})

@app.route('/api/get-free-link')
def api_get_free_link():
    token = secrets.token_hex(16)
    callback_url = RENDER_URL + "/verify/" + token
    try:
        api_url = f"https://link4m.co/api-shorten/v2?api={LINK4M_API_KEY}&url={callback_url}"
        res = requests.get(api_url, timeout=10)
        link_data = res.json()
        if link_data.get('status') == 'success':
            pending_verify[token] = {"time": time(), "verified": False, "key": None}
            return jsonify({"status": "success", "link4m": link_data.get('shortenedUrl'), "token": token})
    except: pass
    return jsonify({"status": "error", "message": "Lỗi!"})

@app.route('/verify/<token>')
def verify_page(token):
    if token not in pending_verify: return "<h1>⚠️ Link không hợp lệ!</h1>", 404
    key = generate_key()
    save_key_to_bot(key, 'free')
    pending_verify[token]["verified"] = True
    pending_verify[token]["key"] = key
    return f"""<!DOCTYPE html><html><head><meta charset='UTF-8'><title>✅ Xác Thực</title>
<style>body{{background:#0a0a1a;color:#fff;text-align:center;padding:50px;font-family:'Segoe UI',Arial}}h2{{color:#0f0}}.key{{color:#0f0;background:rgba(0,0,0,0.5);padding:18px;border-radius:12px;border:2px dashed #0f0;font-family:monospace;font-size:18px;margin:15px 0}}button{{background:#0f0;color:#000;padding:14px 28px;border:none;border-radius:10px;font-weight:700;font-size:16px;cursor:pointer;margin:8px}}</style></head>
<body><h2>✅ HOÀN THÀNH NHIỆM VỤ!</h2><p>Cảm ơn bạn đã ủng hộ!</p><div class='key'>{key}</div>
<button onclick="navigator.clipboard.writeText('{key}')">📋 COPY KEY</button>
<p style='color:#889;margin-top:15px'>💡 Dùng <b>/kichhoat {key[:20]}...</b> trong bot</p></body></html>"""

@app.route('/api/check-verify')
def api_check_verify():
    token = request.args.get('token', '')
    if token in pending_verify and pending_verify[token].get("verified"):
        return jsonify({"status": "verified", "key": pending_verify[token]["key"]})
    return jsonify({"status": "pending"})

@app.route('/api/admin-set-balance', methods=['POST'])
def api_admin_set_balance():
    data = request.json
    email = data.get('email', '').strip().lower()
    amount = data.get('amount', 0)
    if email in users_db:
        users_db[email]['balance'] = amount
        return jsonify({"status": "success", "message": f"Đã cập nhật {email}: {amount}đ"})
    return jsonify({"status": "error", "message": "Không tìm thấy!"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)