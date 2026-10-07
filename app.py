import telebot
from telebot import types
import sqlite3
import os
import time
import threading
import json
import random
import string
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
    {"key": "vaz_2101", "name": "ВАЗ 2101", "level": 1, "base": 90000, "problems": 4, "hp": 62, "weight": 955, "drive": "RWD"},
    {"key": "vaz_2106", "name": "ВАЗ 2106", "level": 1, "base": 100000, "problems": 4, "hp": 75, "weight": 1045, "drive": "RWD"},
    {"key": "vaz_2107", "name": "ВАЗ 2107", "level": 1, "base": 120000, "problems": 4, "hp": 75, "weight": 1050, "drive": "RWD"},
    {"key": "vaz_2109", "name": "ВАЗ 2109", "level": 1, "base": 130000, "problems": 4, "hp": 72, "weight": 945, "drive": "FWD"},
    {"key": "vaz_2110", "name": "ВАЗ 2110", "level": 1, "base": 140000, "problems": 4, "hp": 92, "weight": 1020, "drive": "FWD"},
    {"key": "vaz_2112", "name": "ВАЗ 2112", "level": 1, "base": 150000, "problems": 4, "hp": 92, "weight": 1030, "drive": "FWD"},
    {"key": "vaz_2113", "name": "ВАЗ 2113", "level": 1, "base": 160000, "problems": 4, "hp": 81, "weight": 985, "drive": "FWD"},
    {"key": "vaz_2114", "name": "ВАЗ 2114", "level": 1, "base": 170000, "problems": 4, "hp": 81, "weight": 985, "drive": "FWD"},
    {"key": "vaz_1111", "name": "ВАЗ 1111 Ока", "level": 1, "base": 110000, "problems": 4, "hp": 53, "weight": 675, "drive": "FWD"},
    {"key": "lada_granta", "name": "Lada Granta", "level": 1, "base": 300000, "problems": 3, "hp": 106, "weight": 1160, "drive": "FWD"},
    {"key": "lada_kalina", "name": "Lada Kalina", "level": 1, "base": 280000, "problems": 3, "hp": 98, "weight": 1080, "drive": "FWD"},
    {"key": "lada_priora", "name": "Lada Priora", "level": 1, "base": 280000, "problems": 3, "hp": 98, "weight": 1085, "drive": "FWD"},
    {"key": "daewoo_nexia", "name": "Daewoo Nexia", "level": 1, "base": 140000, "problems": 4, "hp": 85, "weight": 960, "drive": "FWD"},


    # ===== МАШИНЫ — Уровень 2 =====
    {"key": "renault_logan", "name": "Renault Logan", "level": 2, "base": 350000, "problems": 3, "hp": 102, "weight": 1127, "drive": "FWD"},
    {"key": "chevrolet_cruze", "name": "Chevrolet Cruze", "level": 2, "base": 700000, "problems": 3, "hp": 141, "weight": 1315, "drive": "FWD"},
    {"key": "ford_focus", "name": "Ford Focus", "level": 2, "base": 750000, "problems": 3, "hp": 125, "weight": 1275, "drive": "FWD"},
    {"key": "vw_polo", "name": "Volkswagen Polo", "level": 2, "base": 800000, "problems": 3, "hp": 110, "weight": 1170, "drive": "FWD"},
    {"key": "kia_rio", "name": "Kia Rio", "level": 2, "base": 900000, "problems": 3, "hp": 123, "weight": 1150, "drive": "FWD"},
    {"key": "lada_vesta", "name": "Lada Vesta", "level": 2, "base": 1050000, "problems": 3, "hp": 106, "weight": 1230, "drive": "FWD"},
    {"key": "hyundai_solaris", "name": "Hyundai Solaris", "level": 2, "base": 1200000, "problems": 3, "hp": 123, "weight": 1170, "drive": "FWD"},
    {"key": "skoda_rapid", "name": "Skoda Rapid", "level": 2, "base": 1400000, "problems": 3, "hp": 125, "weight": 1190, "drive": "FWD"},
    {"key": "skoda_octavia", "name": "Skoda Octavia", "level": 2, "base": 1200000, "problems": 3, "hp": 150, "weight": 1350, "drive": "FWD"},
    {"key": "bmw_e30", "name": "BMW E30", "level": 2, "base": 500000, "problems": 3, "hp": 170, "weight": 1200, "drive": "RWD"},
    {"key": "toyota_mark_ii", "name": "Toyota Mark II", "level": 2, "base": 1100000, "problems": 3, "hp": 220, "weight": 1450, "drive": "RWD"},
    {"key": "nissan_laurel_c35", "name": "Nissan Laurel C35", "level": 2, "base": 450000, "problems": 3, "hp": 200, "weight": 1400, "drive": "RWD"},


    # ===== МАШИНЫ — Уровень 3 =====
    {"key": "toyota_camry", "name": "Toyota Camry", "level": 3, "base": 2500000, "problems": 2, "hp": 249, "weight": 1550, "drive": "FWD"},
    {"key": "toyota_rav4", "name": "Toyota RAV4", "level": 3, "base": 3000000, "problems": 2, "hp": 199, "weight": 1600, "drive": "AWD"},
    {"key": "kia_sportage", "name": "Kia Sportage", "level": 3, "base": 2300000, "problems": 2, "hp": 184, "weight": 1550, "drive": "AWD"},
    {"key": "hyundai_creta", "name": "Hyundai Creta", "level": 3, "base": 2000000, "problems": 2, "hp": 150, "weight": 1390, "drive": "AWD"},
    {"key": "kia_optima", "name": "Kia Optima", "level": 3, "base": 1800000, "problems": 2, "hp": 245, "weight": 1500, "drive": "FWD"},
    {"key": "kia_ceed", "name": "Kia Ceed", "level": 3, "base": 1700000, "problems": 2, "hp": 128, "weight": 1300, "drive": "FWD"},
    {"key": "hyundai_tucson", "name": "Hyundai Tucson", "level": 3, "base": 2500000, "problems": 2, "hp": 199, "weight": 1550, "drive": "AWD"},
    {"key": "toyota_corolla", "name": "Toyota Corolla", "level": 3, "base": 2200000, "problems": 2, "hp": 140, "weight": 1300, "drive": "FWD"},
    {"key": "mazda_6", "name": "Mazda 6", "level": 3, "base": 2000000, "problems": 2, "hp": 194, "weight": 1450, "drive": "FWD"},
    {"key": "bmw_3_series", "name": "BMW 3 Series", "level": 3, "base": 2800000, "problems": 2, "hp": 258, "weight": 1500, "drive": "RWD"},
    {"key": "mercedes_e_class", "name": "Mercedes E-Class", "level": 3, "base": 3500000, "problems": 2, "hp": 299, "weight": 1700, "drive": "RWD"},
    {"key": "bmw_x5", "name": "BMW X5", "level": 3, "base": 8000000, "problems": 2, "hp": 340, "weight": 2100, "drive": "AWD"},
    {"key": "audi_a6", "name": "Audi A6", "level": 3, "base": 2500000, "problems": 2, "hp": 249, "weight": 1650, "drive": "AWD"},
    {"key": "lexus_rx", "name": "Lexus RX", "level": 3, "base": 4500000, "problems": 2, "hp": 300, "weight": 1950, "drive": "AWD"},
    {"key": "porsche_macan", "name": "Porsche Macan", "level": 3, "base": 5000000, "problems": 2, "hp": 340, "weight": 1870, "drive": "AWD"},


    # ===== МОТОЦИКЛЫ — Уровень 1 =====
    {"key": "vento_riva_2_rx", "name": "Vento Riva 2 RX", "level": 1, "base": 60000, "problems": 4, "type": "moto", "cc": 110, "hp": 6.5, "weight": 95, "drive": "цепь"},
    {"key": "vento_riva_2_sx", "name": "Vento Riva 2 SX", "level": 1, "base": 65000, "problems": 4, "type": "moto", "cc": 110, "hp": 6.5, "weight": 95, "drive": "цепь"},
    {"key": "vento_riva_2_classic", "name": "Vento Riva 2 Classic", "level": 1, "base": 62000, "problems": 4, "type": "moto", "cc": 110, "hp": 6.5, "weight": 95, "drive": "цепь"},
    {"key": "kayo_tt125", "name": "Kayo TT125", "level": 1, "base": 85000, "problems": 4, "type": "moto", "cc": 125, "hp": 11, "weight": 100, "drive": "цепь"},
    {"key": "kayo_tt140", "name": "Kayo TT140", "level": 1, "base": 95000, "problems": 4, "type": "moto", "cc": 140, "hp": 13, "weight": 105, "drive": "цепь"},


    # ===== МОТОЦИКЛЫ — Уровень 2 =====
    {"key": "kayo_k1", "name": "Kayo K1", "level": 2, "base": 140000, "problems": 3, "type": "moto", "cc": 250, "hp": 22, "weight": 120, "drive": "цепь"},
    {"key": "regulmoto_athlete_300", "name": "Regulmoto Athlete 300", "level": 2, "base": 180000, "problems": 3, "type": "moto", "cc": 300, "hp": 26, "weight": 130, "drive": "цепь"},
    {"key": "kews_k16_nb300", "name": "Kews K16 NB300", "level": 2, "base": 220000, "problems": 3, "type": "moto", "cc": 300, "hp": 27, "weight": 130, "drive": "цепь"},
    {"key": "brz_x5_pr250", "name": "BRZ X5 PR250", "level": 2, "base": 160000, "problems": 3, "type": "moto", "cc": 250, "hp": 21, "weight": 125, "drive": "цепь"},
    {"key": "xgz_ktx_pr300", "name": "XGZ KTX PR300", "level": 2, "base": 190000, "problems": 3, "type": "moto", "cc": 300, "hp": 25, "weight": 130, "drive": "цепь"},
    {"key": "bajaj_boxer_150", "name": "Bajaj Boxer 150", "level": 2, "base": 130000, "problems": 3, "type": "moto", "cc": 150, "hp": 12, "weight": 120, "drive": "цепь"},


    # ===== МОТОЦИКЛЫ — Уровень 3 =====
    {"key": "yamaha_yz125", "name": "Yamaha YZ125", "level": 3, "base": 600000, "problems": 2, "type": "moto", "cc": 125, "hp": 35, "weight": 95, "drive": "цепь"},
    {"key": "yamaha_yz250f", "name": "Yamaha YZ250F", "level": 3, "base": 850000, "problems": 2, "type": "moto", "cc": 250, "hp": 40, "weight": 105, "drive": "цепь"},
    {"key": "honda_cb600", "name": "Honda CB600", "level": 3, "base": 700000, "problems": 2, "type": "moto", "cc": 600, "hp": 100, "weight": 200, "drive": "цепь"},
    {"key": "yamaha_r1", "name": "Yamaha R1", "level": 3, "base": 1200000, "problems": 2, "type": "moto", "cc": 1000, "hp": 200, "weight": 200, "drive": "цепь"},
    {"key": "ktm_duke_1390", "name": "KTM Duke 1390", "level": 3, "base": 1900000, "problems": 2, "type": "moto", "cc": 1390, "hp": 190, "weight": 180, "drive": "цепь"},
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


BUSINESSES = {
    "carwash": {"name": "🚿 Автомойка", "price": 500000, "income": 5000, "perk": "Бесплатная мойка"},
    "service": {"name": "🔧 Автосервис", "price": 2000000, "income": 20000, "perk": "Осмотр/диагностика/ремонт -50%"},
    "dealership": {"name": "🏪 Автосалон", "price": 10000000, "income": 100000, "perk": "Точные цены"},
    "factory": {"name": "🏭 Автозавод", "price": 50000000, "income": 500000, "perk": "Бесплатная тачка раз в день"},
    "gas_stations": {"name": "⛽ Сеть АЗС", "price": 200000000, "income": 2000000, "perk": "Бонус ×3"},
}


EVENT_TYPES = [
    {"key": "crisis", "name": "📉 Кризис на рынке", "mult": 0.75, "desc": "Все цены упали на 25%"},
    {"key": "boom", "name": "📈 Рынок растёт", "mult": 1.25, "desc": "Все цены выросли на 25%"},
    {"key": "hype_jdm", "name": "🔥 Хайп на JDM", "mult": 1.5, "desc": "Toyota, Honda, Mazda, Nissan ×1.5"},
    {"key": "hype_bmw", "name": "🔥 Хайп на BMW", "mult": 1.6, "desc": "Все BMW ×1.6"},
    {"key": "hype_toyota", "name": "🔥 Хайп на Toyota", "mult": 1.5, "desc": "Все Toyota ×1.5"},
    {"key": "deficit", "name": "📦 Дефицит запчастей", "mult": 0.85, "desc": "Все цены -15%"},
    {"key": "winter", "name": "❄️ Зимний сезон", "mult": 1.2, "desc": "Кроссоверы и внедорожники +20%"},
    {"key": "fuel", "name": "⛽ Бензин подорожал", "mult": 0.9, "desc": "Прожорливые -10%"},
]


JDM_BRANDS = ["toyota", "honda", "mazda", "nissan", "lexus", "subaru", "mitsubishi"]
SUV_KEYWORDS = ["rav4", "sportage", "creta", "tucson", "tiguan", "kodiaq",
                "x5", "q7", "gle", "rx", "macan", "cayenne"]


# ========== ФУНКЦИИ ==========


def fmt(n):
    return "{:,}".format(int(n)).replace(",", " ")


def get_car_by_key(car_key):
    for c in CARS:
        if c["key"] == car_key:
            return c
    return None


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


def generate_problems(car):
    result = []
    max_problems = car.get("problems", 3)
    num = random.randint(1, max_problems)
    types_list = list(PROBLEMS.keys())
    random.shuffle(types_list)
    for t in types_list[:num]:
        variants = PROBLEMS[t]
        max_idx = min(len(variants) - 1, car.get("level", 1) - 1)
        idx = random.randint(0, max(max_idx, 0))
        name, cost = variants[idx]
        cost = int(cost * (car.get("level", 1) ** 1.5))
        result.append({"type": t, "name": name, "cost": cost, "fixed": False})
    return result


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
        engine_cc INTEGER DEFAULT 0, last_wheelie TEXT,
        washed_until INTEGER DEFAULT 0, service_until INTEGER DEFAULT 0,
        turbo INTEGER DEFAULT 0, seized_until TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_key TEXT, car_name TEXT, car_level INTEGER,
        year INTEGER, mileage INTEGER, price INTEGER,
        owner_name TEXT, problems TEXT, created TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS admins (user_id TEXT PRIMARY KEY, name TEXT, added TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS banned (
        user_id TEXT PRIMARY KEY, name TEXT, reason TEXT, banned_by TEXT, banned_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT, biz_key TEXT, biz_name TEXT,
        bought_at TEXT, last_collect TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT, task_type TEXT, task_data TEXT,
        progress INTEGER DEFAULT 0, target INTEGER DEFAULT 1,
        reward INTEGER DEFAULT 10000, done INTEGER DEFAULT 0,
        date TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS market_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT, event_data TEXT,
        multiplier REAL DEFAULT 1.0,
        started TEXT, ends TEXT, active INTEGER DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS market_multipliers (
        car_key TEXT PRIMARY KEY, multiplier REAL DEFAULT 1.0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS pvp_races (
        code TEXT PRIMARY KEY, creator_id TEXT, creator_name TEXT,
        creator_garage_id INTEGER, bet INTEGER, opponent_id TEXT,
        opponent_garage_id INTEGER, status TEXT DEFAULT 'waiting', created TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS steals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thief_id TEXT, victim_id TEXT, garage_id INTEGER,
        car_name TEXT, stolen_at TEXT, returned INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS chases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT, garage_id INTEGER, car_name TEXT,
        started TEXT, status TEXT DEFAULT 'active')""")
    conn.commit()
    for stmt in [
        "ALTER TABLE garage ADD COLUMN engine_cc INTEGER DEFAULT 0",
        "ALTER TABLE garage ADD COLUMN last_wheelie TEXT",
        "ALTER TABLE garage ADD COLUMN washed_until INTEGER DEFAULT 0",
        "ALTER TABLE garage ADD COLUMN service_until INTEGER DEFAULT 0",
        "ALTER TABLE garage ADD COLUMN turbo INTEGER DEFAULT 0",
        "ALTER TABLE garage ADD COLUMN seized_until TEXT",
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


def has_business(user_id, biz_key):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT 1 FROM businesses WHERE user_id=? AND biz_key=?", (str(user_id), biz_key))
    row = c.fetchone(); conn.close()
    return row is not None


def get_businesses(user_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, biz_key, biz_name, last_collect FROM businesses WHERE user_id=?", (str(user_id),))
    rows = c.fetchall(); conn.close()
    return rows


def main_kb(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔍 Найти тачку", "🏠 Мой гараж")
    markup.add("🏁 Гонки", "🎯 Задания")
    markup.add("🚨 Угон", "🎨 Дрифт")
    markup.add("💰 Баланс", "📊 Рынок")
    markup.add("🏆 Топ", "🎁 Бонус")
    markup.add("👤 Профиль", "💼 Бизнесы")
    if is_admin(uid):
        markup.add("👥 Игроки", "📢 Сообщение")
    return markup
# ========== РЫНОК ==========


def get_market_multiplier(car_key):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT multiplier FROM market_multipliers WHERE car_key=?", (car_key,))
    row = c.fetchone(); conn.close()
    return row[0] if row else 1.0


def get_active_event():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT event_type, event_data, multiplier, started, ends FROM market_events WHERE active=1 ORDER BY id DESC LIMIT 1")
    row = c.fetchone(); conn.close()
    return row


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


# ========== РЫНОК ==========


@bot.message_handler(func=lambda m: m.text == "📊 Рынок")
def market(message):
    if check_ban(message): return
    text = "📊 Рынок\n\n"
    event = get_active_event()
    if event:
        try:
            event_data = json.loads(event[1])
            ends = datetime.strptime(event[4], "%Y-%m-%d %H:%M:%S")
            left = ends - datetime.now()
            h = int(left.total_seconds() // 3600)
            m = int((left.total_seconds() % 3600) // 60)
            text += "📰 АКТИВНОЕ СОБЫТИЕ:\n" + event_data["name"] + "\n"
            text += event_data["desc"] + "\n"
            text += "⏳ Осталось: " + str(h) + " ч " + str(m) + " мин\n\n"
        except Exception: pass
    else:
        text += "📰 Событий нет. Рынок стабилен.\n\n"
    text += "💰 Текущие цены:\n\n"
    for lvl in [1, 2, 3]:
        text += "— Уровень " + str(lvl) + " —\n"
        for car in CARS:
            if car["level"] != lvl: continue
            mult = get_market_multiplier(car["key"])
            new_price = int(car["base"] * mult)
            line = "• " + car["name"] + " — " + fmt(new_price) + " ₽"
            if mult > 1.05: line += " 🔥×" + str(round(mult, 2))
            elif mult < 0.95: line += " 📉×" + str(round(mult, 2))
            text += line + "\n"
        text += "\n"
    if len(text) > 4000:
        bot.send_message(message.chat.id, text[:4000])
        bot.send_message(message.chat.id, text[4000:])
    else:
        bot.send_message(message.chat.id, text)


# ========== ПОИСК ТАЧКИ ==========


@bot.message_handler(func=lambda m: m.text == "🔍 Найти тачку")
def find_car(message):
    if check_ban(message): return
    p = get_player(message.from_user.id)
    if not p:
        bot.send_message(message.chat.id, "Сначала /start"); return
    level = p[4]
    available = [c for c in CARS if c["level"] <= level]
    if not available: available = [c for c in CARS if c["level"] == 1]
    listings = random.sample(available, min(5, len(available)))
    for car in listings:
        year = random.randint(2005, 2023)
        mileage = random.randint(50000, 300000)
        base = car["base"]
        mult = get_market_multiplier(car["key"])
        price = int(base * mult * random.uniform(0.7, 1.3))
        problems = generate_problems(car)
        owner = random.choice(["Артём", "Сергей", "Дмитрий", "Андрей", "Максим",
                                "Иван", "Николай", "Владимир", "Олег", "Роман"])
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("""INSERT INTO listings (car_key, car_name, car_level, year, mileage,
                     price, owner_name, problems, created)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (car["key"], car["name"], car["level"], year, mileage,
                   price, owner, json.dumps(problems),
                   datetime.now().strftime("%d.%m.%Y %H:%M")))
        lid = c.lastrowid
        conn.commit(); conn.close()
        caption = "🚗 " + car["name"] + ", " + str(year) + "\n"
        caption += "💰 " + fmt(price) + " ₽\n"
        caption += "📊 Пробег: " + fmt(mileage) + " км\n"
        if car.get("type") == "moto":
            caption += "🏍 " + str(car.get("cc", "?")) + " куб, " + str(car.get("hp", "?")) + " л.с.\n"
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
        photo = get_photo(car["key"])
        if photo:
            try:
                with open(photo, "rb") as f:
                    bot.send_photo(message.chat.id, f, caption=caption, reply_markup=markup)
                continue
            except Exception as e: print("Photo error:", e)
        bot.send_message(message.chat.id, caption + "\n📷 фото не найдено", reply_markup=markup)


# ========== ОСМОТР ==========


@bot.callback_query_handler(func=lambda c: c.data.startswith("ins_"))
def inspect_car(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    lid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    p = get_player(uid)
    cost = 0 if has_business(uid, "service") else 500
    if p[3] < cost:
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    if cost > 0: c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (cost, uid))
    c.execute("SELECT problems FROM listings WHERE id=?", (lid,))
    row = c.fetchone()
    conn.commit(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Устарело.", show_alert=True); return
    problems = json.loads(row[0])
    if not problems:
        bot.answer_callback_query(call.id, "👀 Осмотр ничего не нашёл.", show_alert=True); return
    found = random.choice(problems)
    prefix = "🆓 " if cost == 0 else "👀 "
    bot.answer_callback_query(call.id, prefix + "Найдено: " + found["name"], show_alert=True)


@bot.callback_query_handler(func=lambda c: c.data.startswith("diag_"))
def diag_car(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    lid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    p = get_player(uid)
    cost = 0 if has_business(uid, "service") else 2000
    if p[3] < cost:
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    if cost > 0: c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (cost, uid))
    c.execute("SELECT problems FROM listings WHERE id=?", (lid,))
    row = c.fetchone()
    conn.commit(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Устарело.", show_alert=True); return
    problems = json.loads(row[0])
    if not problems:
        bot.send_message(call.from_user.id, "👀👀 Проблем нет! 🎉" + (" 🆓" if cost == 0 else ""))
        bot.answer_callback_query(call.id); return
    text = "👀👀 Диагностика" + (" (бесплатно 🆓)" if cost == 0 else "") + ":\n\n"
    total = 0
    for i, pr in enumerate(problems, 1):
        text += str(i) + ". " + pr["name"] + " — ~" + fmt(pr["cost"]) + " ₽\n"
        total += pr["cost"]
    text += "\n💸 Общий ремонт: ~" + fmt(total) + " ₽"
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
    problems = json.loads(problems_json)
    # шанс поломки в пути
    breakdown_chance = 30
    if car_level == 1: breakdown_chance += 10
    elif car_level == 3: breakdown_chance -= 5
    if p[6] >= 80: breakdown_chance -= 10
    breakdown_chance = max(5, min(60, breakdown_chance))
    c.execute("UPDATE players SET money = money - ?, total_deals = total_deals + 1 WHERE user_id=?", (price, uid))
    c.execute("""INSERT INTO garage (user_id, car_key, car_name, car_level, year, mileage,
                 buy_price, problems, engine_cc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (uid, car_key, car_name, car_level, year, mileage, price, problems_json, engine_cc))
    gid = c.lastrowid
    c.execute("DELETE FROM listings WHERE id=?", (lid,))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ Куплено!", show_alert=True)
    task_progress(uid, "buy_cars")
    # поломка в пути
    if random.randint(1, 100) <= breakdown_chance:
        num_new = random.randint(1, 2)
        new_problems = []
        for _ in range(num_new):
            new_prob = generate_random_problem_for_breakdown(car)
            new_problems.append(new_prob)
        problems.extend(new_problems)
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("UPDATE garage SET problems=? WHERE id=?", (json.dumps(problems), gid))
        conn.commit(); conn.close()
        text = "🚗 " + car_name + " куплен!\n\n"
        text += "Но по пути домой...\n"
        if num_new == 1: text += "💥 Машина заглохла на трассе!\n\n"
        else: text += "💥 Сразу две поломки в дороге!\n\n"
        text += "Всплыли проблемы:\n"
        for pr in new_problems:
            text += "• " + pr["name"] + " (~" + fmt(pr["cost"]) + " ₽)\n"
        text += "\nПовезло? Нет."
        bot.send_message(call.from_user.id, text, reply_markup=main_kb(call.from_user.id))
    else:
        bot.send_message(call.from_user.id,
            "🚗 " + car_name + " куплен!\n\nДовезли без приключений. Повезло! ✅",
            reply_markup=main_kb(call.from_user.id))


def generate_random_problem_for_breakdown(car):
    if not car:
        types_list = list(PROBLEMS.keys())
        t = random.choice(types_list)
        name, cost = random.choice(PROBLEMS[t])
        return {"type": t, "name": name, "cost": cost, "fixed": False}
    types_list = list(PROBLEMS.keys())
    t = random.choice(types_list)
    variants = PROBLEMS[t]
    max_idx = min(len(variants) - 1, car.get("level", 1) - 1)
    min_idx = max(0, max_idx - 1)
    idx = random.randint(min_idx, max_idx)
    name, cost = variants[idx]
    cost = int(cost * (car.get("level", 1) ** 1.5))
    return {"type": t, "name": name, "cost": cost, "fixed": False}


@bot.callback_query_handler(func=lambda c: c.data.startswith("skip_"))
def skip_car(call):
    lid = int(call.data.split("_")[1])
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("DELETE FROM listings WHERE id=?", (lid,))
    conn.commit(); conn.close()
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception: pass
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
    bot.send_message(call.from_user.id, "🤝 Цена: " + fmt(price) + " ₽\n\nСколько предложишь?", reply_markup=markup)
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
    # проверяем угнанные тачки
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, garage_id, car_name FROM steals WHERE victim_id=? AND returned=0", (uid,))
    stolen = c.fetchall()
    conn.close()
    if stolen:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for s in stolen:
            markup.add(types.InlineKeyboardButton("⚖️ Суд: " + s[2], callback_data="sue_" + str(s[0])))
        bot.send_message(message.chat.id, "⚖️ У тебя угнали тачки! Подай в суд.", reply_markup=markup)
    photo = get_garage_photo(p[7])
    header = "🏠 Мой гараж (" + str(p[7]) + " слотов)\n\n"
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT id, car_key, car_name, car_level, year, mileage,
                 buy_price, invested, problems, status, engine_cc
                 FROM garage WHERE user_id=? ORDER BY id DESC""", (uid,))
    rows = c.fetchall(); conn.close()
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
    total_value = 0
    lines = []
    for r in rows:
        gid, car_key, car_name, car_level, year, mileage, buy_price, invested, problems_json, status, engine_cc = r
        problems = json.loads(problems_json)
        unfixed = [pr for pr in problems if not pr.get("fixed")]
        car = get_car_by_key(car_key)
        base = car["base"] if car else buy_price
        cond = max(0.3, 1 - len(unfixed) * 0.1)
        est = int(base * cond)
        total_value += est
        status_mark = ""
        if status == "selling": status_mark = " ⏳ продаётся"
        line = "#" + str(gid) + " " + car_name + " (" + str(year) + ")" + status_mark + "\n"
        line += "   💰 Куплено за " + fmt(buy_price) + " ₽\n"
        line += "   📊 Оценка: " + fmt(est) + " ₽\n"
        if engine_cc and engine_cc > 0:
            line += "   🔧 Мотор: " + str(engine_cc) + " куб\n"
        line += "   🔩 Проблем: " + str(len(unfixed)) + "\n"
        lines.append(line)
    text = header + "💰 Капитал гаража: " + fmt(total_value) + " ₽\n\n" + "".join(lines[:5])
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
                 invested, problems, status, engine_cc, turbo, seized_until
                 FROM garage WHERE id=? AND user_id=?""", (gid, uid))
    row = c.fetchone(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    car_key, car_name, car_level, year, mileage, buy_price, invested, problems_json, status, engine_cc, turbo, seized_until = row
    problems = json.loads(problems_json)
    unfixed = [pr for pr in problems if not pr.get("fixed")]
    car = get_car_by_key(car_key)
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
    if turbo:
        text += "🌀 Турбина: есть\n"
    text += "\n🔩 Проблемы (" + str(len(unfixed)) + "):\n"
    if unfixed:
        for pr in unfixed:
            text += "• " + pr["name"] + " (~" + fmt(pr["cost"]) + " ₽)\n"
    else:
        text += "• Нет! 🎉\n"
    seized = False
    if seized_until:
        try:
            s = datetime.strptime(seized_until, "%Y-%m-%d %H:%M:%S")
            if s > datetime.now():
                seized = True
                text += "\n🔒 ИЗЪЯТА ДО " + s.strftime("%d.%m %H:%M")
        except Exception: pass
    markup = types.InlineKeyboardMarkup(row_width=2)
    if not seized:
        if unfixed:
            markup.add(types.InlineKeyboardButton("🔧 Ремонт", callback_data="repair_" + str(gid)))
        if can_swap(car_key) and status == "in_garage":
            markup.add(types.InlineKeyboardButton("🔧 Свап", callback_data="swapmenu_" + str(gid)))
        if car and car.get("type") == "moto" and status == "in_garage":
            markup.add(types.InlineKeyboardButton("🔥 Вили", callback_data="wheelie_" + str(gid)))
        if car and car.get("type") != "moto" and status == "in_garage":
            markup.add(types.InlineKeyboardButton("🎨 Дрифт", callback_data="drift_" + str(gid)))
            if not turbo and car_level <= 3:
                markup.add(types.InlineKeyboardButton("🌀 Турбина", callback_data="turbomenu_" + str(gid)))
        if status == "in_garage":
            markup.add(types.InlineKeyboardButton("💦 Помыть", callback_data="wash_" + str(gid)))
            markup.add(types.InlineKeyboardButton("🔧 ТО", callback_data="service_" + str(gid)))
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
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception: pass
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
        markup.add(types.InlineKeyboardButton(pr["name"] + " — " + fmt(pr["cost"]) + " ₽",
                   callback_data="fix_" + str(gid) + "_" + str(idx)))
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="car_" + str(gid)))
    bot.send_message(call.from_user.id, "🔧 Что ремонтируем?", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("fix_"))
def do_fix(call):
    parts = call.data.split("_")
    gid = int(parts[1]); idx = int(parts[2])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT problems FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone()
    if not row:
        conn.close(); bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    problems = json.loads(row[0])
    if idx >= len(problems) or problems[idx].get("fixed"):
        conn.close(); bot.answer_callback_query(call.id, "Уже отремонтировано.", show_alert=True); return
    conn.close()
    full_cost = problems[idx]["cost"]
    cheap_cost = int(full_cost * 0.5)
    problem_name = problems[idx]["name"]
    has_service = has_business(uid, "service")
    if has_service:
        full_cost = int(full_cost * 0.5)
        cheap_cost = int(full_cost * 0.5)
    text = ("🔧 Ремонт: " + problem_name + "\n\nКак чиним?\n\n"
            "💩 Дешёвый — " + fmt(cheap_cost) + " ₽\n"
            "   Шанс успеха: 40%\n\n"
            "💎 Качественный — " + fmt(full_cost) + " ₽\n"
            "   Шанс успеха: 100%")
    if has_service:
        text += "\n\n🆓 Скидка 50% (Автосервис)"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💩 Дешёвый (" + fmt(cheap_cost) + " ₽)", callback_data="fixgo_" + str(gid) + "_" + str(idx) + "_cheap"),
        types.InlineKeyboardButton("💎 Качественный (" + fmt(full_cost) + " ₽)", callback_data="fixgo_" + str(gid) + "_" + str(idx) + "_good"),
    )
    markup.add(types.InlineKeyboardButton("⬅ Отмена", callback_data="car_" + str(gid)))
    bot.send_message(call.from_user.id, text, reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("fixgo_"))
def fix_go(call):
    parts = call.data.split("_")
    gid = int(parts[1]); idx = int(parts[2]); quality = parts[3]
    uid = str(call.from_user.id)
    p = get_player(uid)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT problems FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone()
    if not row:
        conn.close(); bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    problems = json.loads(row[0])
    if idx >= len(problems) or problems[idx].get("fixed"):
        conn.close(); bot.answer_callback_query(call.id, "Уже отремонтировано.", show_alert=True); return
    full_cost = problems[idx]["cost"]
    problem_name = problems[idx]["name"]
    if has_business(uid, "service"):
        full_cost = int(full_cost * 0.5)
    if quality == "cheap":
        cost = int(full_cost * 0.5)
        success = random.randint(1, 100) <= 40
    else:
        cost = full_cost
        success = True
    if p[3] < cost:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (cost, uid))
    if success:
        problems[idx]["fixed"] = True
        result_text = "✅ " + problem_name + " отремонтировано!\n💸 Заплачено: " + fmt(cost) + " ₽"
        task_progress(uid, "repair")
    else:
        result_text = "❌ " + problem_name + " НЕ отремонтировано!\n💸 Мастер взял деньги и уехал: -" + fmt(cost) + " ₽"
    c.execute("UPDATE garage SET problems=?, invested=invested+? WHERE id=?",
              (json.dumps(problems), cost, gid))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅" if success else "❌")
    bot.send_message(call.from_user.id, result_text)


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
    text = "🔧 Тюнинг мотора\n\nСейчас: " + str(engine_cc or "сток") + " куб\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    if is_alpha(car_key):
        markup.add(
            types.InlineKeyboardButton("🔧 Ремонт стока (5 000₽)", callback_data="swap_" + str(gid) + "_rep"),
            types.InlineKeyboardButton("🔄 125 куб (15 000₽)", callback_data="swap_" + str(gid) + "_125"),
            types.InlineKeyboardButton("🔥 140 куб (25 000₽)", callback_data="swap_" + str(gid) + "_140"),
            types.InlineKeyboardButton("💥 160+ куб (40 000₽)", callback_data="swap_" + str(gid) + "_160"),
        )
    else:
        markup.add(types.InlineKeyboardButton("🔧 Свап 16V (200 000₽)", callback_data="swap_" + str(gid) + "_16v"))
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
    price = prices.get(action, 0); new_cc = ccs.get(action, 0)
    if p[3] < price:
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (price, uid))
    c.execute("UPDATE garage SET engine_cc=?, invested=invested+? WHERE id=?", (new_cc, price, gid))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ Готово!")
    task_progress(uid, "make_swap")
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
    c.execute("SELECT car_key, car_name, last_wheelie FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone()
    if not row:
        conn.close(); bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    car_key, car_name, last_wheelie = row
    if last_wheelie:
        try:
            last = datetime.strptime(last_wheelie, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - last).total_seconds() < 3600:
                left = int(3600 - (datetime.now() - last).total_seconds())
                conn.close()
                bot.answer_callback_query(call.id, "⏳ Отдыхай " + str(left // 60) + " мин.", show_alert=True); return
        except Exception: pass
    roll = random.randint(1, 100)
    c.execute("UPDATE garage SET last_wheelie=? WHERE id=?",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), gid))
    if roll <= 40:
        c.execute("UPDATE players SET reputation = MIN(100, reputation + 3), exp = exp + 10 WHERE user_id=?", (uid,))
        caption = "🔥 " + car_name + " КРАСИВО раздал!\n\n+3 репутации, +10 опыта"
        task_progress(uid, "wheelie")
    elif roll <= 70:
        c.execute("UPDATE players SET exp = exp + 5 WHERE user_id=?", (uid,))
        caption = "😎 " + car_name + " почти убрался, но удержал!\n\n+5 опыта"
        task_progress(uid, "wheelie")
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
            bot.answer_callback_query(call.id, "🔥"); return
        except Exception: pass
    bot.send_message(call.from_user.id, caption)
    bot.answer_callback_query(call.id, "🔥")


# ========== ДРИФТ ==========


@bot.callback_query_handler(func=lambda c: c.data.startswith("drift_"))
def drift_car(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT car_key, car_name, last_wheelie FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone()
    if not row:
        conn.close(); bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    car_key, car_name, last_wheelie = row
    if last_wheelie:
        try:
            last = datetime.strptime(last_wheelie, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - last).total_seconds() < 1800:
                left = int(1800 - (datetime.now() - last).total_seconds())
                conn.close()
                bot.answer_callback_query(call.id, "⏳ Отдыхай " + str(left // 60) + " мин.", show_alert=True); return
        except Exception: pass
    car = get_car_by_key(car_key)
    drive = car.get("drive", "FWD") if car else "FWD"
    chance = 50
    if drive == "RWD": chance = 65
    elif drive == "AWD": chance = 60
    elif drive == "FWD": chance = 40
    roll = random.randint(1, 100)
    c.execute("UPDATE garage SET last_wheelie=? WHERE id=?",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), gid))
    if roll <= chance:
        c.execute("UPDATE players SET reputation = MIN(100, reputation + 5), exp = exp + 10 WHERE user_id=?", (uid,))
        c.execute("UPDATE garage SET invested = MAX(0, invested - 5000) WHERE id=?", (gid,))
        caption = "🎨 " + car_name + " КРАСИВО дрифтанул!\n\nПривод: " + drive + "\n+5 репутации, +10 опыта"
    else:
        c.execute("UPDATE players SET reputation = MAX(0, reputation - 3) WHERE user_id=?", (uid,))
        c.execute("UPDATE garage SET invested = invested + 10000 WHERE id=?", (gid,))
        c.execute("SELECT problems FROM garage WHERE id=?", (gid,))
        problems = json.loads(c.fetchone()[0])
        problems.append({"type": "suspension", "name": "Дрифт убил подвеску", "cost": 30000, "fixed": False})
        c.execute("UPDATE garage SET problems=? WHERE id=?", (json.dumps(problems), gid))
        caption = "💥 " + car_name + " убрался в дрифте!\n\nПривод: " + drive + "\n-3 репутации\nНовая проблема: Дрифт убил подвеску"
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "🎨" if roll <= chance else "💥")
    bot.send_message(call.from_user.id, caption)


# ========== ТУРБИНА ==========


@bot.callback_query_handler(func=lambda c: c.data.startswith("turbomenu_"))
def turbo_menu(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT car_key, car_name, car_level, turbo FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    car_key, car_name, car_level, has_turbo = row
    if has_turbo:
        bot.answer_callback_query(call.id, "✅ Турбина уже стоит.", show_alert=True); return
    prices = {1: 100000, 2: 300000, 3: 800000}
    price = prices.get(car_level, 100000)
    text = ("🌀 Турбина для " + car_name + "\n\nЧто даёт:\n"
            "• +40% к мощности\n• +10% к цене продажи\n• +5% к шансу победы\n\n"
            "⚠️ Риск: 15% что мотор сломается в гонке\n\n💰 Цена: " + fmt(price) + " ₽")
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🌀 Поставить за " + fmt(price) + " ₽",
               callback_data="turboinstall_" + str(gid)))
    markup.add(types.InlineKeyboardButton("⬅ Отмена", callback_data="car_" + str(gid)))
    bot.send_message(call.from_user.id, text, reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("turboinstall_"))
def turbo_install(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    p = get_player(uid)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT car_name, car_level, turbo FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone()
    if not row:
        conn.close(); bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    car_name, car_level, has_turbo = row
    if has_turbo:
        conn.close(); bot.answer_callback_query(call.id, "Уже стоит.", show_alert=True); return
    prices = {1: 100000, 2: 300000, 3: 800000}
    price = prices.get(car_level, 100000)
    if p[3] < price:
        conn.close(); bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (price, uid))
    c.execute("UPDATE garage SET turbo=1, invested=invested+? WHERE id=?", (price, gid))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ Турбина установлена!", show_alert=True)
    bot.send_message(call.from_user.id, "🌀 Турбина установлена на " + car_name + "!")


# ========== МОЙКА И ТО ==========


@bot.callback_query_handler(func=lambda c: c.data.startswith("wash_"))
def wash_car(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    p = get_player(uid)
    cost = 0 if has_business(uid, "carwash") else 500
    if p[3] < cost:
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT washed_until FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone()
    if not row:
        conn.close(); bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    new_until = (row[0] or 0) + 3
    if cost > 0:
        c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (cost, uid))
    c.execute("UPDATE garage SET washed_until=? WHERE id=?", (new_until, gid))
    conn.commit(); conn.close()
    task_progress(uid, "wash_cars")
    bot.answer_callback_query(call.id, "✅ Помыто!", show_alert=True)
    bot.send_message(call.from_user.id, "💦 Помыто! Следующие 3 продажи: -15% к торгу.")


@bot.callback_query_handler(func=lambda c: c.data.startswith("service_"))
def service_car(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    p = get_player(uid)
    cost = 2000
    if p[3] < cost:
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT service_until FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone()
    if not row:
        conn.close(); bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    new_until = (row[0] or 0) + 3
    c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (cost, uid))
    c.execute("UPDATE garage SET service_until=? WHERE id=?", (new_until, gid))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ ТО сделано!", show_alert=True)
    bot.send_message(call.from_user.id, "🔧 ТО! Следующие 3 продажи: -20% к торгу, +10% к цене.")


# ========== ПРОДАЖА ==========


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
    wait_text = (str(wait_min) + " мин " + str(wait_sec) + " сек") if wait_min > 0 else (str(wait_sec) + " сек")
    bot.send_message(int(uid),
        "⏳ Ждём покупателя...\n\nПримерное время: " + wait_text,
        reply_markup=main_kb(int(uid)))
    threading.Thread(target=sell_timer, args=(int(uid), gid, price, wait_seconds), daemon=True).start()


def sell_timer(chat_id, gid, asking_price, wait_seconds):
    time.sleep(wait_seconds)
    uid = str(chat_id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT car_key, car_name, car_level, buy_price, invested,
                 problems, engine_cc, turbo, washed_until, service_until
                 FROM garage WHERE id=?""", (gid,))
    row = c.fetchone()
    if not row:
        conn.close(); return
    (car_key, car_name, car_level, buy_price, invested,
     problems_json, engine_cc, turbo, washed_until, service_until) = row
    problems = json.loads(problems_json)
    unfixed = [p for p in problems if not p.get("fixed")]
    car = get_car_by_key(car_key)
    base = car["base"] if car else buy_price
    cond = max(0.3, 1 - len(unfixed) * 0.1)
    swap_factor = 1.0
    if is_alpha(car_key) and (engine_cc or 0) >= 125: swap_factor = 1.3
    elif car_key.startswith("vaz_") and (engine_cc or 0) >= 1600: swap_factor = 1.4
    service_bonus = 1.10 if (service_until or 0) > 0 else 1.0
    turbo_factor = 1.10 if turbo else 1.0
    market_mult = get_market_multiplier(car_key)
    real_price = int(base * cond * swap_factor * service_bonus * turbo_factor * market_mult)
    p = get_player(uid)
    rep = p[6] if p else 50
    rep_factor = 0.9 + (rep / 100) * 0.2
    max_ok = int(real_price * rep_factor * 1.15)
    haggle_chance = 40
    if (washed_until or 0) > 0: haggle_chance -= 15
    if (service_until or 0) > 0: haggle_chance -= 20
    haggle_chance = max(5, haggle_chance)
    roll = random.randint(1, 100)
    if roll <= (100 - haggle_chance - 10):
        if asking_price <= max_ok:
            event, final_price = "sold", asking_price
        else:
            fp = int(asking_price * 0.9)
            if fp <= max_ok: event, final_price = "haggled", fp
            else: event, final_price = "no_buyer", 0
    elif roll <= (100 - 10):
        fp = int(asking_price * random.uniform(0.8, 0.9))
        if fp <= max_ok: event, final_price = "haggled", fp
        else: event, final_price = "no_buyer", 0
    else:
        event, final_price = "no_buyer", 0
    new_washed = max(0, (washed_until or 0) - 1) if washed_until else 0
    new_service = max(0, (service_until or 0) - 1) if service_until else 0
    c.execute("UPDATE garage SET washed_until=?, service_until=? WHERE id=?",
              (new_washed, new_service, gid))
    if event == "sold":
        find_chance = len(unfixed) * 15
        if rep >= 80: find_chance -= 20
        elif rep < 50: find_chance += 20
        if is_alpha(car_key) and (engine_cc or 0) >= 125: find_chance += 10
        elif car_key.startswith("vaz_") and (engine_cc or 0) >= 1600: find_chance += 10
        find_chance = max(5, min(90, find_chance))
        if random.randint(1, 100) <= find_chance and unfixed:
            num_found = random.randint(1, min(3, len(unfixed)))
            if num_found == 1: discount = 0.10
            elif num_found == 2: discount = 0.20
            else: discount = 0.35
            new_price = int(final_price * (1 - discount))
            found_names = ", ".join(pr["name"] for pr in random.sample(unfixed, num_found))
            c.execute("UPDATE garage SET status='in_garage', sell_price=0 WHERE id=?", (gid,))
            conn.commit(); conn.close()
            bot.send_message(chat_id,
                "🔍 Покупатель нашёл проблемы!\n\nНашёл: " + found_names + "\n"
                "Скидывает: -" + str(int(discount * 100)) + "%\n\n"
                "Предлагает: " + fmt(new_price) + " ₽ (вместо " + fmt(final_price) + ")\n\nСоглашаться?",
                reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                    types.InlineKeyboardButton("✅ Согласиться", callback_data="sellok_" + str(gid) + "_" + str(new_price)),
                    types.InlineKeyboardButton("❌ Отказать", callback_data="sellno_" + str(gid))))
            return
        c.execute("UPDATE players SET money = money + ?, total_deals = total_deals + 1, "
                  "total_earned = total_earned + ?, exp = exp + 20, "
                  "best_deal = MAX(best_deal, ?) WHERE user_id=?",
                  (final_price, final_price, final_price, uid))
        c.execute("DELETE FROM garage WHERE id=?", (gid,))
        conn.commit(); conn.close()
        task_progress(uid, "sell_cars")
        caption = "✅ " + car_name + " ПРОДАНА!\n\n💰 Цена: " + fmt(final_price) + " ₽\n+20 опыта"
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
        bot.send_message(chat_id, "😔 Покупатель не пришёл.\n\n" + car_name + " остаётся в гараже.")


@bot.callback_query_handler(func=lambda c: c.data.startswith("sellok_"))
def sell_ok(call):
    parts = call.data.split("_")
    gid = int(parts[1]); price = int(parts[2])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT car_name FROM garage WHERE id=? AND user_id=?", (gid, uid))
    row = c.fetchone()
    if not row:
        conn.close(); bot.answer_callback_query(call.id, "❌ Уже продано.", show_alert=True); return
    car_name = row[0]
    c.execute("UPDATE players SET money = money + ?, total_deals = total_deals + 1, "
              "total_earned = total_earned + ?, exp = exp + 15 WHERE user_id=?",
              (price, price, uid))
    c.execute("DELETE FROM garage WHERE id=?", (gid,))
    conn.commit(); conn.close()
    task_progress(uid, "sell_cars")
    bot.answer_callback_query(call.id, "✅ Продано!")
    bot.send_message(call.from_user.id, "✅ " + car_name + " продана за " + fmt(price) + " ₽\n+15 опыта")


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




# ========== БИЗНЕСЫ ==========


@bot.message_handler(func=lambda m: m.text == "💼 Бизнесы")
def businesses_menu(message):
    if check_ban(message): return
    uid = str(message.from_user.id)
    p = get_player(uid)
    if not p:
        bot.send_message(message.chat.id, "Сначала /start"); return
    my_biz = get_businesses(uid)
    text = "💼 Бизнесы\n\n"
    if my_biz:
        text += "🏢 Твои бизнесы:\n"
        for b in my_biz:
            biz = BUSINESSES.get(b[1])
            if biz:
                text += "• " + biz["name"] + " — " + fmt(biz["income"]) + " ₽/час\n"
        text += "\n"
    else:
        text += "У тебя пока нет бизнесов.\n\n"
    text += "💰 Доступные:\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    owned_keys = [b[1] for b in my_biz]
    for key, biz in BUSINESSES.items():
        if key in owned_keys: continue
        text += biz["name"] + " — " + fmt(biz["price"]) + " ₽\n"
        text += "   Доход: " + fmt(biz["income"]) + " ₽/час\n"
        text += "   Бонус: " + biz["perk"] + "\n\n"
        markup.add(types.InlineKeyboardButton(biz["name"] + " — " + fmt(biz["price"]) + " ₽",
                   callback_data="bizbuy_" + key))
    if my_biz:
        markup.add(types.InlineKeyboardButton("💰 Собрать доход", callback_data="bizcollect"))
    bot.send_message(message.chat.id, text[:4000], reply_markup=markup)




@bot.callback_query_handler(func=lambda c: c.data.startswith("bizbuy_"))
def biz_buy(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    biz_key = call.data.split("_")[1]
    biz = BUSINESSES.get(biz_key)
    if not biz:
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    uid = str(call.from_user.id)
    p = get_player(uid)
    if has_business(uid, biz_key):
        bot.answer_callback_query(call.id, "Уже куплено.", show_alert=True); return
    if p[3] < biz["price"]:
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (biz["price"], uid))
    c.execute("""INSERT INTO businesses (user_id, biz_key, biz_name, bought_at, last_collect)
                 VALUES (?, ?, ?, ?, ?)""",
              (uid, biz_key, biz["name"],
               datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); conn.close()
    task_progress(uid, "buy_biz")
    bot.answer_callback_query(call.id, "✅ Куплено!", show_alert=True)
    bot.send_message(call.from_user.id,
        "💼 " + biz["name"] + " куплен!\n\n💰 Доход: " + fmt(biz["income"]) + " ₽/час\n🎁 " + biz["perk"],
        reply_markup=main_kb(call.from_user.id))




@bot.callback_query_handler(func=lambda c: c.data == "bizcollect")
def biz_collect(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    uid = str(call.from_user.id)
    my_biz = get_businesses(uid)
    if not my_biz:
        bot.answer_callback_query(call.id, "Нет бизнесов.", show_alert=True); return
    total = 0
    now = datetime.now()
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    for b in my_biz:
        biz = BUSINESSES.get(b[1])
        if not biz: continue
        try:
            last = datetime.strptime(b[3], "%Y-%m-%d %H:%M:%S")
        except Exception:
            last = now
        hours = (now - last).total_seconds() / 3600
        if hours < 1: continue
        earned = int(biz["income"] * hours)
        total += earned
        c.execute("UPDATE businesses SET last_collect=? WHERE id=?",
                  (now.strftime("%Y-%m-%d %H:%M:%S"), b[0]))
    if total == 0:
        conn.close()
        bot.answer_callback_query(call.id, "⏳ Доход ещё не накопился (нужен час).", show_alert=True)
        return
    c.execute("UPDATE players SET money = money + ? WHERE user_id=?", (total, uid))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "💰 +" + fmt(total) + " ₽", show_alert=True)
    bot.send_message(call.from_user.id, "💰 Собрано: " + fmt(total) + " ₽")




# ========== ГОНКИ ==========


@bot.message_handler(func=lambda m: m.text == "🏁 Гонки")
def races_menu(message):
    if check_ban(message): return
    uid = str(message.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM garage WHERE user_id=? AND status='in_garage'", (uid,))
    count = c.fetchone()[0]
    conn.close()
    if count == 0:
        bot.send_message(message.chat.id, "🏁 У тебя нет тачек для гонок."); return
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🤖 С ботом", callback_data="racebot"),
        types.InlineKeyboardButton("👤 С игроком", callback_data="racepvp"),
    )
    bot.send_message(message.chat.id, "🏁 Гонки\n\nВыбери режим:", reply_markup=markup)




@bot.callback_query_handler(func=lambda c: c.data == "raceback")
def race_back(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, "🏁 Гонки\n\nВыбери режим:",
        reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton("🤖 С ботом", callback_data="racebot"),
            types.InlineKeyboardButton("👤 С игроком", callback_data="racepvp")))




@bot.callback_query_handler(func=lambda c: c.data == "racebot")
def racebot_menu(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, car_name FROM garage WHERE user_id=? AND status='in_garage'", (uid,))
    rows = c.fetchall(); conn.close()
    if not rows:
        bot.answer_callback_query(call.id, "Нет тачек.", show_alert=True); return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in rows[:10]:
        markup.add(types.InlineKeyboardButton(r[1], callback_data="rbot_" + str(r[0])))
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="raceback"))
    bot.send_message(call.from_user.id, "🏁 Выбери тачку:", reply_markup=markup)
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data.startswith("rbot_"))
def racebot_difficulty(call):
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT car_key, car_name, engine_cc, turbo, last_wheelie
                 FROM garage WHERE id=? AND user_id=?""", (gid, uid))
    row = c.fetchone(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    car_key, car_name, engine_cc, has_turbo, last_wheelie = row
    if last_wheelie:
        try:
            last = datetime.strptime(last_wheelie, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - last).total_seconds() < 1800:
                left = int(1800 - (datetime.now() - last).total_seconds())
                bot.answer_callback_query(call.id, "⏳ Отдыхай " + str(left // 60) + " мин.", show_alert=True)
                return
        except Exception: pass
    car = get_car_by_key(car_key)
    hp = car.get("hp", 50) if car else 50
    if has_turbo: hp = int(hp * 1.4)
    text = ("🏁 " + car_name + "\n🔧 Твоя мощность: ~" + str(hp) + " л.с.\n"
            "⚠️ Мощность соперника неизвестна\n\nВыбери сложность:")
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🐢 Новичок (ставка 10к)", callback_data="rstart_" + str(gid) + "_easy"),
        types.InlineKeyboardButton("🏎 Опытный (ставка 50к)", callback_data="rstart_" + str(gid) + "_medium"),
        types.InlineKeyboardButton("👑 Чемпион (ставка 200к)", callback_data="rstart_" + str(gid) + "_hard"),
    )
    markup.add(types.InlineKeyboardButton("⬅ Отмена", callback_data="raceback"))
    bot.send_message(call.from_user.id, text, reply_markup=markup)
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data.startswith("rstart_"))
def racebot_start(call):
    parts = call.data.split("_")
    gid = int(parts[1]); difficulty = parts[2]
    uid = str(call.from_user.id)
    p = get_player(uid)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT car_key, car_name, engine_cc, turbo, buy_price
                 FROM garage WHERE id=? AND user_id=?""", (gid, uid))
    row = c.fetchone(); conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    car_key, car_name, engine_cc, has_turbo, buy_price = row
    bets = {"easy": 10000, "medium": 50000, "hard": 200000}
    base_win = {"easy": 65, "medium": 45, "hard": 25}
    bet = bets[difficulty]
    if p[3] < bet:
        bot.answer_callback_query(call.id, "❌ Не хватает на ставку " + fmt(bet) + " ₽", show_alert=True); return
    car = get_car_by_key(car_key)
    hp = car.get("hp", 50) if car else 50
    if has_turbo: hp = int(hp * 1.4)
    bot_hp_range = {"easy": (40, 100), "medium": (100, 250), "hard": (250, 500)}
    bot_hp = random.randint(*bot_hp_range[difficulty])
    hp_diff = hp - bot_hp
    chance = base_win[difficulty] + int(hp_diff / 5)
    if has_turbo: chance += 5
    chance = max(5, min(95, chance))
    # турбина может сломаться
    if has_turbo and random.randint(1, 100) <= 15:
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (bet, uid))
        c.execute("SELECT problems FROM garage WHERE id=?", (gid,))
        problems = json.loads(c.fetchone()[0])
        problems.append({"type": "engine", "name": "Турбина убила мотор", "cost": 200000, "fixed": False})
        c.execute("UPDATE garage SET problems=?, turbo=0, last_wheelie=? WHERE id=?",
                  (json.dumps(problems), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), gid))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "💥 Турбина сдохла", show_alert=True)
        bot.send_message(call.from_user.id,
            "💥 Турбина не выдержала!\n\nМотор сломан, ты проиграл " + fmt(bet) + " ₽.\nРемонт: ~200 000 ₽")
        return
    roll = random.randint(1, 100)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE garage SET last_wheelie=? WHERE id=?",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), gid))
    if roll <= chance:
        prize = bet * 2
        c.execute("UPDATE players SET money = money - ? + ?, exp = exp + 30, reputation = MIN(100, reputation + 2) WHERE user_id=?",
                  (bet, prize, uid))
        conn.commit(); conn.close()
        task_progress(uid, "win_race")
        bot.answer_callback_query(call.id, "🏆 Победа!", show_alert=True)
        bot.send_message(call.from_user.id,
            "🏆 ПОБЕДА!\n\n💰 Выигрыш: " + fmt(prize) + " ₽\n+30 опыта, +2 репутации\n\n"
            "Соперник был: ~" + str(bot_hp) + " л.с.")
    else:
        c.execute("UPDATE players SET money = money - ?, reputation = MAX(0, reputation - 2) WHERE user_id=?",
                  (bet, uid))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "😢 Проиграл", show_alert=True)
        bot.send_message(call.from_user.id,
            "😢 ПРОИГРАЛ\n\n💸 Потерял: " + fmt(bet) + " ₽\n-2 репутации\n\n"
            "Соперник был: ~" + str(bot_hp) + " л.с.")




# ========== PVP ГОНКИ ==========


@bot.callback_query_handler(func=lambda c: c.data == "racepvp")
def racepvp_menu(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ Создать заезд", callback_data="pvpcreate"),
        types.InlineKeyboardButton("🔑 Ввести код", callback_data="pvpjoin"),
    )
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="raceback"))
    bot.send_message(call.from_user.id, "👤 Гонка с игроком\n\nВыбери:", reply_markup=markup)
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data == "pvpcreate")
def pvp_create(call):
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, car_name FROM garage WHERE user_id=? AND status='in_garage'", (uid,))
    rows = c.fetchall(); conn.close()
    if not rows:
        bot.answer_callback_query(call.id, "Нет тачек.", show_alert=True); return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in rows[:10]:
        markup.add(types.InlineKeyboardButton(r[1], callback_data="pvpcar_" + str(r[0])))
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="racepvp"))
    bot.send_message(call.from_user.id, "🏁 Выбери тачку:", reply_markup=markup)
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data.startswith("pvpcar_"))
def pvp_car_select(call):
    gid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    msg = bot.send_message(call.from_user.id, "💰 Какая ставка? (от 1 000 ₽):",
        reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, pvp_set_bet, gid, uid)
    bot.answer_callback_query(call.id)




def pvp_set_bet(message, gid, uid):
    if check_ban(message): return
    try:
        bet = int((message.text or "").strip().replace(" ", ""))
    except ValueError:
        bot.reply_to(message, "❌ Нужно число."); return
    if bet < 1000:
        bot.reply_to(message, "❌ Минимум 1 000 ₽."); return
    p = get_player(uid)
    if p[3] < bet:
        bot.reply_to(message, "❌ Не хватает денег."); return
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO pvp_races (code, creator_id, creator_name,
                 creator_garage_id, bet, status, created)
                 VALUES (?, ?, ?, ?, ?, 'waiting', ?)""",
              (code, uid, p[1], gid, bet, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); conn.close()
    bot.send_message(int(uid),
        "🏁 Заезд создан!\n\n🔑 Код: `" + code + "`\n💰 Ставка: " + fmt(bet) + " ₽\n\n"
        "Передай код другу.\n⚠️ Ждёт 30 минут.",
        parse_mode="Markdown", reply_markup=main_kb(int(uid)))
    threading.Thread(target=pvp_cleanup, args=(code,), daemon=True).start()




def pvp_cleanup(code):
    time.sleep(1800)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT status FROM pvp_races WHERE code=?", (code,))
    row = c.fetchone()
    if row and row[0] == "waiting":
        c.execute("DELETE FROM pvp_races WHERE code=?", (code,))
        conn.commit()
    conn.close()




@bot.callback_query_handler(func=lambda c: c.data == "pvpjoin")
def pvp_join(call):
    uid = str(call.from_user.id)
    msg = bot.send_message(call.from_user.id, "🔑 Введи код заезда:", reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, pvp_join_code, uid)
    bot.answer_callback_query(call.id)




def pvp_join_code(message, uid):
    if check_ban(message): return
    code = (message.text or "").strip().upper()
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT creator_id, bet, status FROM pvp_races WHERE code=?", (code,))
    row = c.fetchone(); conn.close()
    if not row:
        bot.reply_to(message, "❌ Заезд не найден."); return
    creator_id, bet, status = row
    if status != "waiting":
        bot.reply_to(message, "❌ Уже начался."); return
    if str(creator_id) == str(uid):
        bot.reply_to(message, "❌ Свой заезд."); return
    p = get_player(uid)
    if p[3] < bet:
        bot.reply_to(message, "❌ Нужна ставка " + fmt(bet) + " ₽."); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, car_name FROM garage WHERE user_id=? AND status='in_garage'", (uid,))
    rows = c.fetchall(); conn.close()
    if not rows:
        bot.reply_to(message, "❌ У тебя нет тачек."); return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in rows[:10]:
        markup.add(types.InlineKeyboardButton(r[1], callback_data="pvpjoin2_" + code + "_" + str(r[0])))
    bot.send_message(int(uid), "🏁 Выбери тачку:", reply_markup=markup)




@bot.callback_query_handler(func=lambda c: c.data.startswith("pvpjoin2_"))
def pvp_join2(call):
    parts = call.data.split("_")
    code = parts[1]; gid2 = int(parts[2])
    uid2 = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT creator_id, creator_name, creator_garage_id, bet, status FROM pvp_races WHERE code=?", (code,))
    row = c.fetchone()
    if not row or row[4] != "waiting":
        conn.close()
        bot.answer_callback_query(call.id, "❌ Заезд недоступен.", show_alert=True); return
    creator_id, creator_name, gid1, bet, _ = row
    if str(creator_id) == uid2:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Это твой заезд.", show_alert=True); return
    c.execute("SELECT car_key, car_name, engine_cc, turbo FROM garage WHERE id=?", (gid1,))
    car1 = c.fetchone()
    c.execute("SELECT car_key, car_name, engine_cc, turbo FROM garage WHERE id=?", (gid2,))
    car2 = c.fetchone()
    conn.close()
    if not car1 or not car2:
        bot.answer_callback_query(call.id, "❌ Ошибка.", show_alert=True); return
    def get_power(car_row):
        c_key, c_name, c_cc, c_turbo = car_row
        c_data = get_car_by_key(c_key)
        c_hp = c_data.get("hp", 50) if c_data else 50
        if c_turbo: c_hp = int(c_hp * 1.4)
        return c_hp
    hp1 = get_power(car1); hp2 = get_power(car2)
    diff2 = hp2 - hp1
    chance2 = max(10, min(90, 50 + int(diff2 / 5)))
    text2 = ("🏁 Заезд #" + code + "\n\n"
             "🚗 Ты: " + car2[1] + "\n🔧 Мощность: " + str(hp2) + " л.с.\n\n"
             "🆚 Соперник: " + car1[1] + "\n🔧 Мощность: " + str(hp1) + " л.с.\n\n"
             "📊 Твой шанс: " + str(chance2) + "%\n💰 Ставка: " + fmt(bet) + " ₽")
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("✅ Гоняемся", callback_data="pvpgo_" + code + "_" + str(gid2) + "_" + str(gid1)),
        types.InlineKeyboardButton("❌ Отказаться", callback_data="pvpdecline_" + code),
    )
    bot.send_message(call.from_user.id, text2, reply_markup=markup)
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data.startswith("pvpgo_"))
def pvp_go(call):
    parts = call.data.split("_")
    code = parts[1]; gid2 = int(parts[2]); gid1 = int(parts[3])
    uid2 = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT creator_id, creator_name, bet, status FROM pvp_races WHERE code=?", (code,))
    row = c.fetchone()
    if not row or row[3] != "waiting":
        conn.close()
        bot.answer_callback_query(call.id, "❌ Заезд недоступен.", show_alert=True); return
    creator_id, creator_name, bet, _ = row
    c.execute("SELECT car_key, car_name, engine_cc, turbo FROM garage WHERE id=?", (gid1,))
    car1 = c.fetchone()
    c.execute("SELECT car_key, car_name, engine_cc, turbo FROM garage WHERE id=?", (gid2,))
    car2 = c.fetchone()
    conn.close()
    if not car1 or not car2:
        bot.answer_callback_query(call.id, "❌ Ошибка.", show_alert=True); return
    def get_power(car_row):
        c_key, c_name, c_cc, c_turbo = car_row
        c_data = get_car_by_key(c_key)
        c_hp = c_data.get("hp", 50) if c_data else 50
        if c_turbo: c_hp = int(c_hp * 1.4)
        return c_hp
    hp1 = get_power(car1); hp2 = get_power(car2)
    diff2 = hp2 - hp1
    chance2 = max(10, min(90, 50 + int(diff2 / 5)))
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE pvp_races SET opponent_id=?, opponent_garage_id=?, status='ready' WHERE code=?",
              (uid2, gid2, code))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "✅ Готов!")
    bot.send_message(call.from_user.id, "🏁 Ты готов! Ждём подтверждения от " + creator_name + "...")
    chance1 = 100 - chance2
    text1 = ("🏁 Заезд #" + code + "\n\n"
             "🚗 Ты: " + car1[1] + "\n🔧 Мощность: " + str(hp1) + " л.с.\n\n"
             "🆚 Соперник: " + car2[1] + "\n🔧 Мощность: " + str(hp2) + " л.с.\n\n"
             "📊 Твой шанс: " + str(chance1) + "%\n💰 Ставка: " + fmt(bet) + " ₽\n\nСоперник готов. Начинаем?")
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("✅ Гоняемся", callback_data="pvpstart_" + code),
        types.InlineKeyboardButton("❌ Отказаться", callback_data="pvpdecline_" + code),
    )
    try:
        bot.send_message(int(creator_id), text1, reply_markup=markup)
    except Exception: pass




@bot.callback_query_handler(func=lambda c: c.data.startswith("pvpdecline_"))
def pvp_decline(call):
    code = call.data.split("_")[1]
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT creator_id, opponent_id FROM pvp_races WHERE code=?", (code,))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "Уже неактуально.", show_alert=True); return
    creator_id, opponent_id = row
    c.execute("DELETE FROM pvp_races WHERE code=?", (code,))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "❌ Отказ")
    bot.send_message(call.from_user.id, "Ты отказался от заезда.")
    other = opponent_id if str(call.from_user.id) == str(creator_id) else creator_id
    if other:
        try: bot.send_message(int(other), "😔 Соперник отказался. Деньги не списаны.")
        except Exception: pass




@bot.callback_query_handler(func=lambda c: c.data.startswith("pvpstart_"))
def pvp_start(call):
    code = call.data.split("_")[1]
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT creator_id, creator_name, creator_garage_id, bet,
                 opponent_id, opponent_garage_id, status FROM pvp_races WHERE code=?""", (code,))
    row = c.fetchone()
    if not row or row[6] != "ready":
        conn.close()
        bot.answer_callback_query(call.id, "❌ Заезд не готов.", show_alert=True); return
    creator_id, creator_name, gid1, bet, opponent_id, gid2, _ = row
    if str(call.from_user.id) != str(creator_id):
        conn.close()
        bot.answer_callback_query(call.id, "❌ Только создатель.", show_alert=True); return
    c.execute("SELECT car_key, car_name, engine_cc, turbo FROM garage WHERE id=?", (gid1,))
    car1 = c.fetchone()
    c.execute("SELECT car_key, car_name, engine_cc, turbo FROM garage WHERE id=?", (gid2,))
    car2 = c.fetchone()
    conn.close()
    if not car1 or not car2:
        bot.answer_callback_query(call.id, "❌ Ошибка.", show_alert=True); return
    def get_power(car_row):
        c_key, c_name, c_cc, c_turbo = car_row
        c_data = get_car_by_key(c_key)
        c_hp = c_data.get("hp", 50) if c_data else 50
        if c_turbo: c_hp = int(c_hp * 1.4)
        return c_hp
    hp1 = get_power(car1); hp2 = get_power(car2)
    diff = hp1 - hp2
    chance1 = max(10, min(90, 50 + int(diff / 5)))
    p1 = get_player(creator_id); p2 = get_player(opponent_id)
    if p1[3] < bet or p2[3] < bet:
        bot.answer_callback_query(call.id, "❌ Не хватает денег.", show_alert=True); return
    roll = random.randint(1, 100)
    winner_id = creator_id if roll <= chance1 else opponent_id
    loser_id = opponent_id if winner_id == creator_id else creator_id
    winner_name = p1[1] if winner_id == creator_id else p2[1]
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (bet, creator_id))
    c.execute("UPDATE players SET money = money - ? WHERE user_id=?", (bet, opponent_id))
    c.execute("UPDATE players SET money = money + ?, exp = exp + 50, reputation = MIN(100, reputation + 3) WHERE user_id=?",
              (bet * 2, winner_id))
    c.execute("UPDATE players SET reputation = MAX(0, reputation - 2) WHERE user_id=?", (loser_id,))
    c.execute("DELETE FROM pvp_races WHERE code=?", (code,))
    conn.commit(); conn.close()
    task_progress(winner_id, "win_race")
    result = ("🏆 " + winner_name + " ПОБЕДИЛ!\n\n"
              "🆚 " + car1[1] + " (" + str(hp1) + " л.с.) vs " + car2[1] + " (" + str(hp2) + " л.с.)\n"
              "💰 Ставка: " + fmt(bet) + " ₽")
    try: bot.send_message(int(creator_id), result + "\n\nТы: " + ("🏆 ПОБЕДА!" if winner_id == creator_id else "😢 Поражение"))
    except Exception: pass
    try: bot.send_message(int(opponent_id), result + "\n\nТы: " + ("🏆 ПОБЕДА!" if winner_id == opponent_id else "😢 Поражение"))
    except Exception: pass
    bot.answer_callback_query(call.id, "✅ Заезд завершён!")




# ========== ЗАДАНИЯ ==========


@bot.message_handler(func=lambda m: m.text == "🎯 Задания")
def tasks_menu(message):
    if check_ban(message): return
    uid = str(message.from_user.id)
    today = datetime.now().strftime("%d.%m.%Y")
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, task_type, task_data, progress, target, reward, done FROM tasks WHERE user_id=? AND date=?",
              (uid, today))
    rows = c.fetchall()
    if not rows:
        tasks = generate_daily_tasks()
        for t in tasks:
            c.execute("""INSERT INTO tasks (user_id, task_type, task_data, progress, target, reward, done, date)
                         VALUES (?, ?, ?, 0, ?, ?, 0, ?)""",
                      (uid, t["type"], json.dumps(t.get("data", {})), t["target"], t["reward"], today))
        conn.commit()
        c.execute("SELECT id, task_type, task_data, progress, target, reward, done FROM tasks WHERE user_id=? AND date=?",
                  (uid, today))
        rows = c.fetchall()
    conn.close()
    text = "🎯 Задания на сегодня:\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in rows:
        tid, ttype, tdata, progress, target, reward, done = r
        title = task_title(ttype, tdata)
        if done:
            text += "✅ " + title + " — " + fmt(reward) + " ₽ (получено)\n\n"
        else:
            text += "📌 " + title + "\n   Прогресс: " + str(progress) + "/" + str(target) + "\n   Награда: " + fmt(reward) + " ₽\n\n"
            if progress >= target:
                markup.add(types.InlineKeyboardButton("🎁 Забрать " + fmt(reward) + " ₽",
                           callback_data="taskclaim_" + str(tid)))
    bot.send_message(message.chat.id, text[:4000], reply_markup=markup)




def generate_daily_tasks():
    pool = [
        {"type": "sell_cars", "data": {}, "target": 2, "reward": 50000},
        {"type": "buy_cars", "data": {}, "target": 3, "reward": 30000},
        {"type": "make_swap", "data": {}, "target": 1, "reward": 40000},
        {"type": "wash_cars", "data": {}, "target": 3, "reward": 20000},
        {"type": "repair", "data": {}, "target": 2, "reward": 30000},
        {"type": "win_race", "data": {}, "target": 1, "reward": 35000},
        {"type": "wheelie", "data": {}, "target": 2, "reward": 25000},
        {"type": "buy_biz", "data": {}, "target": 1, "reward": 100000},
    ]
    random.shuffle(pool)
    return pool[:3]




def task_title(ttype, tdata_json):
    titles = {
        "sell_cars": "Продать 2 тачки",
        "buy_cars": "Купить 3 тачки",
        "make_swap": "Сделать свап мотора",
        "wash_cars": "Помыть 3 тачки",
        "repair": "Отремонтировать 2 поломки",
        "win_race": "Победить в гонке",
        "wheelie": "Раздать на заднем 2 раза",
        "buy_biz": "Купить бизнес",
    }
    return titles.get(ttype, ttype)




def task_progress(uid, task_type, amount=1):
    today = datetime.now().strftime("%d.%m.%Y")
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE tasks SET progress = progress + ? WHERE user_id=? AND task_type=? AND date=? AND done=0",
              (amount, str(uid), task_type, today))
    conn.commit(); conn.close()




@bot.callback_query_handler(func=lambda c: c.data.startswith("taskclaim_"))
def task_claim(call):
    tid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT reward, progress, target, done FROM tasks WHERE id=? AND user_id=?", (tid, uid))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    reward, progress, target, done = row
    if done:
        conn.close()
        bot.answer_callback_query(call.id, "Уже забрано.", show_alert=True); return
    if progress < target:
        conn.close()
        bot.answer_callback_query(call.id, "Ещё не выполнено.", show_alert=True); return
    c.execute("UPDATE tasks SET done=1 WHERE id=?", (tid,))
    c.execute("UPDATE players SET money = money + ?, exp = exp + 50 WHERE user_id=?", (reward, uid))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "🎁 +" + fmt(reward) + " ₽", show_alert=True)
    bot.send_message(call.from_user.id, "🎁 Награда: " + fmt(reward) + " ₽\n+50 опыта")




# ========== ТОП ==========


@bot.message_handler(func=lambda m: m.text == "🏆 Топ")
def top_players(message):
    if check_ban(message): return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT name, money, total_deals FROM players
                 ORDER BY (money + total_earned) DESC LIMIT 10""")
    rows = c.fetchall(); conn.close()
    if not rows:
        bot.send_message(message.chat.id, "Пока никого нет."); return
    text = "🏆 Топ-10 перекупов:\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, r in enumerate(rows):
        prefix = medals[i] if i < 3 else str(i+1) + "."
        text += prefix + " " + r[0] + " — " + fmt(r[1]) + " ₽ (сделок: " + str(r[2]) + ")\n"
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
            if (datetime.now() - last).total_seconds() < 14400:
                left = int(14400 - (datetime.now() - last).total_seconds())
                h = left // 3600; m = (left % 3600) // 60
                bot.send_message(message.chat.id, "⏳ Бонус через " + str(h) + " ч " + str(m) + " мин.")
                return
        except Exception: pass
    amount = 10000
    if has_business(uid, "gas_stations"):
        amount *= 3
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money = money + ?, last_bonus=? WHERE user_id=?",
              (amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), uid))
    conn.commit(); conn.close()
    bot.send_message(message.chat.id,
        "🎁 Бонус: +" + fmt(amount) + " ₽\n\nПриходи через 4 часа.",
        reply_markup=main_kb(message.from_user.id))




# ========== СОБЫТИЯ РЫНКА ==========


def start_random_event():
    event = random.choice(EVENT_TYPES)
    now = datetime.now()
    ends = now + timedelta(hours=3)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE market_events SET active=0")
    c.execute("""INSERT INTO market_events (event_type, event_data, multiplier, started, ends, active)
                 VALUES (?, ?, ?, ?, ?, 1)""",
              (event["key"], json.dumps(event), event["mult"],
               now.strftime("%Y-%m-%d %H:%M:%S"), ends.strftime("%Y-%m-%d %H:%M:%S")))
    for car in CARS:
        mult = 1.0
        key = car["key"]
        if event["key"] == "crisis": mult = 0.75
        elif event["key"] == "boom": mult = 1.25
        elif event["key"] == "hype_jdm" and any(b in key for b in JDM_BRANDS): mult = 1.5
        elif event["key"] == "hype_bmw" and "bmw" in key: mult = 1.6
        elif event["key"] == "hype_toyota" and "toyota" in key: mult = 1.5
        elif event["key"] == "deficit": mult = 0.85
        elif event["key"] == "winter" and any(k in key for k in SUV_KEYWORDS): mult = 1.2
        elif event["key"] == "fuel":
            if car.get("type") == "moto": mult = 1.1
            else: mult = 0.9
        c.execute("INSERT OR REPLACE INTO market_multipliers (car_key, multiplier) VALUES (?, ?)", (key, mult))
    conn.commit(); conn.close()
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT user_id FROM players")
    uids = [r[0] for r in c.fetchall()]
    conn.close()
    for uid in uids:
        if is_banned(uid): continue
        try:
            bot.send_message(int(uid),
                "📰 СОБЫТИЕ НА РЫНКЕ\n\n" + event["name"] + "\n\n" + event["desc"] +
                "\n\n⏳ Длится 3 часа. Смотри в 📊 Рынок.")
        except Exception: pass
# ========== УГОН ==========


@bot.message_handler(func=lambda m: m.text == "🚨 Угон")
def steal_menu(message):
    if check_ban(message): return
    uid = str(message.from_user.id)
    p = get_player(uid)
    if not p:
        bot.send_message(message.chat.id, "Сначала /start"); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT stolen_at FROM steals WHERE thief_id=? ORDER BY id DESC LIMIT 1", (uid,))
    row = c.fetchone()
    conn.close()
    if row:
        try:
            last = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - last).total_seconds() < 43200:
                left = int(43200 - (datetime.now() - last).total_seconds())
                h = left // 3600; m = (left % 3600) // 60
                bot.send_message(message.chat.id, "⏳ Угон через " + str(h) + " ч " + str(m) + " мин.")
                return
        except Exception: pass
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT DISTINCT p.user_id, p.name, COUNT(g.id) as cars
                 FROM players p JOIN garage g ON p.user_id = g.user_id
                 WHERE p.user_id != ? AND g.status = 'in_garage'
                 GROUP BY p.user_id HAVING cars > 0""", (uid,))
    rows = c.fetchall(); conn.close()
    if not rows:
        bot.send_message(message.chat.id, "😔 Некого грабить."); return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in rows[:10]:
        markup.add(types.InlineKeyboardButton(r[1] + " (" + str(r[2]) + " тачек)",
                   callback_data="stealvictim_" + r[0]))
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="nothing"))
    bot.send_message(message.chat.id,
        "🚨 Угон\n\nВыбери жертву:\n\nШанс: 30%\nПровал: -50 000 ₽, -10 репутации\nКулдаун: 12 часов",
        reply_markup=markup)




@bot.callback_query_handler(func=lambda c: c.data.startswith("stealvictim_"))
def steal_pick_car(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Ты забанен.", show_alert=True); return
    victim_id = call.data.split("_")[1]
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, car_name, car_level FROM garage WHERE user_id=? AND status='in_garage'", (victim_id,))
    rows = c.fetchall(); conn.close()
    if not rows:
        bot.answer_callback_query(call.id, "У жертвы нет тачек.", show_alert=True); return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in rows[:10]:
        markup.add(types.InlineKeyboardButton(r[1] + " (ур. " + str(r[2]) + ")",
                   callback_data="stealgo_" + victim_id + "_" + str(r[0])))
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="nothing"))
    bot.send_message(call.from_user.id, "🚨 Какую тачку угнать?", reply_markup=markup)
    bot.answer_callback_query(call.id)




@bot.callback_query_handler(func=lambda c: c.data.startswith("stealgo_"))
def steal_go(call):
    parts = call.data.split("_")
    victim_id = parts[1]; gid = int(parts[2])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT car_name FROM garage WHERE id=? AND user_id=?", (gid, victim_id))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Тачка уже не там.", show_alert=True); return
    car_name = row[0]
    c.execute("SELECT garage_size FROM players WHERE user_id=?", (uid,))
    max_slots = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM garage WHERE user_id=? AND status='in_garage'", (uid,))
    my_count = c.fetchone()[0]
    if my_count >= max_slots:
        conn.close()
        bot.answer_callback_query(call.id, "❌ У тебя нет места.", show_alert=True); return
    roll = random.randint(1, 100)
    if roll <= 30:
        c.execute("UPDATE garage SET user_id=? WHERE id=?", (uid, gid))
        c.execute("""INSERT INTO steals (thief_id, victim_id, garage_id, car_name, stolen_at)
                     VALUES (?, ?, ?, ?, ?)""",
                  (uid, victim_id, gid, car_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "✅ Угнал!", show_alert=True)
        bot.send_message(call.from_user.id,
            "🚨 УСПЕХ!\n\nУгнал " + car_name + ".\nТачка в твоём гараже.",
            reply_markup=main_kb(call.from_user.id))
        try:
            bot.send_message(int(victim_id),
                "🚨 ТВОЮ ТАЧКУ УГНАЛИ!\n\nУгнали: " + car_name +
                "\nМожешь подать в суд через «🏠 Мой гараж».\nШанс возврата: 50%")
        except Exception: pass
    else:
        c.execute("UPDATE players SET money = MAX(0, money - 50000), reputation = MAX(0, reputation - 10) WHERE user_id=?", (uid,))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "❌ Поймали!", show_alert=True)
        bot.send_message(call.from_user.id,
            "❌ ПРОВАЛ!\n\nТебя поймали на угоне " + car_name + ".\n💸 Штраф: 50 000 ₽\n-10 репутации")




@bot.callback_query_handler(func=lambda c: c.data.startswith("sue_"))
def sue_court(call):
    sid = int(call.data.split("_")[1])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT thief_id, garage_id, car_name FROM steals WHERE id=? AND victim_id=?", (sid, uid))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "❌ Не найдено.", show_alert=True); return
    thief_id, gid, car_name = row
    roll = random.randint(1, 100)
    if roll <= 50:
        c.execute("UPDATE garage SET user_id=? WHERE id=?", (uid, gid))
        c.execute("UPDATE steals SET returned=1 WHERE id=?", (sid,))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "✅ Суд вернул!", show_alert=True)
        bot.send_message(call.from_user.id, "⚖️ Суд вернул " + car_name + "!")
        try: bot.send_message(int(thief_id), "⚖️ Суд вернул " + car_name + " владельцу.")
        except Exception: pass
    else:
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "❌ Суд отказал.", show_alert=True)
        bot.send_message(call.from_user.id, "⚖️ Суд отказал.")




# ========== ПОГОНЯ ==========


def start_chase(uid):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT id, car_name FROM garage
                 WHERE user_id=? AND status='in_garage'
                 AND (seized_until IS NULL OR seized_until='')
                 ORDER BY RANDOM() LIMIT 1""", (uid,))
    row = c.fetchone()
    if not row:
        conn.close(); return False
    gid, car_name = row
    c.execute("""INSERT INTO chases (user_id, garage_id, car_name, started, status)
                 VALUES (?, ?, ?, ?, 'active')""",
              (uid, gid, car_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    cid = c.lastrowid
    conn.commit(); conn.close()
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🏎 Уехать (риск)", callback_data="chase_run_" + str(cid)),
        types.InlineKeyboardButton("🚔 Сдаться (20к)", callback_data="chase_giveup_" + str(cid)),
        types.InlineKeyboardButton("❌ Игнорировать", callback_data="chase_ignore_" + str(cid)),
    )
    try:
        bot.send_message(int(uid),
            "🚔 ПОГОНЯ!\n\nПолиция заметила твою " + car_name + ".\nЧто делаешь?",
            reply_markup=markup)
        return True
    except Exception:
        return False




@bot.callback_query_handler(func=lambda c: c.data.startswith("chase_run_"))
def chase_run(call):
    cid = int(call.data.split("_")[2])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT garage_id, car_name, status FROM chases WHERE id=? AND user_id=?", (cid, uid))
    row = c.fetchone()
    if not row or row[2] != "active":
        conn.close(); bot.answer_callback_query(call.id, "❌ Устарело.", show_alert=True); return
    gid, car_name, _ = row
    roll = random.randint(1, 100)
    if roll <= 50:
        c.execute("UPDATE chases SET status='escaped' WHERE id=?", (cid,))
        c.execute("UPDATE players SET reputation = MIN(100, reputation + 10), exp = exp + 30 WHERE user_id=?", (uid,))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "🏎 Ушёл!", show_alert=True)
        bot.send_message(call.from_user.id, "🏎 ТЫ УШЁЛ!\n+10 репутации, +30 опыта")
    else:
        seized = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE chases SET status='caught' WHERE id=?", (cid,))
        c.execute("UPDATE garage SET seized_until=? WHERE id=?", (seized, gid))
        c.execute("UPDATE players SET money = MAX(0, money - 100000), reputation = MAX(0, reputation - 10) WHERE user_id=?", (uid,))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "🚔 Поймали", show_alert=True)
        bot.send_message(call.from_user.id,
            "🚔 ПОЙМАЛИ!\n\n💸 Штраф: 100 000 ₽\n-10 репутации\n\n🔒 " + car_name + " изъята на 24 ч.")




@bot.callback_query_handler(func=lambda c: c.data.startswith("chase_giveup_"))
def chase_giveup(call):
    cid = int(call.data.split("_")[2])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT car_name, status FROM chases WHERE id=? AND user_id=?", (cid, uid))
    row = c.fetchone()
    if not row or row[1] != "active":
        conn.close(); bot.answer_callback_query(call.id, "Устарело.", show_alert=True); return
    c.execute("UPDATE chases SET status='gaveup' WHERE id=?", (cid,))
    c.execute("UPDATE players SET money = MAX(0, money - 20000), reputation = MAX(0, reputation - 2) WHERE user_id=?", (uid,))
    conn.commit(); conn.close()
    bot.answer_callback_query(call.id, "🚔 Сдался", show_alert=True)
    bot.send_message(call.from_user.id, "🚔 Ты сдался.\n💸 Штраф: 20 000 ₽")




@bot.callback_query_handler(func=lambda c: c.data.startswith("chase_ignore_"))
def chase_ignore(call):
    cid = int(call.data.split("_")[2])
    uid = str(call.from_user.id)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT garage_id, car_name, status FROM chases WHERE id=? AND user_id=?", (cid, uid))
    row = c.fetchone()
    if not row or row[2] != "active":
        conn.close(); bot.answer_callback_query(call.id, "Устарело.", show_alert=True); return
    gid, car_name, _ = row
    roll = random.randint(1, 100)
    if roll <= 30:
        c.execute("UPDATE chases SET status='ignored_ok' WHERE id=?", (cid,))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "Пронесло!", show_alert=True)
        bot.send_message(call.from_user.id, "😅 Пронесло. " + car_name + " осталась.")
    else:
        c.execute("UPDATE chases SET status='confiscated' WHERE id=?", (cid,))
        c.execute("DELETE FROM garage WHERE id=?", (gid,))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "🚨 Конфискация!", show_alert=True)
        bot.send_message(call.from_user.id, "🚨 ТАЧКУ КОНФИСКОВАЛИ!\n\n" + car_name + " изъята навсегда.")




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
    bot.reply_to(message, "✅ Ты теперь админ!\n\n/adminhelp — команды.",
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
            "/addmoney @ник 100000 — добавить деньги\n"
            "/takemoney @ник 50000 — забрать деньги\n"
            "/setmoney @ник 500000 — установить баланс\n"
            "/addexp @ник 500 — добавить опыт\n"
            "/addrep @ник 10 — добавить репутацию\n"
            "/setrep @ник 100 — установить репутацию\n"
            "/setgarage @ник 5 — установить гараж\n"
            "/addcar @ник vaz_2107 — выдать машину\n"
            "/resetplayer @ник — сбросить игрока\n\n"
            "/ban @ник причина — забанить\n"
            "/unban @ник — разбанить\n"
            "/banlist — чёрный список\n"
            "/users — все игроки\n\n"
            "/admin — стать админом\n"
            "/unadmin — снять с себя\n"
            "/admins — управление админами (владелец)")
    bot.send_message(message.chat.id, text)




@bot.message_handler(commands=['addmoney'])
def admin_addmoney(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /addmoney @ник 100000"); return
    try: amount = int(parts[2])
    except ValueError: bot.reply_to(message, "❌ Сумма — число."); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Не найден."); return
    tid, tname, tmoney = row
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money = money + ? WHERE user_id=?", (amount, tid))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": +" + fmt(amount) + " ₽")
    try: bot.send_message(int(tid), "💰 Админ начислил " + fmt(amount) + " ₽")
    except Exception: pass




@bot.message_handler(commands=['takemoney'])
def admin_takemoney(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /takemoney @ник 50000"); return
    try: amount = int(parts[2])
    except ValueError: bot.reply_to(message, "❌ Сумма — число."); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Не найден."); return
    tid, tname, tmoney = row
    new_money = max(0, tmoney - amount)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money=? WHERE user_id=?", (new_money, tid))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": -" + fmt(amount) + " ₽")




@bot.message_handler(commands=['setmoney'])
def admin_setmoney(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /setmoney @ник 500000"); return
    try: amount = int(parts[2])
    except ValueError: bot.reply_to(message, "❌ Сумма — число."); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Не найден."); return
    tid, tname, _ = row
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET money=? WHERE user_id=?", (amount, tid))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": баланс = " + fmt(amount))




@bot.message_handler(commands=['addexp'])
def admin_addexp(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /addexp @ник 500"); return
    try: amount = int(parts[2])
    except ValueError: bot.reply_to(message, "❌ Опыт — число."); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Не найден."); return
    tid, tname, _ = row
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET exp = exp + ? WHERE user_id=?", (amount, tid))
    c.execute("SELECT exp, level FROM players WHERE user_id=?", (tid,))
    new_exp, new_level = c.fetchone()
    calc_level = 1 + new_exp // 1000
    if calc_level > new_level:
        c.execute("UPDATE players SET level=? WHERE user_id=?", (calc_level, tid))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": +" + str(amount) + " опыта")




@bot.message_handler(commands=['addrep'])
def admin_addrep(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /addrep @ник 10"); return
    try: amount = int(parts[2])
    except ValueError: bot.reply_to(message, "❌ Репутация — число."); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Не найден."); return
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
        bot.reply_to(message, "Формат: /setrep @ник 100"); return
    try: amount = int(parts[2])
    except ValueError: bot.reply_to(message, "❌ Репутация — число."); return
    amount = max(0, min(100, amount))
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Не найден."); return
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
        bot.reply_to(message, "Формат: /setgarage @ник 5"); return
    try: level = int(parts[2])
    except ValueError: bot.reply_to(message, "❌ 1-5."); return
    level = max(1, min(5, level))
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Не найден."); return
    tid, tname, _ = row
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE players SET garage_size=? WHERE user_id=?", (level, tid))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + ": гараж = " + str(level))




@bot.message_handler(commands=['addcar'])
def admin_addcar(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /addcar @ник vaz_2107"); return
    car_key = parts[2].strip()
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Не найден."); return
    tid, tname, _ = row
    car = get_car_by_key(car_key)
    if not car:
        bot.reply_to(message, "❌ Машина не найдена."); return
    problems = generate_problems(car)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT garage_size FROM players WHERE user_id=?", (tid,))
    max_slots = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM garage WHERE user_id=? AND status='in_garage'", (tid,))
    used = c.fetchone()[0]
    if used >= max_slots:
        conn.close()
        bot.reply_to(message, "❌ Нет места."); return
    engine_cc = car.get("cc", 0)
    c.execute("""INSERT INTO garage (user_id, car_key, car_name, car_level, year, mileage,
                 buy_price, problems, engine_cc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (tid, car["key"], car["name"], car["level"],
               random.randint(2005, 2023), random.randint(50000, 300000),
               0, json.dumps(problems), engine_cc))
    conn.commit(); conn.close()
    bot.reply_to(message, "✅ " + tname + " получил: " + car["name"])
    try: bot.send_message(int(tid), "🎁 Админ выдал " + car["name"])
    except Exception: pass




@bot.message_handler(commands=['resetplayer'])
def admin_resetplayer(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Только админ."); return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Формат: /resetplayer @ник"); return
    row = find_player_by_username(parts[1])
    if not row:
        bot.reply_to(message, "❌ Не найден."); return
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
    try: bot.send_message(int(tid), "⚠️ Твой прогресс сброшен.")
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
                 ORDER BY money DESC LIMIT 30""")
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
    text = "👤 Профиль игрока\n\nИмя: " + p[1] + "\n"
    if p[2]: text += "@" + p[2] + "\n"
    text += "ID: `" + p[0] + "`\n\n"
    text += "💰 Баланс: " + fmt(p[3]) + " ₽\n"
    text += "📈 Уровень: " + str(p[4]) + " (" + str(p[5]) + " опыта)\n"
    text += "⭐ Репутация: " + str(p[6]) + "/100\n"
    text += "🏠 Гараж: " + str(p[7]) + " слотов (" + str(cars_count) + " занято)\n\n"
    text += "🤝 Сделок: " + str(p[8]) + "\n"
    text += "💵 Заработано: " + fmt(p[9]) + " ₽\n"
    text += "🏆 Лучшая сделка: " + fmt(p[10]) + " ₽\n"
    text += "📅 Регистрация: " + (p[11] or "?")
    if banned:
        text += "\n\n🚫 ЗАБАНЕН: " + (banned[0] or "без причины")
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
            bot.answer_callback_query(call.id, "❌ Нельзя владельца", show_alert=True); return
        c.execute("INSERT OR REPLACE INTO banned (user_id, name, reason, banned_by, banned_at) VALUES (?, ?, ?, ?, ?)",
                  (target_id, row[0], "по решению админа",
                   call.from_user.first_name or "Админ",
                   datetime.now().strftime("%d.%m.%Y %H:%M")))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, "🚫 Забанен", show_alert=True)
        try: bot.send_message(int(target_id), "🚫 Тебя забанили.")
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
        bot.reply_to(message, "❌ Нельзя владельца."); return
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




# ========== АДМИНЫ (владелец) ==========


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




# ========== РАССЫЛКА ==========


@bot.message_handler(func=lambda m: m.text == "📢 Сообщение")
def ann_menu(message):
    if check_ban(message): return
    if not is_admin(message.from_user.id): return
    msg = bot.send_message(message.chat.id, "Текст сообщения:", reply_markup=types.ForceReply())
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
    while True:
        time.sleep(3600)




def events_worker():
    while True:
        try:
            time.sleep(3 * 3600)
            start_random_event()
        except Exception as e:
            print("Events error:", e)
            time.sleep(60)




def chase_worker():
    while True:
        try:
            time.sleep(3600)
            conn = sqlite3.connect(DB_FILE); c = conn.cursor()
            c.execute("""SELECT DISTINCT user_id FROM garage
                         WHERE status='in_garage'
                         AND (seized_until IS NULL OR seized_until='')""")
            uids = [r[0] for r in c.fetchall()]
            conn.close()
            if not uids: continue
            count = random.randint(1, min(2, len(uids)))
            victims = random.sample(uids, count)
            for uid in victims:
                if is_banned(uid): continue
                start_chase(uid)
        except Exception as e:
            print("Chase error:", e)
            time.sleep(60)




# ========== ЗАПУСК ==========


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
    threading.Thread(target=chase_worker, daemon=True).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
