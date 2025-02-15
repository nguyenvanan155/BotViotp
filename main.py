from telebot import apihelper,telebot
import requests
import sqlite3
from datetime import datetime, timedelta
import hashlib
import random
import string
import time 
import os
import io
from multiprocessing import Process
from flask import Flask
from threading import Thread

# Tạo Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

# Chạy Flask server trên một luồng khác
def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

request_data = {}
user_processes = {}
#app = Flask(__name__)

TOKEN = "8056358169:AAHAdMrwlrwgoEYXeP4o2R-IiTo-u3pfTdI"
ADMIN_LIST = [5201276631, 2112221324]

bot = telebot.TeleBot(TOKEN,threaded=True)


conn = sqlite3.connect('userdata.db')
c = conn.cursor()

# 
c.execute('''CREATE TABLE IF NOT EXISTS user_info
             (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, username TEXT, first_name TEXT, last_name TEXT ,warn INTEGER DEFAULT 0, usertoken TEXT, last_bill TEXT,time_use INTEGER DEFAULT 0,role TEXT DEFAULT 'Member')''')

conn.commit()
#DEF 

def handle_messages(chat_id):
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(e)

def start_message_handler(chat_id):
    if chat_id not in user_processes:
        user_process = Process(target=handle_messages, args=(chat_id,))
        user_process.daemon = True
        user_process.start()
        user_processes[chat_id] = user_process
def rndom():
    random_so = ''.join(random.choice('123456789') for _ in range(6))
    return random_so
def add_balance(user_id, amount):
    conn = sqlite3.connect('userdata.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM user_info WHERE user_id=?", (user_id,))
    user_record = c.fetchone()

    if user_record is None:
        return False

    current_balance = user_record[0]
    new_balance = current_balance + amount

    c.execute("UPDATE user_info SET balance=? WHERE user_id=?", (new_balance, user_id))
    conn.commit()
    return True
def get_user_info(user_id):
    conn = sqlite3.connect('userdata.db')
    c = conn.cursor()
    c.execute("SELECT first_name, last_name, balance, warn, usertoken, last_bill, time_use, role  FROM user_info WHERE user_id=?", (user_id,))
    user_record = c.fetchone()
    conn.close()
    return user_record
    
def read_token():
    with open("token.txt", 'r') as file:
        tokens = file.readlines()
    return [token.strip() for token in tokens]
def remove_token(token):
    with open("token.txt", 'r') as file:
        lines = file.readlines()
    with open("token.txt", 'w') as file:
        for line in lines:
            if line.strip() != token:
                file.write(line)
                
def read_services():
    services = {}
    with open('dichvu.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            # 
            if ':' in line:
                service_id, price, name = line.strip().split(':', 2)
                services[int(service_id)] = {'price': int(price), 'name': name}
    return services

def find_services_by_name(file_path, prefix):
    matched_services = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                service_data = line.strip().split(':')
                if len(service_data) == 3:
                    service_id = service_data[0]
                    service_price = service_data[1]
                    service_name = service_data[2]
                    if service_name.lower().startswith(prefix.lower()):
                        matched_services.append((service_id, service_name, service_price))
    except FileNotFoundError:
        print("File not found.")
    return matched_services
    
    
services = read_services()


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        bot.reply_to(message, "Bot Service SMS VanAn OTP\nĐể Sử Dụng Vui Lòng Đăng Ký Bằng Lệnh /register\nDùng Lệnh /cmd Để Xem Danh Sách Lệnh.")
    except Exception as e:
        print(e)

@bot.message_handler(commands=['cmd'])
def handle_help(message):
    try:
        user_id = message.from_user.id
        if 1==1:
            bot.send_message(message.chat.id, "𝗔𝗹𝗹 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗙𝗼𝗿 𝗩𝗮𝗻An\n--------------------------\n/register:Đăng Ký Dịch Vụ OTP\n/sms {id}: Thuê Số Theo Id\n/find {tên dịch vụ}: Tìm ID Với Tên Dịch Vụ\n/user: Kiểm Tra Tài Khoản\n/topup {Số Tiền Cần Nạp}: Nạp Tiền\n/free Lấy GiftCode Nhận Tiền\n/key: Nhập Code")
            if user_id == ADMIN_LIST:
                bot.send_message(message.chat.id, "𝑨𝒅𝒎𝒊𝒏 𝑪𝒐𝒎𝒎𝒂𝒏𝒅\n--------------------------\n/add {user id} {amount}: Add Tiền\n/addtoken {token} add token vafo file token\n/db : BackUp DataBase\nreply/warn: Warn (chưa làm xong)\nreply/ban Ban (chưa làm xong)\n/addcode {code} {amount} {số lượng}: add giftcode nhận xèng (chưa làm xong") 
    except Exception as e:
        print(e)
@bot.message_handler(commands=['register'])
def handle_register(message):
    try:
        user_id = message.from_user.id
        conn = sqlite3.connect('userdata.db')
        c = conn.cursor()
        # Kiểm tra xem người dùng đã đăng ký chưa
        c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id,))
        conn.commit()
        user_data = c.fetchone()
        
        if user_data is None:
            # Nếu người dùng chưa đăng ký, thêm thông tin của họ vào cơ sở dữ liệu
            username = message.from_user.username
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name
            c.execute("INSERT OR REPLACE INTO user_info (user_id, balance, username, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                      (user_id, 0, username, first_name, last_name))
            conn.commit()
            bot.send_message(message.chat.id, f"Account created successfully\nID của bạn là {user_id}\nFirst Name: {first_name}\nBanlance: 0")
            conn.close()
        else:
            # Nếu người dùng đã đăng ký, thông báo rằng họ đã được đăng ký trước đó
            bot.send_message(message.chat.id, "Bạn đã được đăng ký trước đó!")
        conn.close()
    except Exception as e:
        print(e)
@bot.message_handler(commands=['user'])
def handle_user_command(message):
    try:
        user_id = message.from_user.id
        user_info = get_user_info(user_id)

        if user_info:
            if user_info[0] and user_info[1]:
                full_name = f"{user_info[0]} {user_info[1]}"
            elif user_info[0]:
                full_name = f"{user_info[0]}"
            elif user_info[1]:
                full_name = f"{user_info[1]}"
            balance = user_info[2]
            role = user_info[7]
            warn = user_info[3]
            
            
            reply = f"ID của {full_name} là {user_id}\nID chat là {message.chat.id}\nFull Name: {full_name}\nBalance: {balance}\nRole:{role}\nWarning:{warn}"
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, "Không tìm thấy thông tin người dùng.")
        
    except Exception as e:
        print(e)
        
@bot.message_handler(commands=['add'])
def handle_add_command(message):
    user_id = message.from_user.id
    if user_id == ADMIN_LIST:
        tokens = message.text.split()
        if len(tokens) != 3:
            bot.reply_to(message, "Lệnh không hợp lệ. Sử dụng lệnh theo định dạng: /add {user_id} {số tiền}")
            return
        user_id = int(tokens[1])
        amount = int(tokens[2])

        if add_balance(user_id, amount):
            bot.reply_to(message, f"Đã thêm {amount} vào balance của user: {user_id}.")
        else:
            bot.reply_to(message, "Thêm số tiền không thành công. Người dùng không tồn tại.")
    else:
        bot.reply_to(message, "Access denied!❌❌❌")

@bot.message_handler(commands=['db'])
def handle_add_command(message):
    user_id = message.from_user.id
    if user_id == ADMIN_LIST:
        try:
            # 
            with open('userdata.db', 'rb') as db_file:
                # Gửi file cho người dùng
                bot.send_document(message.chat.id, db_file)
            with open('token.txt', 'rb') as db_file:
               
                bot.send_document(message.chat.id, db_file)
        except Exception as e:
            bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")

@bot.message_handler(commands=['topup'])
def handle_topup_command(message):
    try:
        user_id = message.from_user.id
        conn = sqlite3.connect('userdata.db')
        c = conn.cursor()
        c.execute("SELECT balance,last_bill,username FROM user_info WHERE user_id=?", (user_id,))
        user_record = c.fetchone()
        if user_record is None:
            bot.send_message(message.chat.id, "Bạn chưa đăng ký. Vui lòng đăng ký bằng lệnh /register để sử dụng dịch vụ.")
            conn.close()
            return
        tokens = message.text.split()
        if len(tokens) == 1:
            bot.reply_to(message, "Lệnh không hợp lệ. Sử dụng lệnh theo định dạng: /topup {số tiền}\nNạp Dưới 20.000 VND Sẽ Duyệt Bằng Cơm")
            return
        elif len(tokens) == 2:
            amount = int(tokens[1])
            amountt = amount
        else:
            bot.reply_to(message, "Lệnh không hợp lệ. Sử dụng lệnh theo định dạng: /topup {số tiền}")
            return
        if str(amount).isdigit() and int(amount) >= 0:
            pass
        else:
            return
        user_id = message.from_user.id
        username= user_record[2]
        # 
        url = f"https://img.vietqr.io/image/MBBank-9815052005-compact2.jpg?amount={amount}&addInfo={user_id}&accountName=NguyenVanAn"
        response = requests.get(url)

        if response.status_code == 200:
            with open(f"topup_{user_id}.jpg", "wb") as file:
                file.write(response.content)
            file_path = f"topup_{user_id}.jpg"
            bot.send_photo(message.chat.id, open(f"topup_{user_id}.jpg", "rb"))
            os.remove(file_path)
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            amountz = amount * 1.65
            notification_message = f"Thông Báo Tạo Hoá Đơn Nạp Tiền\nNgười Dùng: {user_id} @{username}\nPhương Thức Nạp: Bank\nNạp: {amount}\nThời Gian Request: {current_time}"
            bot.send_message(message.chat.id, f"Tạo Hóa Đơn Nạp Tiền Thành Công\nSố Tiền: {amount} Thực Nhận: {amountz}\nNếu Sau 10p Tiền Chưa Được Cộng Vào Tài Khoản,Vui Lòng Inbox Admin: @eldrie15 !")
            bot.send_message(-1001922603443, notification_message)
            time.sleep(1)
            tgian = datetime.now()
            tgiann = tgian.strftime("%Y-%m-%d")
            url = "https://oauth.casso.vn/v2/transactions"
            params = {
                "fromDate": f"{tgiann}",
                "page": 1,
                "pageSize": 5,
                "sort": "DESC"
            }

            headers = {
                "Authorization": "Apikey AK_CS.450fc7b0f3e011ee99422ffea38dbc17.tJT1X0bboGgkvAa1ZI6xlZATHYWj7op2ZC9AM1EapdbCdf5GeLwnSiygyIII8xih9NQqnGUU",
                "Content-Type": "application/json",
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
            }


            response = requests.get(url, params=params, headers=headers)
            data = response.json()


            start_time = time.time()
            chk=1
            ndck= f"Thanh toan QR-{user_id}"
            last_bill = user_record[1]
            print (ndck,last_bill)
            while True:
                time.sleep(2)
                response = requests.get(url, params=params, headers=headers)
                data = response.json()
                current_time = time.time()
                elapsed_time = current_time - start_time
                if 'data' in data and data['data'] is not None and 'records' in data['data'] and data['data']['records'] is not None:
                    records = data['data']['records']
                    for record in records:
                        amount = record['amount']
                        description = record['description']
                        bill = record['tid']
                        print(amount,description,bill)
                        if (ndck == description or str(user_id) == description or str(user_id) in description) and bill != last_bill and amount==amountt:
                            add_balance(user_id, amountz)
                            c.execute("UPDATE user_info SET last_bill=? WHERE user_id=?", (bill, user_id))
                            conn.commit()
                            bot.reply_to(message, f"Đã nạp thành công {amountz} vào tài khoản của bạn.")
                            chk=0
                            bot.send_message(-1001922603443, f"Đã nạp thành công {amountz} vào tài khoản của {user_id}")
                            break
                        elif bill == last_bill:
                            print("dcm")
                            break
                if chk==0:
                    break
                if elapsed_time >= 300:
                    break
                time.sleep(15)
    except Exception as e:
        print(e)
        bot.reply_to(message, "Đã xảy ra lỗi khi tạo hoá đơn nạp tiền.Vui Lòng Thử Lại Sau")
        

@bot.message_handler(commands=['find'])
def handle_find(message):
    try:
        # 
        command, keyword = message.text.split(' ', 1)
        prefix = keyword
        if prefix:
            zz = ""
            services = find_services_by_name("dichvu.txt", prefix)
            sent_message = bot.reply_to(message, "Đang Tìm Kiếm...")
            # 
            if sent_message:
                if services:
                    for service in services:
                        id, name, price = service  # Unpack service tuple
                        zz += f"Id:{id} Tên: {name} Giá: {price}\n"
                    bot.edit_message_text(chat_id=sent_message.chat.id, message_id=sent_message.message_id, text=f"{zz}")
                else:
                    bot.edit_message_text(chat_id=sent_message.chat.id, message_id=sent_message.message_id, text="Không tìm thấy dịch vụ phù hợp.\nId:276 Tên: OTHER -DV KHÁC Giá: 5400")
            else:
                bot.send_message(message.chat.id, "Đã xảy ra lỗi khi gửi tin nhắn.")
        else:
            bot.send_message(message.chat.id, "Sử dụng lệnh /find theo cú pháp: /find {id}")
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Sử dụng lệnh /find theo cú pháp: /find {id}")

@bot.message_handler(commands=['addtoken'])
def add_token(message):
    if message.from_user.id == ADMIN_LIST:
           
        new_token = message.text.split(' ', 1)[1].strip()
            
            
        with open('tokens.txt', 'a') as token_file:
            token_file.write(new_token + '\n')

@bot.message_handler(commands=['tokenbalance'])
def check_balance_token(message):
    user_id = message.from_user.id
    if user_id == ADMIN_LIST:
        sent_message = bot.reply_to(message, text='PLS Wait')
        tokens = read_token()
        j = 0
        loi = 0
        live = 0
        sodu = 0

        #
        with io.open("token_balance.txt", "w", encoding="utf-8") as file:
            for token in tokens:
                j += 1
                response = requests.get(f"https://api.viotp.com/users/balance?token={token}")
                balance_data = response.json()
                if int(balance_data["status_code"]) == 401:
                    loi += 1
                    file.write(f"Token:{j}, Trạng Thái: Lỗi Xác Thực\n")
                    remove_token(token)
                    continue
                if int(balance_data["status_code"]) == -1:
                    loi += 1
                    file.write(f"Token:{j}, Trạng Thái: Lỗi\n")
                    continue
                user_balance = balance_data["data"]["balance"]
                live= live+1
                sodu=sodu+user_balance
                file.write(f"Token:{j} Trạng Thái: Live Balance: {user_balance}\n")

        # 
        with open("token_balance.txt", "rb") as file:
            bot.send_document(message.chat.id, file)

        bot.send_message(message.chat.id, f"Tổng {j}\nLive: {live} Lỗi: {loi}\nBalance:{sodu}\n")

@bot.message_handler(commands=['sms'])
def handle_sms(message):
    try:
        conn = sqlite3.connect('userdata.db')
        c = conn.cursor()
        user_id = message.from_user.id
        command = message.text.split()
        if len(command) != 2:
            bot.send_message(message.chat.id, "Sử dụng lệnh /sms theo cú pháp: /sms {id}")
            return
        
        service_id = int(command[1])
        
        # 
        if service_id not in services:
            bot.send_message(message.chat.id, "Dịch vụ không tồn tại.")
            return
        
        chabiettenbien = services[service_id]
        name = chabiettenbien['name']
        price = chabiettenbien['price']
        #
        if user_id == ADMIN_LIST:
            pass
        else:
            #
            conn = sqlite3.connect('userdata.db')
            c = conn.cursor()
            c.execute("SELECT balance FROM user_info WHERE user_id=?", (user_id,))
            user_record = c.fetchone()
            if user_record is None:
                bot.send_message(message.chat.id, "Bạn chưa đăng ký. Vui lòng đăng ký để sử dụng dịch vụ.")
                conn.close()
                return
            balance = user_record[0]
            
            if balance < price:
                bot.send_message(message.chat.id, "Bạn không đủ tiền để gửi tin nhắn.")
                conn.close()
                return
            new_balance = balance - price
            c.execute("UPDATE user_info SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()
        tokens = read_token()
        for token in tokens:
            response = requests.get(f"https://api.viotp.com/users/balance?token={token}")
            balance_data = response.json()
            if int(balance_data["status_code"]) == 401:
                remove_token(token)
                continue
            if int(balance_data["status_code"]) == -1:
                continue
            user_balance = balance_data["data"]["balance"]
            if user_balance >= price:
                break
        else:
            bot.reply_to(message, "Admin Hết Tiền Rồi, Vui Lòng Thử Lại Sau")
        
        
        response = requests.get(f"https://api.viotp.com/request/getv2?token={token}&serviceId={service_id}")
        request_data = response.json()
        
        if request_data["status_code"] != 200:
            bot.reply_to(message, "Có lỗi xảy ra khi gửi yêu cầu tin nhắn.")
            return
        
        re_phone_number = request_data["data"]["re_phone_number"]
        request_id = request_data["data"]["request_id"]

        sent_message = bot.reply_to(message, f"╔══*.·:·.✧ ✦ ✧.·:·.*══╗\n║💸𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗥𝗲𝗻𝘁𝗲𝗱 𝗢𝗧𝗣\n║Dịch Vụ: <b>{name}</b>\n║💲Giá : {price}\n╠✲꘏ ꘏ ꘏ ꘏ ꘏ ꘏ ꘏✲\n║📲Số điện thoại: <code>{re_phone_number}</code>\n║🔢ID : <code>{request_id}</code>\n║Đang Chờ Tin Nhắn...\n╚══*.·:·.✧ ✦ ✧.·:·.*══╝", parse_mode="HTML")

        # 
        status = 0
        while status != 1:
            response = requests.get(f"https://api.viotp.com/session/getv2?requestId={request_id}&token={token}")
            #print(response.text())
            session_data = response.json()
            status = session_data["data"]["Status"]
            if status == 1:
                sms_content = session_data["data"]["SmsContent"] 
                codee = session_data["data"]["Code"]
                bot.edit_message_text(chat_id=sent_message.chat.id, message_id=sent_message.message_id,text=f"╔══*.·:·.✧ ✦ ✧.·:·.*══╗\n║💸𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗥𝗲𝗻𝘁𝗲𝗱 𝗢𝗧𝗣\n║Dịch Vụ: <b>{name}</b>\n║💲Giá : {price}\n╠✲꘏ ꘏ ꘏ ꘏ ꘏ ꘏ ꘏✲\n║📲Số điện thoại: <code>{re_phone_number}</code>\n║🔢ID : <code>{request_id}</code>\n║📩Mã của bạn là: <code>{codee}</code>\n║✉️<i>{sms_content}</i>\n╚══*.·:·.✧ ✦ ✧.·:·.*══╝", parse_mode="HTML")
                break
            elif status==2:
                bot.edit_message_text(chat_id=sent_message.chat.id, message_id=sent_message.message_id,text=f"╔══*.·:·.✧ ✦ ✧.·:·.*══╗\n║💸𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗥𝗲𝗻𝘁𝗲𝗱 𝗢𝗧𝗣\n║Dịch Vụ: <b>{name}</b>\n║💲Giá : {price}\n╠✲꘏ ꘏ ꘏ ꘏ ꘏ ꘏ ꘏✲\n║📲Số điện thoại: <code>{re_phone_number}</code>\n║🔢ID : <code>{request_id}</code>\n║Hết Hạn Thuê OTP\n╚══*.·:·.✧ ✦ ✧.·:·.*══╝", parse_mode="HTML")
                bot.send_message(message.chat.id, f"Expried!!")
                c.execute("SELECT balance FROM user_info WHERE user_id=?", (user_id,))
                user_record = c.fetchone()
                zzbalance = user_record[0] + price
                c.execute("UPDATE user_info SET balance=? WHERE user_id=?", (zzbalance, user_id))
                conn.commit()
                conn.close()
                break
    except Exception as e:
        print(e)
       
@bot.message_handler(commands=['resms'])
def re_sms(message):
    try:
        conn = sqlite3.connect('userdata.db')
        c = conn.cursor()
        
        user_id = message.from_user.id
        command = message.text.split()
        
        if len(command) != 3:
            bot.send_message(message.chat.id, "Sử dụng lệnh /resms theo cú pháp: /resms {id dich vu} {phone}")
            return
        
        try:
            service_id = int(command[1])
            phone = command[2]
        except ValueError:
            bot.send_message(message.chat.id, "Vui lòng nhập đúng định dạng cho {id dich vu} và {phone} (cả hai phải là số nguyên).")
            return
        
        # In ra các giá trị để kiểm tra
        print(f"Service ID: {service_id}")
        print(f"Phone: {phone}")
        # 
        if service_id not in services:
            bot.send_message(message.chat.id, "Dịch vụ không tồn tại.")
            return
        print("cc")
        chabiettenbien = services[service_id]
        name = chabiettenbien['name']
        price = chabiettenbien['price']
        #
        if user_id == ADMIN_LIST:
            pass
        else:
            #
            conn = sqlite3.connect('userdata.db')
            c = conn.cursor()
            c.execute("SELECT balance FROM user_info WHERE user_id=?", (user_id,))
            user_record = c.fetchone()
            if user_record is None:
                bot.send_message(message.chat.id, "Bạn chưa đăng ký. Vui lòng đăng ký để sử dụng dịch vụ.")
                conn.close()
                return
            balance = user_record[0]
            
            if balance < price:
                bot.send_message(message.chat.id, "Bạn không đủ tiền để gửi tin nhắn.")
                conn.close()
                return
            new_balance = balance - price
            c.execute("UPDATE user_info SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()
        tokens = read_token()
        for token in tokens:
            response = requests.get(f"https://api.viotp.com/request/getv2?token={token}&serviceId={service_id}&number={phone}")
            balance_data = response.json()
            if int(balance_data["status_code"]) == 401:
                remove_token(token)
                continue
            if int(balance_data["status_code"]) == 200:
                re_phone_number = request_data["data"]["re_phone_number"]
                request_id = request_data["data"]["request_id"]

                sent_message = bot.reply_to(message, f"╔══*.·:·.✧ ✦ ✧.·:·.*══╗\n║💸𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗥𝗲𝗻𝘁𝗲𝗱 𝗢𝗧𝗣\n║Dịch Vụ: <b>{name}</b>\n║💲Giá : {price}\n╠✲꘏ ꘏ ꘏ ꘏ ꘏ ꘏ ꘏✲\n║📲Số điện thoại: <code>{re_phone_number}</code>\n║🔢ID : <code>{request_id}</code>\n║Đang Chờ Tin Nhắn...\n╚══*.·:·.✧ ✦ ✧.·:·.*══╝", parse_mode="HTML")

                # 
                status = 0
                while status != 1:
                    response = requests.get(f"https://api.viotp.com/session/getv2?requestId={request_id}&token={token}")
                    #print(response.text())
                    session_data = response.json()
                    status = session_data["data"]["Status"]
                    if status == 1:
                        sms_content = session_data["data"]["SmsContent"] 
                        codee = session_data["data"]["Code"]
                        bot.edit_message_text(chat_id=sent_message.chat.id, message_id=sent_message.message_id,text=f"╔══*.·:·.✧ ✦ ✧.·:·.*══╗\n║💸𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗥𝗲𝗻𝘁𝗲𝗱 𝗢𝗧𝗣\n║Dịch Vụ: <b>{name}</b>\n║💲Giá : {price}\n╠✲꘏ ꘏ ꘏ ꘏ ꘏ ꘏ ꘏✲\n║📲Số điện thoại: <code>{re_phone_number}</code>\n║🔢ID : <code>{request_id}</code>\n║📩Mã của bạn là: <code>{codee}</code>\n║✉️<i>{sms_content}</i>\n╚══*.·:·.✧ ✦ ✧.·:·.*══╝", parse_mode="HTML")
                        break
                    elif status==2:
                        bot.edit_message_text(chat_id=sent_message.chat.id, message_id=sent_message.message_id,text=f"╔══*.·:·.✧ ✦ ✧.·:·.*══╗\n║💸𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗥𝗲𝗻𝘁𝗲𝗱 𝗢𝗧𝗣\n║Dịch Vụ: <b>{name}</b>\n║💲Giá : {price}\n╠✲꘏ ꘏ ꘏ ꘏ ꘏ ꘏ ꘏✲\n║📲Số điện thoại: <code>{re_phone_number}</code>\n║🔢ID : <code>{request_id}</code>\n║Hết Hạn Thuê OTP\n╚══*.·:·.✧ ✦ ✧.·:·.*══╝", parse_mode="HTML")
                        bot.send_message(message.chat.id, f"Expried!!")
                        c.execute("SELECT balance FROM user_info WHERE user_id=?", (user_id,))
                        user_record = c.fetchone()
                        zzbalance = user_record[0] + price
                        c.execute("UPDATE user_info SET balance=? WHERE user_id=?", (zzbalance, user_id))
                        conn.commit()
                        conn.close()
                        break
    except Exception as e:
        print(e)
#

@bot.message_handler(commands=['free'])
def laykey(message):
    try:
        user_id = message.from_user.id
        conn = sqlite3.connect('userdata.db')
        c = conn.cursor()
        c.execute("SELECT time_use FROM user_info WHERE user_id=?", (user_id,))
        user_record = c.fetchone()
        if user_record is None:
            bot.send_message(message.chat.id, "Bạn chưa đăng ký. Vui lòng đăng ký bằng lệnh /register để sử dụng dịch vụ.")
            conn.close()
            return
        sent_message = bot.reply_to(message, text='PLS Wait')
        
        saltrandom= rndom()
        c.execute("UPDATE user_info SET time_use=? WHERE user_id=?", (saltrandom, user_id))
        conn.commit()
        conn.close()
        string = f'GL-{user_id}+{saltrandom}'
        hash_object = hashlib.md5(string.encode())
        try:    
            key = str(hash_object.hexdigest())
            print(key)
            url_note = requests.get(f'https://web1s.com/note-api?token=b8770924-2643-4491-8ab1-d3cc5f820530&content={key}&title=VuotLink').json()['shortenedUrl']
            print(url_note)
            url_key = requests.get(f'https://web1s.com/api?token=d4174244-758c-4f97-9f83-9b9758b436a5&url={url_note}').json()['shortenedUrl']
            print(url_key)
            textx = f'''
- LINK KEY:{url_key} 
- DÙNG LỆNH /key {{key}} ĐỂ NHẬP KEY
- VƯỢT LINK NGẪU NHIÊN NHẬN TỪ 500-5000
            '''
        except Exception as e:
            print(e)
        bot.edit_message_text(chat_id=sent_message.chat.id, message_id=sent_message.message_id,text= textx)
    except Exception as e:
        print(e)

@bot.message_handler(commands=['key'])
def key(message):
    try:
        user_id = message.from_user.id
        conn = sqlite3.connect('userdata.db')
        c = conn.cursor()
        c.execute("SELECT balance,time_use FROM user_info WHERE user_id=?", (user_id,))
        user_record = c.fetchone()
        if user_record is None:
            bot.send_message(message.chat.id, "Bạn chưa đăng ký. Vui lòng đăng ký bằng lệnh /register để sử dụng dịch vụ.")
            conn.close()
            return
        if len(message.text.split()) == 1:
            bot.reply_to(message, 'Cú Pháp Nhập Key Là /key {{key bạn vừa get}}')
            return
        saltrnd= user_record[1]

        key = message.text.split()[1]
        username = message.from_user.username
        string = f'GL-{user_id}+{saltrnd}'
        hash_object = hashlib.md5(string.encode())
        expected_key = str(hash_object.hexdigest())
        if key == expected_key:
            conn = sqlite3.connect('userdata.db')
            c = conn.cursor()
            c.execute("SELECT balance FROM user_info WHERE user_id=?", (user_id,))
            user_record = c.fetchone()
            sodu = random.randint(500, 1499)
            sodu2 =user_record[0] + sodu
            c.execute("UPDATE user_info SET balance=? WHERE user_id=?", (sodu2, user_id))
            conn.commit()
            conn.close()
            bot.reply_to(message, f'Thành Công.Bạn Được Thêm {sodu} Vào Tài Khoản')
        else:
            bot.reply_to(message, 'Lỗi: Key Sai Hoặc Đã Được Sử Dụng, Vui Lòng Thử Lại')
    except Exception as e:
        print(e)

apihelper.RETRY_ON_ERROR = True

if __name__ == '__main__':
    keep_alive()  # Giữ bot chạy liên tục
    bot.polling(none_stop=True, timeout=120)
