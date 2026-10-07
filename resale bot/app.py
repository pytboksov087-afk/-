import telebot
from telebot import types
import sqlite3
import os
import time
import threading
import json
import random
from datetime import datetime, timedelta
from flask import Flask


TOKEN = os.environ.get("BOT_TOKEN", "").strip()
DB_FILE = "cars.db"
OWNER_ID = os.environ.get("OWNER_ID", "").strip()
ADMIN_IDS = [x.strip() for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]
SECRET_CODE = "DEL202"


PHOTOS_DIR = "cars"
WHEELIE_DIR = "wheelie"
SWAPPED_DIR = "swapped"
GARAGE_DIR = "garage"


app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)


# ========== БАЗА ТРАНСПОРТА ==========


CARS = [
    # ===== МАШИНЫ — Уровень 1 =====
    {"key": "vaz_2101", "name": "ВАЗ 2101", "level": 1, "base": 90000, "problems": 4},
    {"key": "vaz_2106", "name": "ВАЗ 2106", "level": 1, "base": 100000, "problems": 4},
    {"key": "vaz_2107", "name": "ВАЗ 2107", "level": 1, "base": 120000, "problems": 4},
    {"key": "vaz_2109", "name": "ВАЗ 2109", "level": 1, "base": 130000, "problems": 4},
    {"key": "vaz_2110", "name": "ВАЗ 2110", "level": 1, "base": 140000, "problems": 4},
    {"key": "vaz_2112", "name": "ВАЗ 2112", "level": 1, "base": 150000, "problems": 4},
    {"key": "vaz_2113", "name": "ВАЗ 2113", "level": 1, "base": 160000, "problems": 4},
    {"key": "vaz_2114", "name": "ВАЗ 2114", "level": 1, "base": 170000, "problems": 4},
    {"key": "vaz_1111", "name": "ВАЗ 1111 Ока", "level": 1, "base": 110000, "problems": 4},
    {"key": "lada_granta", "name": "Lada Granta", "level": 1, "base": 300000, "problems": 3},
    {"key": "lada_kalina", "name": "Lada Kalina", "level": 1, "base": 280000, "problems": 3},
    {"key": "lada_priora", "name": "Lada Priora", "level": 1, "base": 280000, "problems": 3},
    {"key": "daewoo_nexia", "name": "Daewoo Nexia", "level": 1, "base": 140000, "problems": 4},


    # ===== МАШИНЫ — Уровень 2 =====
    {"key": "renault_logan", "name": "Renault Logan", "level": 2, "base": 350000, "problems": 3},
    {"key": "chevrolet_cruze", "name": "Chevrolet Cruze", "level": 2, "base": 700000, "problems": 3},
    {"key": "ford_focus", "name": "Ford Focus", "level": 2, "base": 750000, "problems": 3},
    {"key": "vw_polo", "name": "Volkswagen Polo", "level": 2, "base": 800000, "problems": 3},
    {"key": "kia_rio", "name": "Kia Rio", "level": 2, "base": 900000, "problems": 3},
    {"key": "lada_vesta", "name": "Lada Vesta", "level": 2, "base": 1050000, "problems": 3},
    {"key": "hyundai_solaris", "name": "Hyundai Solaris", "level": 2, "base": 1200000, "problems": 3},
    {"key": "skoda_rapid", "name": "Skoda Rapid", "level": 2, "base": 1400000, "problems": 3},
    {"key": "skoda_octavia", "name": "Skoda Octavia", "level": 2, "base": 1200000, "problems": 3},
    {"key": "bmw_e30", "name": "BMW E30", "level": 2, "base": 500000, "problems": 3},
    {"key": "toyota_mark_ii", "name": "Toyota Mark II", "level": 2, "base": 1100000, "problems": 3},
    {"key": "nissan_laurel_c35", "name": "Nissan Laurel C35", "level": 2, "base": 450000, "problems": 3},


    # ===== МАШИНЫ — Уровень 3 =====
    {"key": "toyota_camry", "name": "Toyota Camry", "level": 3, "base": 2500000, "problems": 2},
    {"key": "toyota_rav4", "name": "Toyota RAV4", "level": 3, "base": 3000000, "problems": 2},
    {"key": "kia_sportage", "name": "Kia Sportage", "level": 3, "base": 2300000, "problems": 2},
    {"key": "hyundai_creta", "name": "Hyundai Creta", "level": 3, "base": 2000000, "problems": 2},
    {"key": "kia_optima", "name": "Kia Optima", "level": 3, "base": 1800000, "problems": 2},
    {"key": "kia_ceed", "name": "Kia Ceed", "level": 3, "base": 1700000, "problems": 2},
    {"key": "hyundai_tucson", "name": "Hyundai Tucson", "level": 3, "base": 2500000, "problems": 2},
    {"key": "toyota_corolla", "name": "Toyota Corolla", "level": 3, "base": 2200000, "problems": 2},
    {"key": "mazda_6", "name": "Mazda 6", "level": 3, "base": 2000000, "problems": 2},
    {"key": "bmw_3_series", "name": "BMW 3 Series", "level": 3, "base": 2800000, "problems": 2},
    {"key": "mercedes_e_class", "name": "Mercedes E-Class", "level": 3, "base": 3500000, "problems": 2},
    {"key": "bmw_x5", "name": "BMW X5", "level": 3, "base": 8000000, "problems": 2},
    {"key": "audi_a6", "name": "Audi A6", "level": 3, "base": 2500000, "problems": 2},
    {"key": "lexus_rx", "name": "Lexus RX", "level": 3, "base": 4500000, "problems": 2},
    {"key": "porsche_macan", "name": "Porsche Macan", "level": 3, "base": 5000000, "problems": 2},


    # ===== МОТОЦИКЛЫ — Уровень 1 =====
    {"key": "vento_riva_2_rx", "name": "Vento Riva 2 RX", "level": 1, "base": 60000, "problems": 4, "type": "moto", "cc": 110, "hp": 6.5, "stroke": "4Т"},
    {"key": "vento_riva_2_sx", "name": "Vento Riva 2 SX", "level": 1, "base": 65000, "problems": 4, "type": "moto", "cc": 110, "hp": 6.5, "stroke": "4Т"},
    {"key": "vento_riva_2_classic", "name": "Vento Riva 2 Classic", "level": 1, "base": 62000, "problems": 4, "type": "moto", "cc": 110, "hp": 6.5, "stroke": "4Т"},
    {"key": "kayo_tt125", "name": "Kayo TT125", "level": 1, "base": 85000, "problems": 4, "type": "moto", "cc": 125, "hp": 11, "stroke": "4Т"},
    {"key": "kayo_tt140", "name": "Kayo TT140", "level": 1, "base": 95000, "problems": 4, "type": "moto", "cc": 140, "hp": 13, "stroke": "4Т"},


    # ===== МОТОЦИКЛЫ — Уровень 2 =====
    {"key": "kayo_k1", "name": "Kayo K1", "level": 2, "base": 140000, "problems": 3, "type": "moto", "cc": 250, "hp": 22, "stroke": "4Т"},
    {"key": "regulmoto_athlete_300", "name": "Regulmoto Athlete 300", "level": 2, "base": 180000, "problems": 3, "type": "moto", "cc": 300, "hp": 26, "stroke": "4Т"},
    {"key": "kews_k16_nb300", "name": "Kews K16 NB300", "level": 2, "base": 220000, "problems": 3, "type": "moto", "cc": 300, "hp": 27, "stroke": "4Т"},
    {"key": "brz_x5_pr250", "name": "BRZ X5 PR250", "level": 2, "base": 160000, "problems": 3, "type": "moto", "cc": 250, "hp": 21, "stroke": "4Т"},
    {"key": "xgz_ktx_pr300", "name": "XGZ KTX PR300", "level": 2, "base": 190000, "problems": 3, "type": "moto", "cc": 300, "hp": 25, "stroke": "4Т"},
    {"key": "bajaj_boxer_150", "name": "Bajaj Boxer 150", "level": 2, "base": 130000, "problems": 3, "type": "moto", "cc": 150, "hp": 12, "stroke": "4Т"},


    # ===== МОТОЦИКЛЫ — Уровень 3 =====
    {"key": "yamaha_yz125", "name": "Yamaha YZ125", "level": 3, "base": 600000, "problems": 2, "type": "moto", "cc": 125, "hp": 35, "stroke": "2Т"},
    {"key": "yamaha_yz250f", "name": "Yamaha YZ250F", "level": 3, "base": 850000, "problems": 2, "type": "moto", "cc": 250, "hp": 40, "stroke": "4Т"},
    {"key": "honda_cb600", "name": "Honda CB600", "level": 3, "base": 700000, "problems": 2, "type": "moto", "cc": 600, "hp": 100, "stroke": "4Т"},
    {"key": "yamaha_r1", "name": "Yamaha R1", "level": 3, "base": 1200000, "problems": 2, "type": "moto", "cc": 1000, "hp": 200, "stroke": "4Т"},
    {"key": "ktm_duke_1390", "name": "KTM Duke 1390", "level": 3, "base": 1900000, "problems": 2, "type": "moto", "cc": 1390, "hp": 190, "stroke": "4Т"},
]


PROBLEMS = {
    "engine": [("Свечи", 8000), ("Троит", 25000), ("Жрёт масло", 55000), ("Капиталка", 150000)],
    "body": [("Царапина", 5000), ("Вмятина", 15000), ("Ржавчина", 35000), ("Битый", 200000)],
    "gearbox": [("Масло", 10000), ("Пинается", 45000), ("Под замену", 180000)],
    "suspension": [("Стойки", 12000), ("Стучит", 30000), ("Вся под замену", 90000)],
    "interior": [("Пятна", 3000), ("Порваны сиденья", 18000), ("Перетяжка", 60000)],
}


SWAP_KEYS = ["vaz_2101", "vaz_2106", "vaz_2107", "vaz_2109", "vaz_2110",
             "vaz_2112", "vaz_2113", "vaz_2114",
             "vento_riva_2_rx", "vento_riva_2_sx", "vento_riva_2_classic"]


ALPHA_KEYS = ["vento_riva_2_rx", "vento_riva_2_sx", "vento_riva_2_classic"]


GARAGE_PRICES = {1: 0, 2: 300000, 3: 800000, 4: 2000000, 5: 5000000}
GARAGE_SLOTS = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}


WORK_COOLDOWN = 300


# ========== ФУНКЦИИ ==========


def fmt(n):
    return "{:,}".format(int(n)).replace(",", " ")


def get_photo(car_key, swapped=False):
    if swapped:
        for ext in ["jpg", "jpeg", "png", "webp"]:
            path = os.path.join(SWAPPED_DIR, car_key + "." + ext)
            if os.path.exists(path):
                return path
    for ext in ["jpg", "jpeg", "png", "webp"]:
        path = os.path.join(PHOTOS_DIR, car_key + "." + ext)
        if os.path.exists(path):
            return path
    return None


def get_wheelie_photo(car_key):
    for ext in ["jpg", "jpeg", "png", "webp"]:
        path = os.path.join(WHEELIE_DIR, car_key + "." + ext)
        if os.path.exists(path):
            return path
    return None


def get_garage_photo(level):
    for ext in ["jpg", "jpeg", "png", "webp"]:
        path = os.path.join(GARAGE_DIR, "garage_" + str(level) + "." + ext)
        if os.path.exists(path):
            return path
    return None


def is_alpha(car_key):
    return car_key in ALPHA_KEYS


def can_swap(car_key):
    return car_key in SWAP_KEYS


def get_car_by_key(car_key):
    for c in CARS:
        if c["key"] == car_key:
            return c
    return None


# ========== БАЗА ДАННЫХ ==========


def db_init():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS players (
        user_id TEXT PRIMARY KEY, name TEXT, username TEXT,
        money INTEGER DEFAULT 100000, level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0, reputation INTEGER DEFAULT 50,
        garage_size INTEGER DEFAULT 1, total_deals INTEGER DEFAULT 0,
        total_earned INTEGER DEFAULT 0, best_deal INTEGER DEFAULT 0,
        last_bonus TEXT, joined TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS garage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT, car_key TEXT, car_name TEXT, car_level INTEGER,
        year INTEGER, mileage INTEGER, buy_price INTEGER,
        invested INTEGER DEFAULT 0, problems TEXT DEFAULT '[]',
        status TEXT DEFAULT 'in_garage',
        sell_price INTEGER DEFAULT 0, listed_at TEXT,
        engine_cc INTEGER DEFAULT 0, last_wheelie TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_key TEXT, car_name TEXT, car_level INTEGER,
        year INTEGER, mileage INTEGER, price INTEGER,
        owner_name TEXT, problems TEXT, created TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS admins (
        user_id TEXT PRIMARY KEY, name TEXT, added TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS banned (
        user_id TEXT PRIMARY KEY, name TEXT, reason TEXT,
        banned_by TEXT, banned_at TEXT)""")
    conn.commit()
    for stmt in [
        "ALTER TABLE garage ADD COLUMN engine_cc INTEGER DEFAULT 0",
        "ALTER TABLE garage ADD COLUMN last_wheelie TEXT",
        "ALTER TABLE players ADD COLUMN username TEXT",
        "ALTER TABLE players ADD COLUMN last_bonus TEXT",
    ]:
        try: c.execute(stmt)
        except Exception: pass
    conn.commit(); conn.close()


# ========== ХЕЛПЕРЫ ==========


def is_owner(user_id):
    return bool(OWNER_ID) and str(user_id) == OWNER_ID


def is_admin(user_id):
    uid = str(user_id)
    if is_owner(uid): return True
    if uid in ADMIN_IDS: return True
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT 1 FROM admins WHERE user_id=?", (uid,))
    row = c.fetchone(); conn.close()
    return row is not None


def is_banned(user_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT reason FROM banned WHERE user_id=?", (str(user_id),))
    row = c.fetchone(); conn.close()
    return row


def check_ban(message):
    ban = is_banned(message.from_user.id)
    if ban:
        bot.send_message(message.chat.id, "🚫 Ты забанен.\nПричина: " + (ban[0] or "без причины"))
        return True
    return False


def get_player(uid):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT user_id, name, username, money, level, exp, reputation,
                 garage_size, total_deals, total_earned, best_deal, last_bonus
                 FROM players WHERE user_id=?""", (str(uid),))
    row = c.fetchone(); conn.close()
    return row


def find_player_by_username(username):
    uname = username.lstrip("@").strip()
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT user_id, name, money FROM players WHERE LOWER(username)=LOWER(?)", (uname,))
    row = c.fetchone()
    if not row:
        c.execute("SELECT user_id, name, money FROM players WHERE LOWER(name)=LOWER(?)", (uname,))
        row = c.fetchone()
    conn.close()
    return row


def main_kb(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔍 Найти тачку", "🏠 Мой гараж")
    markup.add("💰 Баланс", "📊 Рынок")
    markup.add("🏆 Топ", "🎁 Бонус")
    markup.add("👤 Профиль")
    if is_admin(uid):
        markup.add("👥 Игроки", "📢 Сообщение")
    return markup


# ========== СТАРТ ==========


@bot.message_handler(commands=['start', 'menu'])
def start(message):
    if check_ban(message): return
    uid = str(message.from_user.id)
    p = get_player(uid)
    if not p:
        msg = bot.send_message(message.chat.id,
            "🚗 Привет! Это игра «Перекуп Тачек».\n\n"
            "Ты — начинающий автоперекуп.\n"
            "Покупай дёшево, чини, продавай дорого.\n\n"
            "Как тебя зовут? (напиши имя)",
            reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, reg_name)
        return
    bot.send_message(message.chat.id,
        "🚗 С возвращением, " + p[1] + "!\n\nЖми кнопки внизу 👇",
        reply_markup=main_kb(message.from_user.id))


def reg_name(message):
    if check_ban(message): return
    name = (message.text or "").strip()
    if not name or len(name) > 30:
        bot.reply_to(message, "❌ Имя от 1 до 30 символов. Напиши /start заново.")
        return
    uid = str(message.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO players (user_id, name, username, joined)
                 VALUES (?, ?, ?, ?)""",
              (uid, name, message.from_user.username or "",
               datetime.now().strftime("%d.%m.%Y %H:%M")))
    c.execute("UPDATE players SET username=? WHERE user_id=?",
              (message.from_user.username or "", uid))
    conn.commit(); conn.close()
    bot.send_message(message.chat.id,
        "✅ Добро пожаловать, " + name + "!\n\n"
        "💰 Стартовый капитал: 100 000 ₽\n"
        "🏠 Гараж: 1 слот\n"
        "⭐ Репутация: 50/100\n\n"
        "Начни с «🔍 Найти тачку»!",
        reply_markup=main_kb(message.from_user.id))


@bot.message_handler(commands=['help'])
def help_cmd(message):
    if check_ban(message): return
    text = ("🚗 Перекуп Тачек\n\n"
            "Покупай дёшево → чини → продавай дорого.\n\n"
            "Кнопки внизу 👇\n\n"
            "📝 /rename — сменить имя")
    if is_admin(message.from_user.id):
        text += "\n\n🔑 /adminhelp — админ-команды"
    bot.send_message(message.chat.id, text, reply_markup=main_kb(message.from_user.id))


@bot.message_handler(commands=['rename'])
def rename_cmd(message):
    if check_ban(message): return
    msg = bot.send_message(message.chat.id, "🔄 Напиши новое имя:", reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, rename_step)


def rename_step(message):
    if check_ban(message): return
    name = (message.text or "").strip()
    if not name or len(name) > 30:
        bot.reply_to(message, "❌ Имя от 1 до 30 символов."); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET name=? WHERE user_id=?", (name, str(message.from_user.id)))
    conn.commit(); conn.close()
    bot.send_message(message.chat.id, "✅ Теперь ты " + name, reply_markup=main_kb(message.from_user.id))
# ========== ПОИСК ТАЧКИ ==========


@bot.message_handler(func=lambda m: m.text == "🔍 Найти тачку")
def find_car(message):
    if check_ban(message): return
    p = get_player(message.from_user.id)
    if not p:
        bot.send_message(message.chat.id, "Сначала /start"); return


    level = p[4]
    available = [c for c in CARS if c["level"] <= level]
    if not available:
        available = [c for c in CARS if c["level"] == 1]
    listings = random.sample(available, min(5, len(available)))


    for car in listings:
        year = random.randint(2005, 2023)
        mileage = random.randint(50000, 300000)
        base = car["base"]
        price = int(base * random.uniform(0.7, 1.3))
        problems = generate_problems(car)
        owner = random.choice(["Артём", "Сергей", "Дмитрий", "Андрей",
                                "Максим", "Иван", "Николай", "Владимир", "Олег", "Роман"])
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("""INSERT INTO listings (car_key, car_name, car_level, year, mileage,
                     price, owner_name, problems, created)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (car["key"], car["name"], car["level"], year, mileage,
                   price, owner, json.dumps(problems),
                   datetime.now().strftime("%d.%m.%Y %H:%M")))
        lid = c.lastrowid
        conn.commit(); conn.close()


        # формируем подпись
        caption = "🚗 " + car["name"] + ", " + str(year) + "\n"
        caption += "💰 " + fmt(price) + " ₽\n"
        caption += "📊 Пробег: " + fmt(mileage) + " км\n"
        if car.get("type") == "moto":
            caption += "🏍 " + str(car.get("cc", "?")) + " куб, " + str(car.get("hp", "?")) + " л.с., " + car.get("stroke", "") + "\n"
        caption += "👤 Хозяин: " + owner + "\n"
        caption += "📝 «Не бит, не крашен, дед ездил»"


        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("👀 Осмотр 500₽", callback_data="ins_" + str(lid)),
            types.InlineKeyboardButton("👀👀 Диагностика 2000₽", callback_data="diag_" + str(lid)),
        )
        markup.add(
            types.InlineKeyboardButton("💸 Купить", callback_data="buy_" + str(lid)),
            types.InlineKeyboardButton("🤝 Торг", callback_data="haggle_" + str(lid)),
        )
        markup.add(types.InlineKeyboardButton("❌ Пропустить", callback_data="skip_" + str(lid)))


        # отправляем с фото
        photo = get_photo(car["key"])
        if photo:
            try:
                with open(photo, "rb") as f:
                    bot.send_photo(message.chat.id, f, caption=caption, reply_markup=markup)
                continue
            except Exception as e:
                print("Photo error:", e)
        bot.send_message(message.chat.id, caption + "\n📷 фото не найдено", reply_markup=markup)




def generate_problems(car):
    result = []
    max_problems = car["problems"]
    num = random.randint(1, max_problems)
    types_list = list(PROBLEMS.keys())
    random.shuffle(types_list)
    for t in types_list[:num]:
        variants = PROBLEMS[t]
        max_idx = min(len(variants) - 1, car["level"] - 1)
        idx = random.randint(0, max(max_idx, 0))
        name, cost = variants[idx]
        cost = int(cost * (car["level"] ** 1.5))
        result.append({"type": t, "name": name, "cost": cost, "fixed": False})
    return result




# ========== ОСМОТР ==========


@bot.callback_query_handler(func=lambda c: c.data.startswith("ins_"))
def inspect_car(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    lid = int(call.data.split("_")[1])
    p = get_player(call.from_user.id)
    if p[3] < 500:
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money = money - 500 WHERE user_id=?", (str(call.from_user.id),))
    c.execute("SELECT problems FROM listings WHERE id=?", (lid,))
    row = c.fetchone()
    conn.commit(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Устарело.", show_alert=True); return
    problems = json.loads(row[0])
    if not problems:
        bot.answer_callback_query(call.id, "👀 Осмотр ничего не нашёл.", show_alert=True); return
    found = random.choice(problems)
    bot.answer_callback_query(call.id, "👀 Найдено: " + found["name"], show_alert=True)




@bot.callback_query_handler(func=lambda c: c.data.startswith("diag_"))
def diag_car(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    lid = int(call.data.split("_")[1])
    p = get_player(call.from_user.id)
    if p[3] < 2000:
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money = money - 2000 WHERE user_id=?", (str(call.from_user.id),))
    c.execute("SELECT problems FROM listings WHERE id=?", (lid,))
    row = c.fetchone()
    conn.commit(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Устарело.", show_alert=True); return
    problems = json.loads(row[0])
    if not problems:
        bot.send_message(call.from_user.id, "👀👀 Проблем нет! 🎉")
        bot.answer_callback_query(call.id); return
    text = "👀👀 Диагностика завершена:\n\n"
    total_cost = 0
    for i, pr in enumerate(problems, 1):
        text += str(i) + ". " + pr["name"] + " — ремонт ~" + fmt(pr["cost"]) + " ₽\n"
        total_cost += pr["cost"]
    text += "\n💸 Общий ремонт: ~" + fmt(total_cost) + " ₽"
    bot.send_message(call.from_user.id, text)
    bot.answer_callback_query(call.id)




# ========== ПОКУПКА ==========


@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy_car(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    lid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    p = get_player(uid)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT car_key, car_name, car_level, year, mileage, price, problems FROM listings WHERE id=?", (lid,))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Устарело.", show_alert=True); return
    car_key, car_name, car_level, year, mileage, price, problems_json = row
    if p[3] < price:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    c.execute("SELECT COUNT(*) FROM garage WHERE user_id=? AND status='in_garage'", (uid,))
    count = c.fetchone()[0]
    if count >= p[7]:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Гараж полон!", show_alert=True); return


    car = get_car_by_key(car_key)
    engine_cc = car.get("cc", 0) if car else 0


    c.execute("UPDATE players SET money = money - ?, total_deals = total_deals + 1 WHERE user_id=?",
              (price, uid))
    c.execute("""INSERT INTO garage (user_id, car_key, car_name, car_level, year, mileage,
                 buy_price, problems, engine_cc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (uid, car_key, car_name, car_level, year, mileage, price, problems_json, engine_cc))
    c.execute("DELETE FROM listings WHERE id=?", (lid,))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ Куплено!", show_alert=True)
    bot.send_message(call.from_user.id,
        "🚗 " + car_name + " теперь в гараже!\n\nЗаходи в «🏠 Мой гараж».",
        reply_markup=main_kb(call.from_user.id))




@bot.callback_query_handler(func=lambda c: c.data.startswith("skip_"))
def skip_car(call):
    lid = int(call.data.split("_")[1])
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("DELETE FROM listings WHERE id=?", (lid,))
    conn.commit(); conn.close()
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.answer_callback_query(call.id, "Пропущено")




# ========== ТОРГ ==========


@bot.callback_query_handler(func=lambda c: c.data.startswith("haggle_"))
def haggle_car(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    lid = int(call.data.split("_")[1])
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT price FROM listings WHERE id=?", (lid,))
    row = c.fetchone(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Устарело.", show_alert=True); return
    price = row[0]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("-5% (" + fmt(price*0.95) + ")", callback_data="hg_" + str(lid) + "_5"),
        types.InlineKeyboardButton("-10% (" + fmt(price*0.9) + ")", callback_data="hg_" + str(lid) + "_10"),
    )
    markup.add(
        types.InlineKeyboardButton("-20% (" + fmt(price*0.8) + ")", callback_data="hg_" + str(lid) + "_20"),
        types.InlineKeyboardButton("-30% (" + fmt(price*0.7) + ")", callback_data="hg_" + str(lid) + "_30"),
    )
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="hg_" + str(lid) + "_0"))
    bot.send_message(call.from_user.id,
        "🤝 Цена: " + fmt(price) + " ₽\n\nСколько предложишь?",
        reply_markup=markup)
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data.startswith("hg_"))
def haggle_result(call):
    parts = call.data.split("_")
    lid = int(parts[1]); percent = int(parts[2])
    if percent == 0:
        bot.answer_callback_query(call.id, "Отменено"); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT price FROM listings WHERE id=?", (lid,))
    row = c.fetchone(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Устарело.", show_alert=True); return
    price = row[0]
    chance = {5: 90, 10: 60, 20: 30, 30: 10}.get(percent, 0)
    if random.randint(1, 100) <= chance:
        new_price = int(price * (100 - percent) / 100)
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("UPDATE listings SET price=? WHERE id=?", (new_price, lid))
        conn.commit(); conn.close()
        bot.send_message(call.from_user.id,
            "✅ Хозяин согласился!\nНовая цена: " + fmt(new_price) + " ₽",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("💸 Купить за " + fmt(new_price),
                    callback_data="buy_" + str(lid))))
        bot.answer_callback_query(call.id, "Ура!")
    else:
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("DELETE FROM listings WHERE id=?", (lid,))
        conn.commit(); conn.close()
        bot.send_message(call.from_user.id, "😤 Хозяин: «Не, братан, за столько сам ездить буду»")
        bot.answer_callback_query(call.id, "Отказ")




# ========== ГАРАЖ ==========


@bot.message_handler(func=lambda m: m.text == "🏠 Мой гараж")
def my_garage(message):
    if check_ban(message): return
    uid = str(message.from_user.id)
    p = get_player(uid)
    if not p:
        bot.send_message(message.chat.id, "Сначала /start"); return


    # фото гаража по уровню
    photo = get_garage_photo(p[7])
    header = ("🏠 Мой гараж (" + str(p[7]) + " слотов)\n\n")


    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT id, car_key, car_name, car_level, year, mileage,
                 buy_price, invested, problems, status, engine_cc
                 FROM garage WHERE user_id=? ORDER BY id DESC""", (uid,))
    rows = c.fetchall()
    conn.close()


    if not rows:
        text = header + "Гараж пуст. Найди первую тачку!"
        if photo:
            try:
                with open(photo, "rb") as f:
                    bot.send_photo(message.chat.id, f, caption=text, reply_markup=main_kb(message.from_user.id))
                return
            except Exception: pass
        bot.send_message(message.chat.id, text, reply_markup=main_kb(message.from_user.id))
        return


    # считаем капитал гаража
    total_value = 0
    lines = []
    for r in rows:
        gid, car_key, car_name, car_level, year, mileage, buy_price, invested, problems_json, status, engine_cc = r
        problems = json.loads(problems_json)
        unfixed = [pr for pr in problems if not pr.get("fixed")]
        # оценочная цена
        car = get_car_by_key(car_key)
        base = car["base"] if car else buy_price
        cond = max(0.3, 1 - len(unfixed) * 0.1)
        est = int(base * cond)
        total_value += est


        status_mark = ""
        if status == "selling":
            status_mark = " ⏳ продаётся"
        elif status == "done":
            status_mark = " ✅ продано"


        line = "#" + str(gid) + " " + car_name + " (" + str(year) + ")" + status_mark + "\n"
        line += "   💰 Куплено за " + fmt(buy_price) + " ₽\n"
        line += "   📊 Оценка: " + fmt(est) + " ₽\n"
        if engine_cc and engine_cc > 0:
            line += "   🔧 Мотор: " + str(engine_cc) + " куб\n"
        line += "   🔩 Проблем: " + str(len(unfixed)) + "\n"
        lines.append(line)


    text = header
    text += "💰 Капитал гаража: " + fmt(total_value) + " ₽\n\n"
    text += "".join(lines[:5])
    if len(lines) > 5:
        text += "\n... и ещё " + str(len(lines) - 5)


    if photo:
        try:
            with open(photo, "rb") as f:
                bot.send_photo(message.chat.id, f, caption=text)
        except Exception:
            bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, text)


    # отдельно — кнопки на каждую тачку
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in rows[:10]:
        gid, car_key, car_name, car_level, year, mileage, buy_price, invested, problems_json, status, engine_cc = r
        markup.add(types.InlineKeyboardButton("🚗 " + car_name + " (#" + str(gid) + ")",
                   callback_data="car_" + str(gid)))
    bot.send_message(message.chat.id, "Выбери тачку:", reply_markup=markup)




@bot.callback_query_handler(func=lambda c: c.data.startswith("car_"))
def show_car(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT car_key, car_name, car_level, year, mileage, buy_price,
                 invested, problems, status, engine_cc FROM garage
                 WHERE id=? AND user_id=?""", (gid, uid))
    row = c.fetchone(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return


    car_key, car_name, car_level, year, mileage, buy_price, invested, problems_json, status, engine_cc = row
    problems = json.loads(problems_json)
    unfixed = [pr for pr in problems if not pr.get("fixed")]
    car = get_car_by_key(car_key)


    # фото (свапнутая — если Альфа с мотором 125+)
    swapped = is_alpha(car_key) and (engine_cc or 0) >= 125
    photo = get_photo(car_key, swapped=swapped)


    text = "🚗 " + car_name + " (" + str(year) + ")\n"
    text += "📊 Пробег: " + fmt(mileage) + " км\n"
    text += "💰 Куплено за: " + fmt(buy_price) + " ₽\n"
    text += "💸 Вложено: " + fmt(invested) + " ₽\n"
    if car and car.get("type") == "moto":
        text += "🏍 " + str(car.get("cc", "?")) + " куб, " + str(car.get("hp", "?")) + " л.с.\n"
    if engine_cc and engine_cc > 0:
        text += "🔧 Мотор: " + str(engine_cc) + " куб\n"
    text += "\n🔩 Проблемы (" + str(len(unfixed)) + "):\n"
    if unfixed:
        for pr in unfixed:
            text += "• " + pr["name"] + " (~" + fmt(pr["cost"]) + " ₽)\n"
    else:
        text += "• Нет! 🎉\n"


    # кнопки
    markup = types.InlineKeyboardMarkup(row_width=2)
    if unfixed:
        markup.add(types.InlineKeyboardButton("🔧 Ремонт", callback_data="repair_" + str(gid)))
    if can_swap(car_key) and status == "in_garage":
        markup.add(types.InlineKeyboardButton("🔧 Свап 16V / мотор", callback_data="swapmenu_" + str(gid)))
    if car and car.get("type") == "moto" and status == "in_garage":
        markup.add(types.InlineKeyboardButton("🔥 Раздать на заднем", callback_data="wheelie_" + str(gid)))
    if status == "in_garage":
        markup.add(types.InlineKeyboardButton("💸 Продать", callback_data="sell_" + str(gid)))
    elif status == "selling":
        markup.add(types.InlineKeyboardButton("⏳ Продаётся...", callback_data="nothing"))
    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="close_car"))


    if photo:
        try:
            with open(photo, "rb") as f:
                bot.send_photo(call.from_user.id, f, caption=text, reply_markup=markup)
            bot.answer_callback_query(call.id)
            return
        except Exception: pass
    bot.send_message(call.from_user.id, text, reply_markup=markup)
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data == "close_car")
def close_car(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data == "nothing")
def nothing_cb(call):
    bot.answer_callback_query(call.id)




# ========== РЕМОНТ ==========


@bot.callback_query_handler(func=lambda c: c.data.startswith("repair_"))
def repair_menu(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT problems FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    problems = json.loads(row[0])
    unfixed = [(i, pr) for i, pr in enumerate(problems) if not pr.get("fixed")]
    if not unfixed:
        bot.answer_callback_query(call.id, "✅ Проблем нет!", show_alert=True); return


    markup = types.InlineKeyboardMarkup(row_width=1)
    for idx, pr in unfixed:
        markup.add(types.InlineKeyboardButton(
            pr["name"] + " — " + fmt(pr["cost"]) + " ₽",
            callback_data="fix_" + str(gid) + "_" + str(idx)))
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="car_" + str(gid)))
    bot.send_message(call.from_user.id, "🔧 Что ремонтируем?", reply_markup=markup)
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data.startswith("fix_"))
def do_fix(call):
    parts = call.data.split("_")
    gid = int(parts[1]); idx = int(parts[2])
    uid = str(call.from_user.id)
    p = get_player(uid)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT problems, invested FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    problems = json.loads(row[0])
    invested = row[1]
    if idx >= len(problems) or problems[idx].get("fixed"):
        conn.close()
        bot.answer_callback_query(call.id, "Уже отремонтировано.", show_alert=True); return
    cost = problems[idx]["cost"]
    if p[3] < cost:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    problems[idx]["fixed"] = True
    c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (cost, uid))
    c.execute("UPDATE garage SET problems=?, invested=invested+? WHERE id=?",
              (json.dumps(problems), cost, gid))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ Отремонтировано!")
    bot.send_message(call.from_user.id,
        "🔧 " + problems[idx]["name"] + " отремонтировано за " + fmt(cost) + " ₽")




# ========== СВАП ==========


@bot.callback_query_handler(func=lambda c: c.data.startswith("swapmenu_"))
def swap_menu(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT car_key, engine_cc FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    car_key, engine_cc = row
    is_alpha_car = is_alpha(car_key)


    text = "🔧 Тюнинг мотора\n\nСейчас: " + str(engine_cc or "сток") + " куб\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    if is_alpha_car:
        markup.add(
            types.InlineKeyboardButton("🔧 Ремонт стока (5 000₽)", callback_data="swap_" + str(gid) + "_rep"),
            types.InlineKeyboardButton("🔄 125 куб (15 000₽)", callback_data="swap_" + str(gid) + "_125"),
            types.InlineKeyboardButton("🔥 140 куб (25 000₽)", callback_data="swap_" + str(gid) + "_140"),
            types.InlineKeyboardButton("💥 160+ куб (40 000₽)", callback_data="swap_" + str(gid) + "_160"),
        )
    else:
        markup.add(
            types.InlineKeyboardButton("🔧 Свап 16V (200 000₽)", callback_data="swap_" + str(gid) + "_16v"),
        )
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="car_" + str(gid)))
    bot.send_message(call.from_user.id, text, reply_markup=markup)
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data.startswith("swap_"))
def do_swap(call):
    parts = call.data.split("_")
    gid = int(parts[1]); action = parts[2]
    uid = str(call.from_user.id)
    p = get_player(uid)
    prices = {"rep": 5000, "125": 15000, "140": 25000, "160": 40000, "16v": 200000}
    ccs = {"rep": 110, "125": 125, "140": 140, "160": 160, "16v": 1600}
    price = prices.get(action, 0)
    new_cc = ccs.get(action, 0)
    if p[3] < price:
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (price, uid))
    c.execute("UPDATE garage SET engine_cc=?, invested=invested+? WHERE id=?",
              (new_cc, price, gid))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ Готово!")
    if action == "rep":
        bot.send_message(call.from_user.id, "🔧 Мотор отремонтирован!")
    else:
        bot.send_message(call.from_user.id, "🔄 Поставлен мотор " + str(new_cc) + " куб!")




# ========== ВИЛИ ==========


@bot.callback_query_handler(func=lambda c: c.data.startswith("wheelie_"))
def wheelie(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT car_key, car_name, last_wheelie FROM garage WHERE id=? AND user_id=?",
              (gid, uid))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    car_key, car_name, last_wheelie = row


    if last_wheelie:
        try:
            last = datetime.strptime(last_wheelie, "%Y-%m-%d %H:%M:%S")
            elapsed = (datetime.now() - last).total_seconds()
            if elapsed < 3600:
                left = int(3600 - elapsed)
                bot.answer_callback_query(call.id, "⏳ Отдыхай ещё " + str(left // 60) + " мин.", show_alert=True)
                conn.close(); return
        except Exception:
            pass


    roll = random.randint(1, 100)
    c.execute("UPDATE garage SET last_wheelie=? WHERE id=?",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), gid))


    if roll <= 40:
        c.execute("UPDATE players SET reputation = MIN(100, reputation + 3), exp = exp + 10 WHERE user_id=?", (uid,))
        caption = "🔥 " + car_name + " КРАСИВО раздал!\n\n+3 репутации, +10 опыта"
    elif roll <= 70:
        c.execute("UPDATE players SET exp = exp + 5 WHERE user_id=?", (uid,))
        caption = "😎 " + car_name + " почти убрался, но удержал!\n\n+5 опыта"
    elif roll <= 90:
        c.execute("UPDATE players SET reputation = MAX(0, reputation - 5) WHERE user_id=?", (uid,))
        c.execute("UPDATE garage SET invested=invested+15000 WHERE id=?", (gid,))
        caption = "💥 " + car_name + " убрался!\n\n-5 репутации\nРемонт: 15 000 ₽"
    else:
        c.execute("UPDATE players SET money = money - 15000, reputation = MAX(0, reputation - 5) WHERE user_id=?", (uid,))
        caption = "🚔 " + car_name + " поймали за вили!\n\nШтраф: 15 000 ₽\n-5 репутации"


    conn.commit(); conn.close()


    photo = get_wheelie_photo(car_key)
    if photo:
        try:
            with open(photo, "rb") as f:
                bot.send_photo(call.from_user.id, f, caption=caption)
            bot.answer_callback_query(call.id, "🔥")
            return
        except Exception: pass
    bot.send_message(call.from_user.id, caption)
    bot.answer_callback_query(call.id, "🔥")




# ========== ПРОДАЖА (ожидание 20 сек – 5 мин) ==========


@bot.callback_query_handler(func=lambda c: c.data.startswith("sell_"))
def sell_start(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT car_name, status FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    car_name, status = row
    if status != "in_garage":
        bot.answer_callback_query(call.id, "❌ Нельзя продать.", show_alert=True); return


    msg = bot.send_message(call.from_user.id,
        "💸 За сколько продаём " + car_name + "?\n\nНапиши цену в ₽:",
        reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, sell_set_price, gid, uid)
    bot.answer_callback_query(call.id)




def sell_set_price(message, gid, uid):
    if check_ban(message): return
    try:
        price = int((message.text or "").strip().replace(" ", ""))
    except ValueError:
        bot.reply_to(message, "❌ Нужно число."); return
    if price < 1000:
        bot.reply_to(message, "❌ Минимум 1000 ₽."); return


    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE garage SET status='selling', sell_price=?, listed_at=? WHERE id=? AND user_id=?",
              (price, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), gid, uid))
    conn.commit(); conn.close()


    wait_seconds = random.randint(20, 300)
    wait_min = wait_seconds // 60
    wait_sec = wait_seconds % 60
    if wait_min > 0:
        wait_text = str(wait_min) + " мин " + str(wait_sec) + " сек"
    else:
        wait_text = str(wait_sec) + " сек"


    bot.send_message(int(uid),
        "⏳ Ждём покупателя...\n\nПримерное время: " + wait_text + "\n"
        "Не закрывай бота — сообщу.",
        reply_markup=main_kb(int(uid)))


    threading.Thread(target=sell_timer, args=(int(uid), gid, price, wait_seconds), daemon=True).start()




def sell_timer(chat_id, gid, asking_price, wait_seconds):
    time.sleep(wait_seconds)
    uid = str(chat_id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT car_key, car_name, car_level, buy_price, invested,
                 problems, engine_cc FROM garage WHERE id=?""", (gid,))
    row = c.fetchone()
    if not row:
        conn.close(); return
    car_key, car_name, car_level, buy_price, invested, problems_json, engine_cc = row
    problems = json.loads(problems_json)
    unfixed = [p for p in problems if not p.get("fixed")]
    car = get_car_by_key(car_key)
    base = car["base"] if car else buy_price
    cond = max(0.3, 1 - len(unfixed) * 0.1)
    swap_factor = 1.0
    if is_alpha(car_key) and (engine_cc or 0) >= 125:
        swap_factor = 1.3
    elif car_key.startswith("vaz_") and (engine_cc or 0) >= 1600:
        swap_factor = 1.4
    real_price = int(base * cond * swap_factor)
    p = get_player(uid)
    rep = p[6] if p else 50
    rep_factor = 0.9 + (rep / 100) * 0.2
    max_ok = int(real_price * rep_factor * 1.15)


    roll = random.randint(1, 100)
    if roll <= 70:
        if asking_price <= max_ok:
            event, final_price = "sold", asking_price
        else:
            fp = int(asking_price * 0.9)
            if fp <= max_ok:
                event, final_price = "haggled", fp
            else:
                event, final_price = "no_buyer", 0
    elif roll <= 90:
        fp = int(asking_price * random.uniform(0.8, 0.9))
        if fp <= max_ok:
            event, final_price = "haggled", fp
        else:
            event, final_price = "no_buyer", 0
    else:
        event, final_price = "no_buyer", 0


    if event == "sold":
        c.execute("UPDATE players SET money = money + ?, total_deals = total_deals + 1, "
                  "total_earned = total_earned + ?, exp = exp + 20, "
                  "best_deal = MAX(best_deal, ?) WHERE user_id=?",
                  (final_price, final_price, final_price, uid))
        c.execute("DELETE FROM garage WHERE id=?", (gid,))
        conn.commit(); conn.close()
        caption = ("✅ " + car_name + " ПРОДАНА!\n\n"
                   "💰 Цена: " + fmt(final_price) + " ₽\n+20 опыта")
        photo = get_photo(car_key)
        if photo:
            try:
                with open(photo, "rb") as f:
                    bot.send_photo(chat_id, f, caption=caption)
                return
            except Exception: pass
        bot.send_message(chat_id, caption)


    elif event == "haggled":
        c.execute("UPDATE garage SET status='in_garage', sell_price=0 WHERE id=?", (gid,))
        conn.commit(); conn.close()
        bot.send_message(chat_id,
            "🤝 Покупатель торгуется!\n\n"
            "Предлагает: " + fmt(final_price) + " ₽ (вместо " + fmt(asking_price) + ")\n\nСогласиться?",
            reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                types.InlineKeyboardButton("✅ Согласиться", callback_data="sellok_" + str(gid) + "_" + str(final_price)),
                types.InlineKeyboardButton("❌ Отказать", callback_data="sellno_" + str(gid))))


    else:
        c.execute("UPDATE garage SET status='in_garage', sell_price=0 WHERE id=?", (gid,))
        conn.commit(); conn.close()
        bot.send_message(chat_id,
            "😔 Покупатель не пришёл.\n\n" + car_name + " остаётся в гараже.")




@bot.callback_query_handler(func=lambda c: c.data.startswith("sellok_"))
def sell_ok(call):
    parts = call.data.split("_")
    gid = int(parts[1]); price = int(parts[2])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT car_name FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Уже продано.", show_alert=True); return
    car_name = row[0]
    c.execute("UPDATE players SET money = money + ?, total_deals = total_deals + 1, "
              "total_earned = total_earned + ?, exp = exp + 15 WHERE user_id=?",
              (price, price, uid))
    c.execute("DELETE FROM garage WHERE id=?", (gid,))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ Продано!")
    bot.send_message(call.from_user.id,
        "✅ " + car_name + " продана за " + fmt(price) + " ₽\n+15 опыта")




@bot.callback_query_handler(func=lambda c: c.data.startswith("sellno_"))
def sell_no(call):
    bot.answer_callback_query(call.id, "Отказано")
    bot.send_message(call.from_user.id, "❌ Отказал покупателю. Тачка в гараже.",
                     reply_markup=main_kb(call.from_user.id))




# ========== ПРОФИЛЬ ==========


@bot.message_handler(func=lambda m: m.text == "👤 Профиль")
def profile(message):
    if check_ban(message): return
    uid = str(message.from_user.id)
    p = get_player(uid)
    if not p:
        bot.send_message(message.chat.id, "Сначала /start"); return
    photo = get_garage_photo(p[7])
    text = ("👤 " + p[1] + "\n\n"
            "💰 Баланс: " + fmt(p[3]) + " ₽\n"
            "📈 Уровень: " + str(p[4]) + "\n"
            "🎯 Опыт: " + str(p[5]) + "\n"
            "⭐ Репутация: " + str(p[6]) + "/100\n"
            "🏠 Гараж: " + str(p[7]) + " слотов\n\n"
            "🤝 Сделок: " + str(p[8]) + "\n"
            "💵 Заработано: " + fmt(p[9]) + " ₽\n"
            "🏆 Лучшая сделка: " + fmt(p[10]) + " ₽")


    markup = types.InlineKeyboardMarkup(row_width=1)
    if p[7] < 5:
        next_lvl = p[7] + 1
        price = GARAGE_PRICES[next_lvl]
        markup.add(types.InlineKeyboardButton("🏗 Расширить гараж (" + fmt(price) + " ₽)",
                   callback_data="upgrade_garage"))


    if photo:
        try:
            with open(photo, "rb") as f:
                bot.send_photo(message.chat.id, f, caption=text, reply_markup=markup)
            return
        except Exception: pass
    bot.send_message(message.chat.id, text, reply_markup=markup)




@bot.callback_query_handler(func=lambda c: c.data == "upgrade_garage")
def upgrade_garage_menu(call):
    uid = str(call.from_user.id)
    p = get_player(uid)
    if not p:
        bot.answer_callback_query(call.id, "Сначала /start", show_alert=True); return
    current = p[7]
    next_level = current + 1
    if next_level > 5:
        bot.answer_callback_query(call.id, "🏆 Максимальный гараж!", show_alert=True); return
    price = GARAGE_PRICES[next_level]
    slots = GARAGE_SLOTS[next_level]
    text = ("🏗 Расширение гаража\n\n"
            "Сейчас: " + str(current) + " слотов\n"
            "Будет: " + str(slots) + " слотов\n"
            "Цена: " + fmt(price) + " ₽\n\n"
            "💰 У тебя: " + fmt(p[3]) + " ₽")
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("✅ Купить за " + fmt(price) + " ₽",
               callback_data="buy_garage_" + str(next_level)))
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="nothing"))
    bot.send_message(call.from_user.id, text, reply_markup=markup)
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_garage_"))
def buy_garage(call):
    uid = str(call.from_user.id)
    level = int(call.data.split("_")[2])
    p = get_player(uid)
    price = GARAGE_PRICES[level]
    if p[3] < price:
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money = money - ?, garage_size = ? WHERE user_id=?",
              (price, level, uid))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ Гараж расширен!", show_alert=True)
    bot.send_message(call.from_user.id,
        "🏗 Гараж расширен до " + str(level) + " уровня!",
        reply_markup=main_kb(call.from_user.id))




# ========== БАЛАНС ==========


@bot.message_handler(func=lambda m: m.text == "💰 Баланс")
def balance(message):
    if check_ban(message): return
    p = get_player(message.from_user.id)
    if not p:
        bot.send_message(message.chat.id, "Сначала /start"); return
    bot.send_message(message.chat.id,
        "💰 Баланс: " + fmt(p[3]) + " ₽\n"
        "📈 Уровень: " + str(p[4]) + "\n"
        "⭐ Репутация: " + str(p[6]) + "/100",
        reply_markup=main_kb(message.from_user.id))




# ========== РЫНОК ==========


@bot.message_handler(func=lambda m: m.text == "📊 Рынок")
def market(message):
    if check_ban(message): return
    text = "📊 Рынок (цены примерные):\n\n"
    # группируем по уровням
    for lvl in [1, 2, 3]:
        text += "— Уровень " + str(lvl) + " —\n"
        for car in CARS:
            if car["level"] == lvl:
                text += "• " + car["name"] + " — " + fmt(car["base"]) + " ₽\n"
        text += "\n"
    bot.send_message(message.chat.id, text[:4000])




# ========== ТОП ==========


@bot.message_handler(func=lambda m: m.text == "🏆 Топ")
def top_players(message):
    if check_ban(message): return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT name, money, garage_size, total_deals, total_earned
                 FROM players ORDER BY (money + total_earned) DESC LIMIT 10""")
    rows = c.fetchall(); conn.close()
    if not rows:
        bot.send_message(message.chat.id, "Пока никого нет."); return
    text = "🏆 Топ-10 перекупов:\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, r in enumerate(rows):
        prefix = medals[i] if i < 3 else str(i+1) + "."
        text += prefix + " " + r[0] + " — " + fmt(r[1]) + " ₽ (сделок: " + str(r[3]) + ")\n"
    bot.send_message(message.chat.id, text)




# ========== БОНУС ==========


@bot.message_handler(func=lambda m: m.text == "🎁 Бонус")
def bonus(message):
    if check_ban(message): return
    uid = str(message.from_user.id)
    p = get_player(uid)
    if not p:
        bot.send_message(message.chat.id, "Сначала /start"); return


    if p[11]:
        try:
            last = datetime.strptime(p[11], "%Y-%m-%d %H:%M:%S")
            elapsed = (datetime.now() - last).total_seconds()
            if elapsed < 14400:  # 4 часа
                left = int(14400 - elapsed)
                h = left // 3600
                m = (left % 3600) // 60
                bot.send_message(message.chat.id,
                    "⏳ Бонус будет доступен через " + str(h) + " ч " + str(m) + " мин.")
                return
        except Exception:
            pass


    amount = 10000
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money = money + ?, last_bonus=? WHERE user_id=?",
              (amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), uid))
    conn.commit(); conn.close()
    bot.send_message(message.chat.id,
        "🎁 Бонус получен: +" + fmt(amount) + " ₽\n\nПриходи через 4 часа.",
        reply_markup=main_kb(message.from_user.id))
# ========== АДМИН-СИСТЕМА ==========


@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if check_ban(message): return
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "✅ Ты уже админ.", reply_markup=main_kb(message.from_user.id))
        return
    msg = bot.send_message(message.chat.id, "🔑 Введи секретный код:", reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, admin_code_step)




def admin_code_step(message):
    if check_ban(message): return
    code = (message.text or "").strip()
    if code != SECRET_CODE:
        bot.reply_to(message, "❌ Неверный код."); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO admins (user_id, name, added) VALUES (?, ?, ?)",
              (str(message.from_user.id), message.from_user.first_name or "Админ",
               datetime.now().strftime("%d.%m.%Y %H:%M")))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ Ты теперь админ!\n\nНапиши /adminhelp — список команд.",
                 reply_markup=main_kb(message.from_user.id))




@bot.message_handler(commands=['unadmin'])
def unadmin_cmd(message):
    if check_ban(message): return
    if is_owner(message.from_user.id):
        bot.reply_to(message, "👑 Владельца нельзя снять."); return
    if not is_admin(message.from_user.id): return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("DELETE FROM admins WHERE user_id=?", (str(message.from_user.id),))
    conn.commit(); conn.close()
    bot.reply_to(message, "Ты больше не админ.", reply_markup=main_kb(message.from_user.id))




@bot.message_handler(commands=['adminhelp'])
def admin_help(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    text = ("🎛 Админ-команды:\n\n"
            "👤 УПРАВЛЕНИЕ ИГРОКАМИ:\n"
            "/addmoney @ник 100000 — добавить деньги\n"
            "/takemoney @ник 50000 — забрать деньги\n"
            "/setmoney @ник 500000 — установить баланс\n"
            "/addexp @ник 500 — добавить опыт\n"
            "/addrep @ник 10 — добавить репутацию\n"
            "/setrep @ник 100 — установить репутацию\n"
            "/setgarage @ник 5 — установить гараж (1-5)\n"
            "/addcar @ник vaz_2107 — выдать машину\n"
            "/resetplayer @ник — сбросить игрока\n\n"
            "🚫 МОДЕРАЦИЯ:\n"
            "/ban @ник причина — забанить\n"
            "/unban @ник — разбанить\n"
            "/banlist — чёрный список\n"
            "/users — все игроки\n\n"
            "🔑 АДМИН:\n"
            "/admin — стать админом (код)\n"
            "/unadmin — снять с себя\n"
            "/adminhelp — эта справка\n\n"
            "👑 ВЛАДЕЛЕЦ:\n"
            "/admins — управление админами")
    bot.send_message(message.chat.id, text)




@bot.message_handler(commands=['addmoney'])
def admin_addmoney(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /addmoney @юзернейм 100000"); return
    try:
        amount = int(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ Сумма — число."); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Игрок не найден."); return
    tid, tname, tmoney = row
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money = money + ? WHERE user_id=?", (amount, tid))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": +" + fmt(amount) + " ₽\nБыло: " + fmt(tmoney) + " → Стало: " + fmt(tmoney + amount))
    try: bot.send_message(int(tid), "💰 Админ начислил тебе " + fmt(amount) + " ₽")
    except Exception: pass




@bot.message_handler(commands=['takemoney'])
def admin_takemoney(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /takemoney @юзернейм 50000"); return
    try:
        amount = int(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ Сумма — число."); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Игрок не найден."); return
    tid, tname, tmoney = row
    new_money = max(0, tmoney - amount)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money=? WHERE user_id=?", (new_money, tid))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": -" + fmt(amount) + " ₽\nБыло: " + fmt(tmoney) + " → Стало: " + fmt(new_money))
    try: bot.send_message(int(tid), "💸 Админ списал у тебя " + fmt(amount) + " ₽")
    except Exception: pass




@bot.message_handler(commands=['setmoney'])
def admin_setmoney(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /setmoney @юзернейм 500000"); return
    try:
        amount = int(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ Сумма — число."); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Игрок не найден."); return
    tid, tname, _ = row
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money=? WHERE user_id=?", (amount, tid))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": баланс = " + fmt(amount) + " ₽")
    try: bot.send_message(int(tid), "💰 Админ установил тебе баланс: " + fmt(amount) + " ₽")
    except Exception: pass




@bot.message_handler(commands=['addexp'])
def admin_addexp(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /addexp @юзернейм 500"); return
    try:
        amount = int(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ Опыт — число."); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Игрок не найден."); return
    tid, tname, _ = row
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET exp = exp + ? WHERE user_id=?", (amount, tid))
    c.execute("SELECT exp, level FROM players WHERE user_id=?", (tid,))
    new_exp, new_level = c.fetchone()
    calc_level = 1 + new_exp // 1000
    if calc_level > new_level:
        c.execute("UPDATE players SET level=? WHERE user_id=?", (calc_level, tid))
        level_msg = "\n🎉 Новый уровень: " + str(calc_level)
    else:
        level_msg = ""
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": +" + str(amount) + " опыта" + level_msg)




@bot.message_handler(commands=['addrep'])
def admin_addrep(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /addrep @юзернейм 10"); return
    try:
        amount = int(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ Репутация — число."); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Игрок не найден."); return
    tid, tname, _ = row
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET reputation = MIN(100, MAX(0, reputation + ?)) WHERE user_id=?", (amount, tid))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": репутация " + ("+" if amount >= 0 else "") + str(amount))




@bot.message_handler(commands=['setrep'])
def admin_setrep(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /setrep @юзернейм 100"); return
    try:
        amount = int(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ Репутация — число."); return
    amount = max(0, min(100, amount))
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Игрок не найден."); return
    tid, tname, _ = row
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET reputation=? WHERE user_id=?", (amount, tid))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": репутация = " + str(amount))




@bot.message_handler(commands=['setgarage'])
def admin_setgarage(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /setgarage @юзернейм 5"); return
    try:
        level = int(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ Уровень — число 1-5."); return
    level = max(1, min(5, level))
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Игрок не найден."); return
    tid, tname, _ = row
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET garage_size=? WHERE user_id=?", (level, tid))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": гараж = " + str(level) + " слотов")
    try: bot.send_message(int(tid), "🏗 Админ расширил твой гараж до " + str(level) + " слотов")
    except Exception: pass




@bot.message_handler(commands=['addcar'])
def admin_addcar(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /addcar @юзернейм vaz_2107"); return
    car_key = parts[2].strip()
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Игрок не найден."); return
    tid, tname, _ = row
    car = get_car_by_key(car_key)
    if not car:
        bot.reply_to(message, "❌ Машина не найдена. Пример: vaz_2107"); return
    problems = generate_problems(car)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT garage_size FROM players WHERE user_id=?", (tid,))
    max_slots = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM garage WHERE user_id=? AND status='in_garage'", (tid,))
    used = c.fetchone()[0]
    if used >= max_slots:
        conn.close()
        bot.reply_to(message, "❌ У игрока нет места (" + str(used) + "/" + str(max_slots) + ")"); return
    engine_cc = car.get("cc", 0)
    c.execute("""INSERT INTO garage (user_id, car_key, car_name, car_level, year, mileage,
                 buy_price, problems, engine_cc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (tid, car["key"], car["name"], car["level"],
               random.randint(2005, 2023), random.randint(50000, 300000),
               0, json.dumps(problems), engine_cc))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + " получил: " + car["name"])
    try: bot.send_message(int(tid), "🎁 Админ выдал тебе " + car["name"])
    except Exception: pass




@bot.message_handler(commands=['resetplayer'])
def admin_resetplayer(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Формат: /resetplayer @юзернейм"); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Игрок не найден."); return
    tid, tname, _ = row
    if is_owner(tid):
        bot.reply_to(message, "❌ Нельзя сбросить владельца."); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("DELETE FROM garage WHERE user_id=?", (tid,))
    c.execute("""UPDATE players SET money=100000, level=1, exp=0, reputation=50,
                 garage_size=1, total_deals=0, total_earned=0, best_deal=0
                 WHERE user_id=?""", (tid,))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + " сброшен.")
    try: bot.send_message(int(tid), "⚠️ Твой прогресс сброшен админом.")
    except Exception: pass




# ========== СПИСОК ИГРОКОВ ==========


@bot.message_handler(commands=['users'])
def users_cmd(message):
    if check_ban(message): return
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    show_users(message.chat.id)




@bot.message_handler(func=lambda m: m.text == "👥 Игроки")
def users_btn(message):
    if check_ban(message): return
    if not is_admin(message.from_user.id): return
    show_users(message.chat.id)




def show_users(chat_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT user_id, name, username, money, level FROM players
                 ORDER BY (money) DESC LIMIT 30""")
    rows = c.fetchall(); conn.close()
    if not rows:
        bot.send_message(chat_id, "Игроков нет."); return
    text = "👥 Игроки (" + str(len(rows)) + "):\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in rows:
        uid, name, username, money, level = r
        line = name
        if username: line += " (@" + username + ")"
        line += " — " + fmt(money) + " ₽, ур. " + str(level)
        text += "• " + line + "\n"
        markup.add(types.InlineKeyboardButton("👤 " + name, callback_data="vp_" + str(uid)))
    bot.send_message(chat_id, text, reply_markup=markup)




@bot.callback_query_handler(func=lambda c: c.data.startswith("vp_"))
def view_profile(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Только админ.", show_alert=True); return
    target_id = call.data.split("_")[1]
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT user_id, name, username, money, level, exp, reputation,
                 garage_size, total_deals, total_earned, best_deal, joined
                 FROM players WHERE user_id=?""", (target_id,))
    p = c.fetchone()
    if not p:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Не найден.", show_alert=True); return
    c.execute("SELECT COUNT(*) FROM garage WHERE user_id=?", (target_id,))
    cars_count = c.fetchone()[0]
    c.execute("SELECT 1 FROM banned WHERE user_id=?", (target_id,))
    banned = c.fetchone()
    conn.close()


    text = ("👤 Профиль игрока\n\n"
            "Имя: " + p[1] + "\n")
    if p[2]: text += "@" + p[2] + "\n"
    text += "ID: `" + p[0] + "`\n\n"
    text += "💰 Баланс: " + fmt(p[3]) + " ₽\n"
    text += "📈 Уровень: " + str(p[4]) + " (" + str(p[5]) + " опыта)\n"
    text += "⭐ Репутация: " + str(p[6]) + "/100\n"
    text += "🏠 Гараж: " + str(p[7]) + " слотов (" + str(cars_count) + " занято)\n\n"
    text += "🤝 Сделок: " + str(p[8]) + "\n"
    text += "💵 Заработано: " + fmt(p[9]) + " ₽\n"
    text += "🏆 Лучшая сделка: " + fmt(p[10]) + " ₽\n"
    text += "📅 Регистрация: " + (p[11] or "?") + "\n"
    if banned:
        text += "\n🚫 ЗАБАНЕН: " + (banned[0] or "без причины")


    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💰 +100k", callback_data="ap_" + target_id + "_m100"),
        types.InlineKeyboardButton("💰 +500k", callback_data="ap_" + target_id + "_m500"),
    )
    markup.add(
        types.InlineKeyboardButton("💸 -100k", callback_data="ap_" + target_id + "_m-100"),
        types.InlineKeyboardButton("💸 -500k", callback_data="ap_" + target_id + "_m-500"),
    )
    markup.add(
        types.InlineKeyboardButton("⭐ +10 реп", callback_data="ap_" + target_id + "_r10"),
        types.InlineKeyboardButton("⭐ -10 реп", callback_data="ap_" + target_id + "_r-10"),
    )
    markup.add(types.InlineKeyboardButton("🏗 +1 слот", callback_data="ap_" + target_id + "_g1"))
    if banned:
        markup.add(types.InlineKeyboardButton("🔓 Разбанить", callback_data="ap_" + target_id + "_unban"))
    else:
        markup.add(types.InlineKeyboardButton("🚫 Забанить", callback_data="ap_" + target_id + "_ban"))
    markup.add(types.InlineKeyboardButton("♻️ Сбросить", callback_data="ap_" + target_id + "_reset"))
    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="close_car"))


    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              reply_markup=markup, parse_mode="Markdown")
    except Exception:
        bot.send_message(call.from_user.id, text, reply_markup=markup, parse_mode="Markdown")
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data.startswith("ap_"))
def admin_action(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Только админ.", show_alert=True); return
    parts = call.data.split("_")
    target_id = parts[1]
    action = "_".join(parts[2:])
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()


    if action.startswith("m"):
        delta = int(action[1:]) * 1000
        c.execute("UPDATE players SET money = MAX(0, money + ?) WHERE user_id=?", (delta, target_id))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "✅ " + ("+" if delta > 0 else "") + fmt(delta) + " ₽", show_alert=True)
    elif action.startswith("r"):
        delta = int(action[1:])
        c.execute("UPDATE players SET reputation = MIN(100, MAX(0, reputation + ?)) WHERE user_id=?", (delta, target_id))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "✅ Репутация " + ("+" if delta > 0 else "") + str(delta), show_alert=True)
    elif action == "g1":
        c.execute("UPDATE players SET garage_size = MIN(5, garage_size + 1) WHERE user_id=?", (target_id,))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "✅ +1 слот", show_alert=True)
    elif action == "ban":
        c.execute("SELECT name FROM players WHERE user_id=?", (target_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            bot.answer_callback_query(call.id, "❌ Не найден", show_alert=True); return
        if is_owner(target_id):
            conn.close()
            bot.answer_callback_query(call.id, "❌ Нельзя забанить владельца", show_alert=True); return
        c.execute("INSERT OR REPLACE INTO banned (user_id, name, reason, banned_by, banned_at) VALUES (?, ?, ?, ?, ?)",
                  (target_id, row[0], "по решению админа",
                   call.from_user.first_name or "Админ",
                   datetime.now().strftime("%d.%m.%Y %H:%M")))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "🚫 Забанен", show_alert=True)
        try: bot.send_message(int(target_id), "🚫 Тебя забанили в игре.")
        except Exception: pass
    elif action == "unban":
        c.execute("DELETE FROM banned WHERE user_id=?", (target_id,))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "🔓 Разбанен", show_alert=True)
        try: bot.send_message(int(target_id), "🔓 Ты разбанен.")
        except Exception: pass
    elif action == "reset":
        c.execute("DELETE FROM garage WHERE user_id=?", (target_id,))
        c.execute("""UPDATE players SET money=100000, level=1, exp=0, reputation=50,
                     garage_size=1, total_deals=0, total_earned=0, best_deal=0
                     WHERE user_id=?""", (target_id,))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "♻️ Сброшен", show_alert=True)
    else:
        conn.close()
        bot.answer_callback_query(call.id, "?")




# ========== БАН / РАЗБАН / ЧЁРНЫЙ СПИСОК ==========


@bot.message_handler(commands=['ban'])
def ban_cmd(message):
    if check_ban(message): return
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        bot.reply_to(message, "Формат: /ban @ник причина"); return
    reason = parts[2] if len(parts) > 2 else "без причины"
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Не найден."); return
    tid, tname, _ = row
    if is_owner(tid):
        bot.reply_to(message, "❌ Нельзя забанить владельца."); return
    if not is_owner(message.from_user.id) and is_admin(tid):
        bot.reply_to(message, "❌ Только владелец может банить админов."); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO banned (user_id, name, reason, banned_by, banned_at) VALUES (?, ?, ?, ?, ?)",
              (tid, tname, reason, message.from_user.first_name or "Админ",
               datetime.now().strftime("%d.%m.%Y %H:%M")))
    conn.commit(); conn.close()
    bot.reply_to(message, "🚫 " + tname + " забанен. Причина: " + reason)
    try: bot.send_message(int(tid), "🚫 Тебя забанили.\nПричина: " + reason)
    except Exception: pass




@bot.message_handler(commands=['unban'])
def unban_cmd(message):
    if check_ban(message): return
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Формат: /unban @ник"); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Не найден."); return
    tid, tname, _ = row
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("DELETE FROM banned WHERE user_id=?", (tid,))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + " разбанен.")
    try: bot.send_message(int(tid), "🔓 Ты разбанен.")
    except Exception: pass




@bot.message_handler(commands=['banlist'])
def banlist_cmd(message):
    if check_ban(message): return
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT user_id, name, reason, banned_by, banned_at FROM banned ORDER BY banned_at DESC")
    rows = c.fetchall(); conn.close()
    if not rows:
        bot.send_message(message.chat.id, "🚫 Чёрный список пуст."); return
    text = "🚫 Чёрный список (" + str(len(rows)) + "):\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in rows:
        text += "• " + (r[1] or "?") + " — " + (r[2] or "без причины") + "\n"
        text += "  Забанил: " + (r[3] or "?") + " (" + (r[4] or "?") + ")\n"
        markup.add(types.InlineKeyboardButton("🔓 Разбанить: " + (r[1] or "?"),
                   callback_data="unban2_" + r[0]))
    bot.send_message(message.chat.id, text, reply_markup=markup)




@bot.callback_query_handler(func=lambda c: c.data.startswith("unban2_"))
def unban2(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Только админ.", show_alert=True); return
    tid = call.data.split("_")[1]
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT name FROM banned WHERE user_id=?", (tid,))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "Уже не в бане.", show_alert=True); return
    c.execute("DELETE FROM banned WHERE user_id=?", (tid,))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ " + row[0] + " разбанен.", show_alert=True)
    try: bot.send_message(int(tid), "🔓 Ты разбанен.")
    except Exception: pass




# ========== АДМИНЫ (только владелец) ==========


@bot.message_handler(commands=['admins'])
def admins_list(message):
    if check_ban(message): return
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ Только владелец."); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT user_id, name, added FROM admins ORDER BY added")
    rows = c.fetchall(); conn.close()
    text = "👑 Владелец: " + (OWNER_ID or "не задан") + "\n\n"
    if not rows:
        text += "🔑 Админов нет."
        bot.send_message(message.chat.id, text); return
    text += "🔑 Админы (" + str(len(rows)) + "):\n"
    for r in rows:
        text += "• " + r[1] + "\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in rows:
        markup.add(types.InlineKeyboardButton("🗑 Удалить: " + r[1],
                   callback_data="adm_del_" + r[0]))
    bot.send_message(message.chat.id, text, reply_markup=markup)




@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_del_"))
def adm_del(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Только владелец.", show_alert=True); return
    target = call.data.split("_")[2]
    if target == OWNER_ID:
        bot.answer_callback_query(call.id, "Владельца нельзя удалить.", show_alert=True); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT name FROM admins WHERE user_id=?", (target,))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "Уже не админ.", show_alert=True); return
    name = row[0]
    c.execute("DELETE FROM admins WHERE user_id=?", (target,))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ " + name + " больше не админ.", show_alert=True)
    try: bot.send_message(int(target), "🔓 С тебя снята админка.")
    except Exception: pass




# ========== СООБЩЕНИЕ ОТ АДМИНА ==========


@bot.message_handler(func=lambda m: m.text == "📢 Сообщение")
def ann_menu(message):
    if check_ban(message): return
    if not is_admin(message.from_user.id): return
    msg = bot.send_message(message.chat.id, "Текст сообщения для всех:", reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, ann_send)




def ann_send(message):
    if check_ban(message): return
    if not is_admin(message.from_user.id): return
    text = (message.text or "").strip()
    if not text:
        bot.reply_to(message, "❌ Пусто."); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT user_id FROM players")
    uids = [r[0] for r in c.fetchall()]
    conn.close()
    sent = 0
    for uid in uids:
        if is_banned(uid): continue
        try:
            bot.send_message(int(uid), "📢 Сообщение от админа:\n\n" + text)
            sent += 1
        except Exception: pass
    bot.reply_to(message, "✅ Отправлено: " + str(sent) + " из " + str(len(uids)))




# ========== ФОНОВЫЕ ЗАДАЧИ ==========


def bonus_worker():
    """Напоминает о бонусе раз в 4 часа (опционально)"""
    while True:
        time.sleep(3600)




def events_worker():
    """Случайные события раз в 30 минут (пример, можно отключить)"""
    while True:
        time.sleep(1800)
        # можно добавить: разослать игрокам новость про кризис/хайп




@app.route('/')
def health():
    return "Car flipping game is running"




def run_bot():
    bot.infinity_polling()




if __name__ == '__main__':
    db_init()
    threading.Thread(target=run_bot, daemon=True).start()
    threading.Thread(target=bonus_worker, daemon=True).start()
    threading.Thread(target=events_worker, daemon=True).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)