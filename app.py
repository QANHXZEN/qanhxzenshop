from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json, os, secrets, string, requests
from datetime import datetime, timedelta
from time import time

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(32)

BOT_TOKEN = "8466851320:AAGc77X4DnPQRNkw7rVUhlpJVIcBlOcSlDA"
CHAT_ID = "8588555065"
OWNER_ID = 8588555065
LINK4M_API_KEY = "65c47d157fbdff4d79625e57"

def generate_key():
    c = string.ascii_uppercase + string.digits
    r = lambda l: ''.join(secrets.choice(c) for _ in range(l))
    return f"QANH-{r(10)}-{r(10)}-{r(10)}-{r(5)}"

pending_verify = {}

# ===== TRANG CHỦ SHOP =====
SHOP_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QANH SHOP - Key Uy Tín</title>
    <style>
        :root{--gold:#FFD700;--green:#00ff00;--red:#ff4444;--blue:#0088ff;--purple:#9933ff}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Segoe UI',Arial;color:#fff;min-height:100vh;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e)}
        .navbar{background:rgba(26,26,46,0.95);padding:15px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid var(--gold);flex-wrap:wrap;gap:10px}
        .navbar .logo{font-size:22px;font-weight:bold;color:var(--gold)}
        .navbar .balance{background:rgba(0,0,0,0.5);border:1px solid var(--gold);border-radius:20px;padding:8px 15px;color:var(--gold);font-weight:bold;cursor:pointer;font-size:14px}
        .navbar .btn-nav{background:var(--gold);color:#000;border:none;border-radius:20px;padding:8px 18px;font-weight:bold;cursor:pointer;font-size:13px}
        .navbar .btn-admin{background:var(--purple);color:#fff}
        .container{max-width:500px;margin:0 auto;padding:20px}
        .card{background:rgba(26,26,46,0.9);border-radius:15px;padding:20px;margin-bottom:15px;border:1px solid rgba(255,255,255,0.1);transition:0.3s}
        .card:hover{border-color:rgba(255,215,0,0.3)}
        .card h2{color:var(--gold);margin-bottom:10px;font-size:18px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
        .card .price{font-size:32px;font-weight:bold;color:var(--gold)}
        .card .duration{color:#aaa;margin:5px 0}
        .card ul{list-style:none;margin:10px 0}
        .card ul li{padding:4px 0;color:#ccc;font-size:14px}
        .card ul li::before{content:"✅ ";color:var(--green)}
        .btn-card{display:block;width:100%;padding:14px;border:none;border-radius:10px;font-size:16px;font-weight:bold;cursor:pointer;text-align:center;margin-top:10px;transition:0.3s}
        .btn-card:hover{opacity:0.9;transform:scale(1.02)}
        .btn-card:disabled{opacity:0.5;cursor:not-allowed}
        .btn-green{background:linear-gradient(135deg,#00cc00,#008800);color:#fff}
        .btn-gold{background:linear-gradient(135deg,#FFD700,#FFA500);color:#000}
        .btn-blue{background:linear-gradient(135deg,#0088cc,#004488);color:#fff}
        .btn-purple{background:linear-gradient(135deg,#9933ff,#6600cc);color:#fff}
        .btn-recharge{background:linear-gradient(135deg,#00ff88,#00cc66);color:#000;font-size:18px;padding:18px;font-weight:bold}
        .badge{padding:3px 10px;border-radius:20px;font-size:11px;font-weight:bold}
        .badge-free{background:#00cc00;color:#fff}
        .badge-vip{background:var(--gold);color:#000}
        .badge-hot{background:#ff6600;color:#fff;animation:pulse 1s infinite}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
        .hidden{display:none!important}
        .modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:1000;justify-content:center;align-items:center}
        .modal.active{display:flex}
        .modal-content{background:rgba(26,26,46,0.98);border-radius:15px;padding:25px;width:90%;max-width:420px;text-align:center;max-height:85vh;overflow-y:auto;border:1px solid var(--gold);animation:fadeIn 0.3s}
        @keyframes fadeIn{from{opacity:0;transform:scale(0.9)}to{opacity:1;transform:scale(1)}}
        .modal-content h3{color:var(--gold);margin-bottom:15px;font-size:20px}
        .modal-content input,.modal-content select{width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #333;background:#0f0f1f;color:#fff;font-size:14px}
        .close-btn{float:right;color:var(--gold);font-size:24px;cursor:pointer;background:none;border:none;padding:5px}
        .close-btn:hover{color:#fff}
        .key-display{font-size:14px;color:var(--green);font-family:monospace;background:#000;padding:15px;border-radius:8px;margin:10px 0;word-break:break-all;border:1px dashed var(--green)}
        .copy-btn{background:var(--gold);color:#000;border:none;padding:12px;border-radius:8px;cursor:pointer;font-weight:bold;font-size:16px;width:100%;margin-top:10px}
        .copy-btn:hover{background:#fff}
        .loading{display:inline-block;width:30px;height:30px;border:3px solid #333;border-top:3px solid var(--gold);border-radius:50%;animation:spin 1s linear infinite;margin:10px auto}
        @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
        .alert-box{background:rgba(255,0,0,0.1);border:1px solid var(--red);border-radius:10px;padding:15px;margin:10px 0;color:var(--red)}
        .success-box{background:rgba(0,255,0,0.1);border:1px solid var(--green);border-radius:10px;padding:15px;margin:10px 0;color:var(--green)}
        .info-text{color:#888;font-size:12px;margin-top:10px}
        .toast{position:fixed;top:20px;right:20px;z-index:10000;padding:15px 20px;border-radius:10px;color:#fff;font-weight:bold;max-width:350px;animation:slideIn 0.5s}
        .toast-success{background:#00cc00}.toast-error{background:#ff4444}
        @keyframes slideIn{from{transform:translateX(100%)}to{transform:translateX(0)}}
        .user-info{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
    </style>
</head>
<body>
<div class="navbar">
    <div class="logo">⚡ QANH SHOP</div>
    <div class="user-info">
        <span class="balance" id="balanceDisplay">💰 0đ</span>
        <button class="btn-nav" id="authBtn" onclick="showAuthModal()">🔑 ĐĂNG NHẬP</button>
        <button class="btn-nav btn-admin hidden" id="adminBtn" onclick="showAdminModal()">⚙️ ADMIN</button>
    </div>
</div>
<div class="container">
    <!-- NẠP TIỀN -->
    <div class="card" style="border-color:#00ff88;border-width:2px" id="rechargeSection">
        <h2>💳 NẠP TIỀN VÀO TÀI KHOẢN</h2>
        <select id="rcType"><option value="">Chọn nhà mạng</option><option value="VIETTEL">📱 Viettel</option><option value="MOBIFONE">📱 Mobifone</option><option value="VINAPHONE">📱 Vinaphone</option></select>
        <select id="rcAmount"><option value="">Chọn mệnh giá</option><option value="10000">10.000đ</option><option value="20000">20.000đ</option><option value="50000">50.000đ</option><option value="100000">100.000đ</option><option value="200000">200.000đ</option><option value="500000">500.000đ</option></select>
        <input type="text" id="rcPin" placeholder="🔢 Nhập mã thẻ...">
        <input type="text" id="rcSerial" placeholder="📝 Nhập số serial...">
        <button class="btn-card btn-recharge" id="btnRecharge" onclick="recharge()">💳 NẠP TIỀN NGAY</button>
        <div id="rcResult" style="margin-top:10px"></div>
    </div>

    <!-- KEY FREE -->
    <div class="card" style="border-color:#00cc00">
        <h2>🆓 KEY FREE <span class="badge badge-free">MIỄN PHÍ</span></h2>
        <div class="price">0đ</div><div class="duration">⏰ 1 ngày</div>
        <ul><li>Dùng thử miễn phí</li><li>Tất cả tính năng cơ bản</li></ul>
        <button class="btn-card btn-green" id="btnFreeKey" onclick="window.open('/Getkey.php','_blank')">🎁 NHẬN KEY FREE</button>
        <p class="info-text">⚠️ Cần hoàn thành nhiệm vụ trên link4m để nhận key</p>
    </div>

    <!-- KEY 1 TUẦN -->
    <div class="card" style="border-color:#9933ff">
        <h2>💎 KEY 1 TUẦN <span class="badge badge-hot">HOT</span></h2>
        <div class="price">50.000đ</div><div class="duration">⏰ 7 ngày</div>
        <ul><li>Tất cả tính năng VIP</li><li>Không giới hạn link</li><li>Tốc độ cao</li></ul>
        <button class="btn-card btn-purple" id="btnWeek" onclick="buyKey('week')">💳 MUA NGAY</button>
    </div>

    <!-- KEY 1 THÁNG -->
    <div class="card" style="border-color:#0088cc">
        <h2>🔑 KEY 1 THÁNG <span class="badge badge-vip">VIP</span></h2>
        <div class="price">150.000đ</div><div class="duration">⏰ 30 ngày</div>
        <ul><li>Tất cả tính năng VIP</li><li>Hỗ trợ 24/7</li><li>Ưu tiên xử lý</li></ul>
        <button class="btn-card btn-blue" id="btnMonth" onclick="buyKey('month')">💳 MUA NGAY</button>
    </div>

    <!-- KEY VĨNH VIỄN -->
    <div class="card" style="border-color:#FFD700">
        <h2>👑 KEY VĨNH VIỄN <span class="badge badge-vip">PREMIUM</span></h2>
        <div class="price">250.000đ</div><div class="duration">⏰ Không giới hạn</div>
        <ul><li>Tất cả Premium</li><li>Update trọn đời</li><li>Hỗ trợ VIP</li></ul>
        <button class="btn-card btn-gold" id="btnForever" onclick="buyKey('forever')">💳 MUA NGAY</button>
    </div>
</div>

<!-- MODAL ĐĂNG NHẬP -->
<div class="modal" id="authModal"><div class="modal-content">
    <span class="close-btn" onclick="document.getElementById('authModal').classList.remove('active')">✕</span>
    <h3>🔑 ĐĂNG NHẬP / ĐĂNG KÝ</h3>
    <input type="text" id="authEmail" placeholder="📧 Email của bạn">
    <input type="password" id="authPassword" placeholder="🔒 Mật khẩu">
    <button class="btn-card btn-gold" id="btnAuth" onclick="doAuth()">🔓 ĐĂNG NHẬP / ĐĂNG KÝ</button>
    <p class="info-text">Nếu chưa có tài khoản, hệ thống sẽ tự động đăng ký</p>
</div></div>

<!-- MODAL KEY -->
<div class="modal" id="keyModal"><div class="modal-content">
    <span class="close-btn" onclick="document.getElementById('keyModal').classList.remove('active')">✕</span>
    <h3 style="color:#0f0">✅ THÀNH CÔNG!</h3>
    <p id="keyMessage"></p>
    <div class="key-display" id="keyDisplay"></div>
    <button class="copy-btn" id="btnCopy" onclick="copyKey()">📋 COPY KEY</button>
    <p class="info-text">💡 Dùng lệnh <b>/kichhoat KEY</b> trong bot Telegram</p>
</div></div>

<!-- MODAL XÁC NHẬN MUA -->
<div class="modal" id="confirmBuyModal"><div class="modal-content">
    <span class="close-btn" onclick="document.getElementById('confirmBuyModal').classList.remove('active')">✕</span>
    <h3>⚠️ XÁC NHẬN MUA KEY</h3>
    <div class="alert-box">
        <p><b id="confirmKeyType"></b></p>
        <p>Giá: <b id="confirmKeyPrice"></b></p>
        <p>Số dư: <b id="confirmBalance"></b></p>
        <p style="color:#ff4444">⚠️ Giao dịch không thể hoàn lại!</p>
    </div>
    <button class="btn-card btn-gold" id="btnConfirmBuy" onclick="confirmBuy()">✅ XÁC NHẬN MUA</button>
    <button class="btn-card" style="background:#555;color:#fff;margin-top:5px" onclick="document.getElementById('confirmBuyModal').classList.remove('active')">❌ HỦY</button>
</div></div>

<!-- MODAL ADMIN -->
<div class="modal" id="adminModal"><div class="modal-content">
    <span class="close-btn" onclick="document.getElementById('adminModal').classList.remove('active')">✕</span>
    <h3>⚙️ ADMIN PANEL</h3>
    <p style="color:#aaa;margin-bottom:10px">Quản lý người dùng và tạo key</p>
    <input type="text" id="adminTargetEmail" placeholder="📧 Email người dùng cần chỉnh...">
    <input type="number" id="adminSetBalance" placeholder="💰 Số dư mới...">
    <button class="btn-card btn-gold" id="btnAdminSet" onclick="adminSetBalance()">💾 CẬP NHẬT SỐ DƯ</button>
    <hr style="border-color:#333;margin:15px 0">
    <button class="btn-card btn-green" id="btnAdminKey" onclick="adminQuickFreeKey()">🎁 TẠO KEY FREE NHANH</button>
</div></div>

<script>
var API = window.location.origin;
var currentUser = null;
var userKeys = [];
var userRecharges = [];
var allUsers = [];
var pendingBuy = null;
var keyPrices = {week:50000, month:150000, forever:250000};
var keyNames = {week:'💎 KEY 1 TUẦN', month:'🔑 KEY 1 THÁNG', forever:'👑 KEY VĨNH VIỄN'};
var keyDurations = {week:'7 NGÀY VIP', month:'30 NGÀY VIP', forever:'VĨNH VIỄN'};

// Load data
try {
    currentUser = JSON.parse(localStorage.getItem('qanh_user')) || null;
    userKeys = JSON.parse(localStorage.getItem('qanh_keys')) || [];
    userRecharges = JSON.parse(localStorage.getItem('qanh_recharges')) || [];
    allUsers = JSON.parse(localStorage.getItem('qanh_all_users')) || [];
} catch(e) { currentUser = null; userKeys = []; userRecharges = []; allUsers = []; }

function saveAll() {
    try {
        if (currentUser) localStorage.setItem('qanh_user', JSON.stringify(currentUser));
        localStorage.setItem('qanh_keys', JSON.stringify(userKeys));
        localStorage.setItem('qanh_recharges', JSON.stringify(userRecharges));
        localStorage.setItem('qanh_all_users', JSON.stringify(allUsers));
    } catch(e) {}
}

function updateUI() {
    if (!currentUser) {
        document.getElementById('authBtn').innerText = '🔑 ĐĂNG NHẬP';
        document.getElementById('balanceDisplay').innerText = '💰 0đ';
        document.getElementById('adminBtn').classList.add('hidden');
    } else {
        document.getElementById('authBtn').innerText = '👤 ' + (currentUser.name || 'User');
        document.getElementById('balanceDisplay').innerText = '💰 ' + (currentUser.balance || 0).toLocaleString() + 'đ';
        if (currentUser.isAdmin) {
            document.getElementById('adminBtn').classList.remove('hidden');
        } else {
            document.getElementById('adminBtn').classList.add('hidden');
        }
    }
}

function showToast(msg, type) {
    var t = document.createElement('div');
    t.className = 'toast toast-' + (type || 'success');
    t.innerText = msg;
    document.body.appendChild(t);
    setTimeout(function() { t.style.opacity = '0'; t.style.transition = 'opacity 0.5s'; setTimeout(function() { t.remove(); }, 500); }, 2500);
}

function showAuthModal() {
    if (currentUser) {
        if (confirm('Bạn muốn đăng xuất?')) {
            currentUser = null;
            localStorage.removeItem('qanh_user');
            updateUI();
            showToast('👋 Đã đăng xuất!');
        }
        return;
    }
    document.getElementById('authEmail').value = '';
    document.getElementById('authPassword').value = '';
    document.getElementById('authModal').classList.add('active');
}

function doAuth() {
    var email = document.getElementById('authEmail').value.trim();
    var pass = document.getElementById('authPassword').value.trim();
    
    if (!email || !pass) { showToast('⚠️ Vui lòng điền đầy đủ!', 'error'); return; }
    
    // Admin check
    if (email === 'admin@qanhshop.com' && pass === 'QanhAdmin@2025#Secret!') {
        currentUser = {name: 'Admin', email: email, password: pass, balance: 999999999, isAdmin: true};
        saveAll();
        document.getElementById('authModal').classList.remove('active');
        updateUI();
        showToast('✅ Đăng nhập Admin thành công!');
        return;
    }
    
    // Normal user
    var found = false;
    for (var i = 0; i < allUsers.length; i++) {
        if (allUsers[i].email === email) {
            if (allUsers[i].password !== pass) { showToast('❌ Sai mật khẩu!', 'error'); return; }
            currentUser = allUsers[i];
            found = true;
            break;
        }
    }
    if (!found) {
        currentUser = {name: email.split('@')[0], email: email, password: pass, balance: 0, isAdmin: false};
        allUsers.push(currentUser);
    }
    
    saveAll();
    document.getElementById('authModal').classList.remove('active');
    updateUI();
    showToast('✅ Thành công!');
}

// ===== NẠP TIỀN =====
function recharge() {
    if (!currentUser) { showToast('⚠️ Vui lòng đăng nhập!', 'error'); showAuthModal(); return; }
    
    var telco = document.getElementById('rcType').value;
    var amount = parseInt(document.getElementById('rcAmount').value);
    var pin = document.getElementById('rcPin').value.trim();
    var serial = document.getElementById('rcSerial').value.trim();
    
    if (!telco || !amount || !pin || !serial) {
        showToast('⚠️ Vui lòng điền đầy đủ thông tin thẻ!', 'error');
        return;
    }
    
    document.getElementById('rcResult').innerHTML = '<div class="loading"></div><p style="color:var(--gold)">Đang xử lý thẻ...</p>';
    
    fetch('https://api.shoppay.vn/card/charge', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            partner_id: '70406595609',
            partner_key: 'add9c7d61cb54ff1b447e2188c71a8c2',
            telco: telco,
            amount: amount,
            pin: pin,
            serial: serial
        })
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.status === 1) {
            currentUser.balance = (currentUser.balance || 0) + amount;
            for (var i = 0; i < allUsers.length; i++) {
                if (allUsers[i].email === currentUser.email) {
                    allUsers[i].balance = currentUser.balance;
                    break;
                }
            }
            userRecharges.unshift({type: telco, amount: amount, time: new Date().toLocaleString(), status: '✅ OK'});
            saveAll();
            updateUI();
            document.getElementById('rcResult').innerHTML = '<div class="success-box">✅ Nạp thành công ' + amount.toLocaleString() + 'đ!</div>';
            document.getElementById('rcPin').value = '';
            document.getElementById('rcSerial').value = '';
            showToast('✅ Nạp tiền thành công!', 'success');
        } else {
            document.getElementById('rcResult').innerHTML = '<div class="alert-box">❌ ' + (data.message || 'Thẻ không hợp lệ!') + '</div>';
            showToast('❌ ' + (data.message || 'Lỗi'), 'error');
        }
    })
    .catch(function() {
        document.getElementById('rcResult').innerHTML = '<div class="alert-box">❌ Lỗi kết nối, thử lại sau!</div>';
        showToast('❌ Lỗi kết nối!', 'error');
    });
}

// ===== MUA KEY =====
function buyKey(type) {
    if (!currentUser) { showToast('⚠️ Vui lòng đăng nhập!', 'error'); showAuthModal(); return; }
    
    var price = keyPrices[type];
    if ((currentUser.balance || 0) < price) {
        showToast('❌ Không đủ tiền! Cần ' + price.toLocaleString() + 'đ', 'error');
        return;
    }
    
    pendingBuy = type;
    document.getElementById('confirmKeyType').innerText = keyNames[type];
    document.getElementById('confirmKeyPrice').innerText = price.toLocaleString() + 'đ';
    document.getElementById('confirmBalance').innerText = (currentUser.balance || 0).toLocaleString() + 'đ';
    document.getElementById('confirmBuyModal').classList.add('active');
}

function confirmBuy() {
    if (!pendingBuy) return;
    
    var type = pendingBuy;
    var price = keyPrices[type];
    pendingBuy = null;
    document.getElementById('confirmBuyModal').classList.remove('active');
    
    // Trừ tiền
    currentUser.balance -= price;
    for (var i = 0; i < allUsers.length; i++) {
        if (allUsers[i].email === currentUser.email) {
            allUsers[i].balance = currentUser.balance;
            break;
        }
    }
    saveAll();
    updateUI();
    
    // Gọi API tạo key
    fetch(API + '/api/buy-key?type=' + type)
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.status === 'success') {
            userKeys.unshift({
                key: data.key,
                type: keyNames[type],
                duration: keyDurations[type],
                time: new Date().toLocaleString()
            });
            saveAll();
            document.getElementById('keyDisplay').innerText = data.key;
            document.getElementById('keyMessage').innerText = 'Mua ' + keyNames[type] + ' thành công!';
            document.getElementById('keyModal').classList.add('active');
            showToast('✅ Mua key thành công!', 'success');
        } else {
            // Hoàn tiền
            currentUser.balance += price;
            for (var i = 0; i < allUsers.length; i++) {
                if (allUsers[i].email === currentUser.email) {
                    allUsers[i].balance = currentUser.balance;
                    break;
                }
            }
            saveAll();
            updateUI();
            showToast('❌ Lỗi tạo key!', 'error');
        }
    })
    .catch(function() {
        // Hoàn tiền
        currentUser.balance += price;
        for (var i = 0; i < allUsers.length; i++) {
            if (allUsers[i].email === currentUser.email) {
                allUsers[i].balance = currentUser.balance;
                break;
            }
        }
        saveAll();
        updateUI();
        showToast('❌ Lỗi kết nối!', 'error');
    });
}

// ===== COPY KEY =====
function copyKey() {
    var key = document.getElementById('keyDisplay').innerText;
    if (navigator.clipboard) {
        navigator.clipboard.writeText(key).then(function() {
            showToast('✅ Đã copy key! Dùng /kichhoat ' + key.substring(0, 20) + '...');
        }).catch(function() {
            prompt('📋 Copy key:', key);
        });
    } else {
        prompt('📋 Copy key:', key);
    }
}

// ===== ADMIN =====
function showAdminModal() {
    if (!currentUser || !currentUser.isAdmin) return;
    document.getElementById('adminTargetEmail').value = '';
    document.getElementById('adminSetBalance').value = '';
    document.getElementById('adminModal').classList.add('active');
}

function adminSetBalance() {
    var email = document.getElementById('adminTargetEmail').value.trim();
    var amount = parseInt(document.getElementById('adminSetBalance').value);
    
    if (!email || isNaN(amount) || amount < 0) {
        showToast('⚠️ Vui lòng điền đầy đủ!', 'error');
        return;
    }
    
    var found = false;
    for (var i = 0; i < allUsers.length; i++) {
        if (allUsers[i].email === email) {
            allUsers[i].balance = amount;
            found = true;
            break;
        }
    }
    
    if (found) {
        saveAll();
        showToast('✅ Đã cập nhật số dư cho ' + email + ': ' + amount.toLocaleString() + 'đ', 'success');
        document.getElementById('adminModal').classList.remove('active');
    } else {
        showToast('❌ Không tìm thấy người dùng!', 'error');
    }
}

function adminQuickFreeKey() {
    if (!currentUser || !currentUser.isAdmin) return;
    document.getElementById('adminModal').classList.remove('active');
    
    fetch(API + '/api/create-key?type=free')
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.status === 'success') {
            userKeys.unshift({key: data.key, type: '🆓 FREE (Admin)', duration: '1 NGÀY', time: new Date().toLocaleString()});
            saveAll();
            document.getElementById('keyDisplay').innerText = data.key;
            document.getElementById('keyMessage').innerText = 'Key Free Admin!';
            document.getElementById('keyModal').classList.add('active');
            showToast('✅ Tạo key thành công!');
        }
    });
}

// Init
updateUI();
</script>
</body>
</html>"""

# ===== TRANG GET KEY FREE =====
GETKEY_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nhận Key Free - QANH BOT</title>
    <style>
        :root{--gold:#FFD700;--green:#00ff00;--red:#ff4444;--blue:#00d4ff}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Segoe UI',Arial;color:#fff;min-height:100vh;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);display:flex;justify-content:center;align-items:center;padding:20px}
        .container{background:rgba(26,26,46,0.95);border-radius:20px;padding:30px;max-width:500px;width:100%;border:2px solid var(--gold);box-shadow:0 0 30px rgba(255,215,0,0.2);text-align:center}
        .logo{font-size:28px;color:var(--gold);font-weight:bold;margin-bottom:5px;text-shadow:0 0 10px rgba(255,215,0,0.5)}
        .subtitle{color:#aaa;margin-bottom:20px;font-size:14px}
        .step-container{background:rgba(0,0,0,0.3);border-radius:15px;padding:20px;margin:15px 0;border:1px solid rgba(255,255,255,0.1)}
        .step-title{font-size:18px;color:var(--gold);margin-bottom:10px}
        .step-desc{color:#ccc;font-size:14px;margin-bottom:15px;line-height:1.5}
        .timer-box{background:rgba(0,0,0,0.5);border:2px solid var(--blue);border-radius:10px;padding:15px;margin:15px 0}
        .key-display{font-size:18px;color:#00ff00;font-family:monospace;background:rgba(0,0,0,0.7);padding:15px;border-radius:10px;margin:15px 0;border:2px dashed #00ff00;word-break:break-all}
        .btn{display:block;width:100%;padding:14px;border:none;border-radius:10px;font-size:16px;font-weight:bold;cursor:pointer;text-align:center;margin:10px 0;transition:0.3s}
        .btn:hover:not(:disabled){transform:scale(1.02);opacity:0.9}
        .btn:disabled{opacity:0.5;cursor:not-allowed}
        .btn-gold{background:linear-gradient(135deg,#FFD700,#FFA500);color:#000}
        .btn-green{background:linear-gradient(135deg,#00cc00,#008800);color:#fff}
        .btn-copy{background:linear-gradient(135deg,#00ff88,#00cc66);color:#000;font-size:18px}
        .hidden{display:none!important}
        .alert{background:rgba(255,0,0,0.1);border:1px solid var(--red);border-radius:10px;padding:15px;margin:10px 0;color:var(--red)}
        .success{background:rgba(0,255,0,0.1);border:1px solid var(--green);border-radius:10px;padding:15px;margin:10px 0;color:var(--green)}
        .info-text{color:#888;font-size:12px;margin-top:10px}
        .loading{display:inline-block;width:30px;height:30px;border:3px solid #333;border-top:3px solid var(--gold);border-radius:50%;animation:spin 1s linear infinite;margin:10px}
        @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
        .step-indicator{display:flex;justify-content:center;gap:20px;margin:15px 0}
        .step-dot{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:18px}
        .step-dot.active{background:var(--gold);color:#000}
        .step-dot.done{background:#00cc00;color:#fff}
        .step-dot.wait{background:rgba(255,255,255,0.1);color:#aaa}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">⚡ QANH KEY SYSTEM</div>
        <p class="subtitle">Nhận Key Free cho Bot Telegram</p>
        
        <div class="step-indicator">
            <div class="step-dot active" id="dot1">1</div>
            <div style="color:#aaa">→</div>
            <div class="step-dot wait" id="dot2">2</div>
            <div style="color:#aaa">→</div>
            <div class="step-dot wait" id="dot3">✓</div>
        </div>

        <div id="step1" class="step-container">
            <div class="step-title">📌 Bước 1: Xác Thực</div>
            <div class="step-desc">Nhấn nút bên dưới để mở link xác thực. Bạn cần <b>hoàn thành nhiệm vụ</b> để nhận key.</div>
            <button class="btn btn-gold" id="btnVerify" onclick="startVerify()">🔗 MỞ LINK XÁC THỰC</button>
            <p class="info-text">Link sẽ mở trong tab mới</p>
        </div>

        <div id="step2" class="step-container hidden">
            <div class="step-title">⏳ Bước 2: Đang Kiểm Tra</div>
            <div class="step-desc">Đang chờ bạn hoàn thành nhiệm vụ trên link4m...</div>
            <div class="timer-box">
                <div class="loading"></div>
                <p style="color:#ff6600;font-size:13px;margin-top:10px">⚠️ Vui lòng xem HẾT nội dung trên tab vừa mở!</p>
            </div>
            <button class="btn btn-gold" disabled id="btnChecking">⏳ ĐANG KIỂM TRA...</button>
        </div>

        <div id="step3" class="step-container hidden">
            <div class="step-title">✅ Bước 3: Nhận Key</div>
            <div class="step-desc">Xác thực thành công! Key của bạn đã sẵn sàng.</div>
            <div class="key-display" id="keyDisplay">Đang tạo key...</div>
            <button class="btn btn-copy" onclick="copyKey()">📋 COPY KEY</button>
            <p class="info-text">💡 Dùng lệnh <b>/kichhoat KEY</b> trong bot Telegram</p>
        </div>
    </div>

    <script>
        var API = window.location.origin;
        var verifyToken = null;
        var checkInterval = null;
        var myKey = null;

        function startVerify() {
            var btn = document.getElementById('btnVerify');
            btn.disabled = true;
            btn.innerText = '⏳ ĐANG TẠO LINK...';
            
            fetch(API + '/api/get-free-link?email=user_' + Date.now())
            .then(function(res) { return res.json(); })
            .then(function(data) {
                if (data.status === 'success' && data.link4m) {
                    verifyToken = data.token;
                    window.open(data.link4m, '_blank');
                    
                    document.getElementById('step1').classList.add('hidden');
                    document.getElementById('step2').classList.remove('hidden');
                    document.getElementById('dot1').className = 'step-dot done';
                    document.getElementById('dot2').className = 'step-dot active';
                    
                    startCheck();
                } else {
                    alert('Lỗi: ' + (data.message || 'Không thể tạo link!'));
                    btn.disabled = false;
                    btn.innerText = '🔗 MỞ LINK XÁC THỰC';
                }
            })
            .catch(function() {
                alert('Lỗi kết nối! Vui lòng thử lại.');
                btn.disabled = false;
                btn.innerText = '🔗 MỞ LINK XÁC THỰC';
            });
        }

        function startCheck() {
            var count = 0;
            checkInterval = setInterval(function() {
                count++;
                fetch(API + '/api/check-verify?token=' + verifyToken)
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.status === 'verified' && data.key) {
                        clearInterval(checkInterval);
                        myKey = data.key;
                        
                        document.getElementById('step2').classList.add('hidden');
                        document.getElementById('step3').classList.remove('hidden');
                        document.getElementById('dot2').className = 'step-dot done';
                        document.getElementById('dot3').className = 'step-dot active';
                        document.getElementById('keyDisplay').innerText = data.key;
                    } else if (count >= 120) {
                        clearInterval(checkInterval);
                        document.getElementById('btnChecking').disabled = false;
                        document.getElementById('btnChecking').innerText = '🔄 THỬ LẠI';
                        document.getElementById('btnChecking').className = 'btn btn-gold';
                        document.getElementById('btnChecking').onclick = function() { location.reload(); };
                    }
                });
            }, 5000);
        }

        function copyKey() {
            if (!myKey) return;
            navigator.clipboard.writeText(myKey).then(function() {
                alert('✅ Đã copy Key! Dùng /kichhoat ' + myKey.substring(0, 20) + '...');
            }).catch(function() {
                prompt('Copy key:', myKey);
            });
        }
    </script>
</body>
</html>"""

# ===== ROUTES =====
@app.route('/')
def index():
    return render_template_string(SHOP_HTML)

@app.route('/Getkey.php')
def getkey_page():
    return render_template_string(GETKEY_HTML)

@app.route('/api/buy-key')
def api_buy_key():
    key_type = request.args.get('type', 'week')
    key = generate_key()
    
    # Gửi key cho bot Telegram
    try:
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                json={'chat_id': CHAT_ID, 'text': f'KEY:{key}:TYPE:{key_type}'}, timeout=5)
    except: pass
    
    return jsonify({"status": "success", "key": key})

@app.route('/api/create-key')
def api_create_key():
    key = generate_key()
    try:
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                json={'chat_id': CHAT_ID, 'text': f'KEY:{key}:TYPE:free'}, timeout=5)
    except: pass
    return jsonify({"status": "success", "key": key})

@app.route('/api/get-free-link')
def api_get_free_link():
    email = request.args.get('email', 'user')
    token = secrets.token_hex(16)
    callback_url = "https://qanhxzenshop.onrender.com/verify/" + token
    
    try:
        api_url = f"https://link4m.co/api-shorten/v2?api={LINK4M_API_KEY}&url={callback_url}"
        res = requests.get(api_url, timeout=10)
        link_data = res.json()
        if link_data.get('status') == 'success':
            pending_verify[token] = {"email": email, "time": time(), "verified": False, "key": None}
            return jsonify({"status": "success", "link4m": link_data.get('shortenedUrl'), "token": token})
        return jsonify({"status": "error", "message": "Lỗi tạo link!"})
    except: return jsonify({"status": "error", "message": "Lỗi kết nối!"})

@app.route('/verify/<token>')
def verify_page(token):
    if token not in pending_verify: return "<h1>⚠️ Link không hợp lệ!</h1>", 404
    key = generate_key()
    
    try:
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                json={'chat_id': CHAT_ID, 'text': f'KEY:{key}:TYPE:free'}, timeout=5)
    except: pass
    
    pending_verify[token]["verified"] = True
    pending_verify[token]["key"] = key
    
    return f"""<!DOCTYPE html><html><head><meta charset='UTF-8'><title>✅ Xác Thực Thành Công</title>
<style>body{{background:#0f0c29;color:#fff;text-align:center;padding:50px;font-family:'Segoe UI',Arial}}h2{{color:#0f0}}.key{{color:#0f0;background:#000;padding:15px;border-radius:10px;border:1px dashed #0f0;font-family:monospace;font-size:18px}}button{{background:#0f0;color:#000;padding:12px 25px;border:none;border-radius:8px;font-weight:bold;font-size:16px;margin:10px;cursor:pointer}}</style></head>
<body><h2>✅ HOÀN THÀNH NHIỆM VỤ!</h2><p>Cảm ơn bạn đã ủng hộ!</p><div class='key'>{key}</div>
<button onclick="navigator.clipboard.writeText('{key}')">📋 COPY KEY</button>
<p style='color:#aaa;margin-top:15px'>💡 Dùng <b>/kichhoat {key[:20]}...</b> trong bot Telegram</p></body></html>"""

@app.route('/api/check-verify')
def api_check_verify():
    token = request.args.get('token', '')
    if token in pending_verify and pending_verify[token].get("verified"):
        return jsonify({"status": "verified", "key": pending_verify[token]["key"]})
    return jsonify({"status": "pending"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)