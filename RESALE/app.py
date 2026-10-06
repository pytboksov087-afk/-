# -*- coding: utf-8 -*-
"""
Перекуп Тачек — Telegram-бот игры про покупку/продажу авто и мото.
Хостинг: BotHost (Flask + threading)
ИСПРАВЛЕНО: локальные картинки вместо Wikimedia, шрифты для Linux
"""

import os
import io
import sqlite3
import random
import time
import threading
import json
import re
import math
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import requests
import telebot
from telebot import types
from PIL import Image, ImageDraw, ImageFont

# ─── КОНФИГ ───────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
ADMIN_CODE = "DEL202"
DB_PATH = "cars.db"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
PORT = int(os.environ.get("PORT", "5000"))

# Папка с картинками
IMAGES_DIR = Path(__file__).resolve().parent.parent / "images" if Path(__file__).resolve().parent.parent / "images" .exists() else Path(__file__).resolve().parent / "images"
if not IMAGES_DIR.exists():
    IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# ─── ДАННЫЕ ТРАНСПОРТА ────────────────────────────────

CARS = {
    # Уровень 1 — советские
    1: [
        {"brand": "ВАЗ", "model": "2101", "year": 1970, "base_price": 30000, "type": "Авто", "wm_query": "VAZ-2101 sedan"},
        {"brand": "ВАЗ", "model": "2103", "year": 1972, "base_price": 35000, "type": "Авто", "wm_query": "VAZ-2103 sedan"},
        {"brand": "ВАЗ", "model": "2106", "year": 1976, "base_price": 40000, "type": "Авто", "wm_query": "VAZ-2106 sedan"},
        {"brand": "ВАЗ", "model": "2107", "year": 1982, "base_price": 45000, "type": "Авто", "wm_query": "VAZ-2107 sedan"},
        {"brand": "ВАЗ", "model": "2109", "year": 1987, "base_price": 50000, "type": "Авто", "wm_query": "VAZ-2109 hatchback"},
        {"brand": "ВАЗ", "model": "2110", "year": 1995, "base_price": 60000, "type": "Авто", "wm_query": "VAZ-2110 sedan"},
        {"brand": "ВАЗ", "model": "2114", "year": 2001, "base_price": 65000, "type": "Авто", "wm_query": "VAZ-2114 hatchback"},
        {"brand": "Москвич", "model": "2140", "year": 1976, "base_price": 25000, "type": "Авто", "wm_query": "Moskvitch 2140 sedan"},
        {"brand": "ЗАЗ", "model": "968", "year": 1971, "base_price": 20000, "type": "Авто", "wm_query": "ZAZ-968"},
        {"brand": "ГАЗ", "model": "3110 Волга", "year": 1997, "base_price": 55000, "type": "Авто", "wm_query": "GAZ-3110 Volga"},
    ],
    # Уровень 1 — мотоциклы (доступные/китайцы)
    11: [
        {"brand": "Alpha", "model": "RX", "year": 2018, "base_price": 35000, "type": "Мото", "wm_query": "Alpha RX motorcycle"},
        {"brand": "Alpha", "model": "SX", "year": 2018, "base_price": 38000, "type": "Мото", "wm_query": "Alpha SX motorcycle"},
        {"brand": "Alpha", "model": "CX", "year": 2019, "base_price": 42000, "type": "Мото", "wm_query": "Alpha CX motorcycle"},
        {"brand": "Kevs", "model": "K16", "year": 2020, "base_price": 48000, "type": "Мото", "wm_query": "Kevs K16 enduro"},
        {"brand": "Kayo", "model": "K1", "year": 2021, "base_price": 55000, "type": "Мото", "wm_query": "Kayo K1 motorcycle"},
        {"brand": "Irbis", "model": "TTR 250", "year": 2019, "base_price": 50000, "type": "Мото", "wm_query": "Irbis TTR 250 enduro"},
    ],
    # Уровень 2 — бюджетные иномарки
    2: [
        {"brand": "Лада", "model": "Гранта", "year": 2015, "base_price": 350000, "type": "Авто", "wm_query": "Lada Granta sedan"},
        {"brand": "Лада", "model": "Веста", "year": 2018, "base_price": 600000, "type": "Авто", "wm_query": "Lada Vesta sedan"},
        {"brand": "Kia", "model": "Rio", "year": 2017, "base_price": 800000, "type": "Авто", "wm_query": "Kia Rio UB sedan"},
        {"brand": "Hyundai", "model": "Solaris", "year": 2016, "base_price": 750000, "type": "Авто", "wm_query": "Hyundai Solaris sedan"},
        {"brand": "Renault", "model": "Logan", "year": 2015, "base_price": 500000, "type": "Авто", "wm_query": "Renault Logan sedan"},
        {"brand": "Volkswagen", "model": "Polo", "year": 2017, "base_price": 900000, "type": "Авто", "wm_query": "Volkswagen Polo sedan"},
        {"brand": "Skoda", "model": "Rapid", "year": 2018, "base_price": 850000, "type": "Авто", "wm_query": "Skoda Rapid sedan"},
        {"brand": "Ford", "model": "Focus", "year": 2016, "base_price": 700000, "type": "Авто", "wm_query": "Ford Focus sedan"},
        {"brand": "Chevrolet", "model": "Cruze", "year": 2014, "base_price": 600000, "type": "Авто", "wm_query": "Chevrolet Cruze sedan"},
        {"brand": "Nissan", "model": "Almera", "year": 2015, "base_price": 650000, "type": "Авто", "wm_query": "Nissan Almera sedan"},
    ],
    # Уровень 2 — мотоциклы
    22: [
        {"brand": "Bajaj", "model": "Pulsar 200", "year": 2016, "base_price": 120000, "type": "Мото", "wm_query": "Bajaj Pulsar 200"},
        {"brand": "ИЖ", "model": "Планета 5", "year": 2005, "base_price": 80000, "type": "Мото", "wm_query": "IZH Planeta 5"},
        {"brand": "Урал", "model": "М-67", "year": 2008, "base_price": 90000, "type": "Мото", "wm_query": "Ural M-67"},
        {"brand": "Kawasaki", "model": "Ninja 300", "year": 2014, "base_price": 250000, "type": "Мото", "wm_query": "Kawasaki Ninja 300"},
    ],
    # Уровень 3 — средний класс
    3: [
        {"brand": "Toyota", "model": "Camry XV70", "year": 2018, "base_price": 2200000, "type": "Авто", "wm_query": "Toyota Camry XV70 sedan"},
        {"brand": "Toyota", "model": "RAV4 XA50", "year": 2019, "base_price": 2500000, "type": "Авто", "wm_query": "Toyota RAV4 XA50"},
        {"brand": "Honda", "model": "Accord", "year": 2018, "base_price": 2000000, "type": "Авто", "wm_query": "Honda Accord sedan"},
        {"brand": "Mazda", "model": "6", "year": 2019, "base_price": 2100000, "type": "Авто", "wm_query": "Mazda 6 sedan"},
        {"brand": "Hyundai", "model": "Tucson", "year": 2020, "base_price": 2300000, "type": "Авто", "wm_query": "Hyundai Tucson"},
        {"brand": "Kia", "model": "Sportage", "year": 2020, "base_price": 2200000, "type": "Авто", "wm_query": "Kia Sportage"},
        {"brand": "Volkswagen", "model": "Tiguan", "year": 2019, "base_price": 2400000, "type": "Авто", "wm_query": "Volkswagen Tiguan"},
        {"brand": "Skoda", "model": "Kodiaq", "year": 2020, "base_price": 2600000, "type": "Авто", "wm_query": "Skoda Kodiaq"},
        {"brand": "BMW", "model": "3 E90", "year": 2011, "base_price": 1800000, "type": "Авто", "wm_query": "BMW E90 sedan"},
        {"brand": "Audi", "model": "A4 B8", "year": 2012, "base_price": 1700000, "type": "Авто", "wm_query": "Audi A4 B8 sedan"},
    ],
    # Уровень 3 — мотоциклы
    33: [
        {"brand": "Kawasaki", "model": "Ninja 400", "year": 2019, "base_price": 450000, "type": "Мото", "wm_query": "Kawasaki Ninja 400"},
        {"brand": "KTM", "model": "Duke 390", "year": 2020, "base_price": 400000, "type": "Мото", "wm_query": "KTM Duke 390"},
        {"brand": "Honda", "model": "CB600F Hornet", "year": 2014, "base_price": 500000, "type": "Мото", "wm_query": "Honda CB600F Hornet"},
        {"brand": "Yamaha", "model": "YZF-R6", "year": 2015, "base_price": 600000, "type": "Мото", "wm_query": "Yamaha YZF-R6"},
    ],
    # Уровень 4 — премиум
    4: [
        {"brand": "BMW", "model": "5 F10", "year": 2014, "base_price": 3500000, "type": "Авто", "wm_query": "BMW F10 sedan"},
        {"brand": "BMW", "model": "X5 F15", "year": 2015, "base_price": 4500000, "type": "Авто", "wm_query": "BMW X5 F15"},
        {"brand": "Audi", "model": "A6 C7", "year": 2015, "base_price": 3200000, "type": "Авто", "wm_query": "Audi A6 C7 sedan"},
        {"brand": "Audi", "model": "Q7 4M", "year": 2016, "base_price": 5000000, "type": "Авто", "wm_query": "Audi Q7 4M"},
        {"brand": "Mercedes-Benz", "model": "E W213", "year": 2018, "base_price": 4000000, "type": "Авто", "wm_query": "Mercedes-Benz W213 sedan"},
        {"brand": "Mercedes-Benz", "model": "S W222", "year": 2016, "base_price": 7000000, "type": "Авто", "wm_query": "Mercedes-Benz W222 sedan"},
        {"brand": "Mercedes-Benz", "model": "GLE", "year": 2018, "base_price": 5500000, "type": "Авто", "wm_query": "Mercedes-Benz GLE SUV"},
        {"brand": "Lexus", "model": "RX", "year": 2018, "base_price": 4200000, "type": "Авто", "wm_query": "Lexus RX"},
        {"brand": "Porsche", "model": "Macan", "year": 2017, "base_price": 4500000, "type": "Авто", "wm_query": "Porsche Macan"},
        {"brand": "Porsche", "model": "Cayenne", "year": 2017, "base_price": 5500000, "type": "Авто", "wm_query": "Porsche Cayenne"},
    ],
    # Уровень 4 — мотоциклы
    44: [
        {"brand": "Suzuki", "model": "GSX-R600", "year": 2016, "base_price": 700000, "type": "Мото", "wm_query": "Suzuki GSX-R600"},
        {"brand": "Honda", "model": "CBR 600RR", "year": 2015, "base_price": 750000, "type": "Мото", "wm_query": "Honda CBR 600RR"},
        {"brand": "BMW", "model": "R1200GS", "year": 2017, "base_price": 900000, "type": "Мото", "wm_query": "BMW R1200GS"},
        {"brand": "Suzuki", "model": "V-Strom 650", "year": 2018, "base_price": 800000, "type": "Мото", "wm_query": "Suzuki V-Strom 650"},
    ],
    # Уровень 5 — эксклюзив
    5: [
        {"brand": "Ferrari", "model": "488 GTB", "year": 2018, "base_price": 20000000, "type": "Авто", "wm_query": "Ferrari 488 GTB"},
        {"brand": "Lamborghini", "model": "Huracan", "year": 2018, "base_price": 22000000, "type": "Авто", "wm_query": "Lamborghini Huracan"},
        {"brand": "McLaren", "model": "720S", "year": 2019, "base_price": 25000000, "type": "Авто", "wm_query": "McLaren 720S"},
        {"brand": "Bentley", "model": "Continental GT", "year": 2018, "base_price": 18000000, "type": "Авто", "wm_query": "Bentley Continental GT"},
        {"brand": "Rolls-Royce", "model": "Ghost", "year": 2018, "base_price": 30000000, "type": "Авто", "wm_query": "Rolls-Royce Ghost"},
        {"brand": "Porsche", "model": "911 991", "year": 2018, "base_price": 12000000, "type": "Авто", "wm_query": "Porsche 911 991"},
        {"brand": "Tesla", "model": "Model S", "year": 2019, "base_price": 8000000, "type": "Авто", "wm_query": "Tesla Model S"},
        {"brand": "Mercedes-Benz", "model": "G-Class W463", "year": 2019, "base_price": 15000000, "type": "Авто", "wm_query": "Mercedes-Benz G-Class W463"},
        {"brand": "Lamborghini", "model": "Urus", "year": 2019, "base_price": 20000000, "type": "Авто", "wm_query": "Lamborghini Urus"},
        {"brand": "Bugatti", "model": "Chiron", "year": 2019, "base_price": 50000000, "type": "Авто", "wm_query": "Bugatti Chiron"},
    ],
    # Уровень 5 — мотоциклы
    55: [
        {"brand": "Yamaha", "model": "YZF-R1", "year": 2019, "base_price": 1500000, "type": "Мото", "wm_query": "Yamaha YZF-R1"},
        {"brand": "Honda", "model": "Africa Twin", "year": 2020, "base_price": 1300000, "type": "Мото", "wm_query": "Honda Africa Twin"},
    ],
}

ALL_LEVELS = [1, 11, 2, 22, 3, 33, 4, 44, 5, 55]

LEVEL_NAMES = {
    1: "Советские тачки",
    11: "Дешёвые мотоциклы",
    2: "Бюджетные иномарки",
    22: "Народные мотоциклы",
    3: "Средний класс",
    33: "Спортбайки",
    4: "Премиум",
    44: "Тяжёлые мотоциклы",
    5: "Эксклюзив",
    55: "Топовые мотоциклы",
}

GARAGE_DESCRIPTIONS = {
    1: "🏚 Гараж-коробка на окраине. Сыро, холодно, зато свой.",
    2: "🔧 Обычный гараж в кооперативе. Есть свет и яма.",
    3: "🏢 Тёплый паркинг под домом. Камеры, охрана.",
    4: "🏆 Крытое парковочное место в бизнес-центре.",
    5: "✨ Подземный паркинг с лифтом. Премиум-зона.",
    6: "🏰 Частный бокс на 3 машины. Своё помещение.",
    7: "👑 Автосалон-мини. Стеклянные стены, подсветка.",
    8: "💎 Шоурум в центре города. Витрины, кофе-бар.",
    9: "🚀 Ангар на 10 машин. Сервисная зона, подъёмники.",
    10: "👑 Элитная коллекция. Музей эксклюзивных авто.",
}

def get_garage_desc(level):
    return GARAGE_DESCRIPTIONS.get(level, GARAGE_DESCRIPTIONS[10])


# ─── БАЗА ДАННЫХ ──────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        username TEXT DEFAULT '',
        balance INTEGER DEFAULT 100000,
        level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0,
        reputation INTEGER DEFAULT 50,
        garage_size INTEGER DEFAULT 1,
        best_deal INTEGER DEFAULT 0,
        total_deals INTEGER DEFAULT 0,
        total_earned INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        last_bonus REAL DEFAULT 0,
        rare_part_buff REAL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS player_cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        brand TEXT,
        model TEXT,
        year INTEGER,
        car_type TEXT,
        base_price INTEGER,
        market_price INTEGER,
        buy_price INTEGER,
        mileage INTEGER,
        problems TEXT,
        photo_url TEXT,
        level_key INTEGER,
        bought_at REAL,
        sell_price INTEGER DEFAULT 0,
        sell_cooldown REAL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS car_photos (
        model_key TEXT PRIMARY KEY,
        photo_url TEXT,
        cached_at REAL
    );

    CREATE TABLE IF NOT EXISTS market_prices (
        model_key TEXT PRIMARY KEY,
        current_price INTEGER,
        updated_at REAL
    );

    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        model_key TEXT,
        multiplier REAL DEFAULT 1.0,
        active_until REAL,
        created_at REAL
    );
    """)
    conn.commit()
    conn.close()

# ─── ПОЛУЧЕНИЕ ФОТО ТРАНСПОРТА (ИСПРАВЛЕНО) ───────────

def wm_query_to_filename(wm_query):
    """Преобразует wm_query в имя файла для локальной картинки."""
    safe = wm_query.lower().replace(" ", "_").replace("-", "_")
    # Убираем проблемные символы
    safe = re.sub(r'[^a-z0-9_]', '', safe)
    return f"{safe}.png"

def get_local_car_photo(wm_query):
    """Возвращает путь к локальному PNG-файлу или None."""
    filename = wm_query_to_filename(wm_query)
    filepath = IMAGES_DIR / filename
    if filepath.exists():
        return str(filepath)
    return None

def get_car_photo(query_key):
    """Получить фото транспорта. Сначала Wikimedia, потом локальный файл."""
    conn = get_db()
    c = conn.cursor()
    # Проверка кэша
    c.execute("SELECT photo_url FROM car_photos WHERE model_key=? AND cached_at > ?",
              (query_key, time.time() - 30 * 86400))
    row = c.fetchone()
    if row and row["photo_url"]:
        conn.close()
        return row["photo_url"]
    conn.close()

    # Пробуем Wikimedia
    photo_url = None
    try:
        photo_url = search_wikimedia_photo(query_key)
    except Exception:
        photo_url = None

    # Сохранение в кэш
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO car_photos (model_key, photo_url, cached_at) VALUES (?, ?, ?)",
              (query_key, photo_url, time.time()))
    conn.commit()
    conn.close()
    return photo_url

def send_car_photo(user_id, wm_query, caption, kb):
    """Отправляет фото транспорта: сначала URL, потом локальный файл, потом заглушку."""
    photo_url = get_car_photo(wm_query)
    if photo_url:
        try:
            bot.send_photo(user_id, photo_url, caption=caption, reply_markup=kb)
            return
        except Exception:
            pass
    # Локальный файл
    local_path = get_local_car_photo(wm_query)
    if local_path:
        try:
            with open(local_path, "rb") as f:
                bot.send_photo(user_id, f, caption=caption, reply_markup=kb)
            return
        except Exception:
            pass
    # Заглушка
    bot.send_message(user_id, "🖼 [Фото недоступно]\n\n" + caption, reply_markup=kb)

def send_garage_car_photo(user_id, photo_url, wm_query, caption, kb):
    """Отправляет фото машины из гаража: сначала URL, потом локальный файл, потом заглушка."""
    if photo_url:
        try:
            bot.send_photo(user_id, photo_url, caption=caption, reply_markup=kb)
            return
        except Exception:
            pass
    # Локальный файл
    if wm_query:
        local_path = get_local_car_photo(wm_query)
        if local_path:
            try:
                with open(local_path, "rb") as f:
                    bot.send_photo(user_id, f, caption=caption, reply_markup=kb)
                return
            except Exception:
                pass
    # Заглушка
    bot.send_message(user_id, "🖼 [Фото недоступно]\n\n" + caption, reply_markup=kb)

# ─── WIKIMEDIA API (оставлено для совместимости) ─────

EXCLUDE_KEYWORDS = [
    "tuned", "tuning", "custom", "modified", "race", "racing", "rally",
    "drift", "concept", "prototype", "drawing", "render", "art", "toy",
    "model car", "miniature", "detail", "interior", "dashboard", "engine bay",
    "wheel", "headlight", "taillight", "badge", "logo", "emblem"
]

PREFER_KEYWORDS = [
    "front", "side", "view", "sedan", "hatchback", "wagon", "coupe",
    "suv", "roadster", "exterior"
]

def wikimedia_search(query, limit=15):
    try:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": 6,
            "srlimit": limit,
            "format": "json",
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        results = []
        for item in data.get("query", {}).get("search", []):
            title = item.get("title", "")
            if title.startswith("File:"):
                results.append(title[5:])
        return results
    except Exception:
        return []

def get_file_info(filename):
    try:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": f"File:{filename}",
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "iiurlwidth": 1280,
            "format": "json",
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            ii = page.get("imageinfo", [])
            if ii:
                info = ii[0]
                return {
                    "url": info.get("thumburl", "") or info.get("url", ""),
                    "width": info.get("width", 0),
                    "height": info.get("height", 0),
                    "mime": info.get("mime", ""),
                }
        return None
    except Exception:
        return None

def filter_filename(filename):
    fl = filename.lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in fl:
            return False
    if fl.endswith(".svg") or fl.endswith(".gif") or fl.endswith(".tif"):
        return False
    return True

def prefer_score(filename):
    fl = filename.lower()
    score = 0
    for kw in PREFER_KEYWORDS:
        if kw in fl:
            score += 2
    if fl.endswith(".jpg") or fl.endswith(".jpeg"):
        score += 1
    return score

def check_size(info):
    if not info:
        return False
    w = info.get("width", 0)
    h = info.get("height", 0)
    if w < 800 or h < 500:
        return False
    ratio = w / max(h, 1)
    if ratio < 1.0 or ratio > 3.0:
        return False
    return True

def search_wikimedia_photo(query):
    files = wikimedia_search(query, limit=15)
    if not files:
        parts = query.rsplit(" ", 1)
        if len(parts) > 1:
            files = wikimedia_search(parts[0], limit=15)
    if not files:
        return None
    filtered = [f for f in files if filter_filename(f)]
    if not filtered:
        filtered = files
    filtered.sort(key=prefer_score, reverse=True)
    for fname in filtered[:8]:
        info = get_file_info(fname)
        if check_size(info):
            return info["url"]
    for fname in filtered:
        info = get_file_info(fname)
        if info and info.get("url"):
            return info["url"]
    return None

# ─── РЫНОЧНЫЕ ЦЕНЫ ────────────────────────────────────

def get_all_car_defs():
    result = []
    for lvl in ALL_LEVELS:
        for car in CARS[lvl]:
            entry = dict(car)
            entry["level_key"] = lvl
            result.append(entry)
    return result

def get_market_price(level_key, brand, model):
    model_key = f"{brand} {model}"
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT current_price FROM market_prices WHERE model_key=?", (model_key,))
    row = c.fetchone()
    now = time.time()
    if row:
        base = row["current_price"]
    else:
        car_def = None
        for cd in get_all_car_defs():
            if cd["brand"] == brand and cd["model"] == model:
                car_def = cd
                break
        base = car_def["base_price"] if car_def else 100000
        c.execute("INSERT OR REPLACE INTO market_prices (model_key, current_price, updated_at) VALUES (?, ?, ?)",
                  (model_key, base, now))
        conn.commit()

    c.execute("SELECT multiplier FROM events WHERE model_key=? AND active_until > ? AND type='hype'",
              (model_key, now))
    ev = c.fetchone()
    if ev:
        base = int(base * ev["multiplier"])

    c.execute("SELECT multiplier FROM events WHERE model_key='' AND active_until > ? AND type='crisis'",
              (now,))
    ev2 = c.fetchone()
    if ev2:
        base = int(base * ev2["multiplier"])

    conn.close()
    return base

def update_all_market_prices():
    conn = get_db()
    c = conn.cursor()
    now = time.time()
    for car in get_all_car_defs():
        model_key = f"{car['brand']} {car['model']}"
        c.execute("SELECT current_price FROM market_prices WHERE model_key=?", (model_key,))
        row = c.fetchone()
        if row:
            old = row["current_price"]
        else:
            old = car["base_price"]
        change = random.uniform(-0.30, 0.30)
        new_price = max(int(old * (1 + change)), int(car["base_price"] * 0.3))
        c.execute("INSERT OR REPLACE INTO market_prices (model_key, current_price, updated_at) VALUES (?, ?, ?)",
                  (model_key, new_price, now))
    conn.commit()
    conn.close()

# ─── ПРОБЛЕМЫ ТРАНСПОРТА ──────────────────────────────

PROBLEMS = [
    {"name": "Стук в двигателе", "mult": 0.25},
    {"name": "Троит цилиндр", "mult": 0.15},
    {"name": "Мёртвый аккумулятор", "mult": 0.05},
    {"name": "Течёт масло", "mult": 0.10},
    {"name": "Износ тормозных колодок", "mult": 0.08},
    {"name": "Гнилой порог", "mult": 0.12},
    {"name": "Разбитая подвеска", "mult": 0.18},
    {"name": "Пробит глушитель", "mult": 0.07},
    {"name": "Проблемы с электрикой", "mult": 0.14},
    {"name": "Изношенная резина", "mult": 0.06},
    {"name": "Стучит рулевая рейка", "mult": 0.13},
    {"name": "Дымит выхлоп", "mult": 0.10},
    {"name": "Сбит сход-развал", "mult": 0.05},
    {"name": "Сцепление буксует", "mult": 0.15},
    {"name": "Ржавчина на крыльях", "mult": 0.08},
]

def generate_problems():
    n = random.randint(1, 4)
    return random.sample(PROBLEMS, min(n, len(PROBLEMS)))

def problems_to_json(problems):
    return json.dumps([{"name": p["name"], "mult": p["mult"]} for p in problems])

def problems_from_json(json_str):
    if not json_str:
        return []
    try:
        return json.loads(json_str)
    except Exception:
        return []

def repair_cost(problem, base_price):
    return int(base_price * problem["mult"] * 0.4)

# ─── ИГРОВЫЕ ФУНКЦИИ ──────────────────────────────────

def get_player(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def create_player(user_id, username=""):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO players (user_id, username, balance, level, exp, reputation, garage_size, last_bonus) VALUES (?, ?, 100000, 1, 0, 50, 1, 0)",
              (user_id, username))
    conn.commit()
    conn.close()
    return get_player(user_id)

def update_player(user_id, **kwargs):
    conn = get_db()
    c = conn.cursor()
    sets = ", ".join([f"{k}=?" for k in kwargs])
    vals = list(kwargs.values()) + [user_id]
    c.execute(f"UPDATE players SET {sets} WHERE user_id=?", vals)
    conn.commit()
    conn.close()

def get_player_cars(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM player_cars WHERE user_id=? ORDER BY bought_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_player_car(car_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM player_cars WHERE id=?", (car_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def count_player_cars(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM player_cars WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row["cnt"] if row else 0

def exp_for_level(level):
    return level * 5000

def check_level_up(user_id):
    player = get_player(user_id)
    if not player:
        return False
    level = player["level"]
    exp = player["exp"]
    leveled = False
    while exp >= exp_for_level(level):
        exp -= exp_for_level(level)
        level += 1
        leveled = True
    if leveled:
        new_garage = min(level, 10)
        update_player(user_id, level=level, exp=exp, garage_size=new_garage)
        return True
    return False

def add_exp(user_id, amount):
    player = get_player(user_id)
    if not player:
        return
    update_player(user_id, exp=player["exp"] + amount)
    return check_level_up(user_id)

def calc_capital(user_id):
    player = get_player(user_id)
    if not player:
        return 0
    capital = player["balance"]
    cars = get_player_cars(user_id)
    for car in cars:
        capital += car["market_price"]
    return capital

def format_money(amount):
    return f"{amount:,}".replace(",", " ") + " ₽"

def car_full_name(car):
    return f"{car['brand']} {car['model']}"

def car_full_name_from_def(cd):
    return f"{cd['brand']} {cd['model']}"

# ─── ГЕНЕРАЦИЯ ОБЪЯВЛЕНИЙ ─────────────────────────────

SELLER_NAMES = [
    "Ахмет", "Серёга", "Дядя Гена", "Рустам", "Валера", "Эдик",
    "Михалыч", "Тагир", "Костян", "Андрюха", "Жека", "Рамиль",
    "Боря", "Стас", "Лёха", "Марат", "Витёк", "Юра", "Паша", "Гена",
]

def generate_listing(user_id):
    player = get_player(user_id)
    if not player:
        return None
    plevel = player["level"]

    available = []
    for l in ALL_LEVELS:
        car_level = l if l <= 10 else l // 11
        if car_level <= plevel:
            available.append(l)

    if not available:
        available = [1, 11]

    chosen_level = random.choice(available)
    car_def = random.choice(CARS[chosen_level])
    brand = car_def["brand"]
    model = car_def["model"]

    market_price = get_market_price(chosen_level, brand, model)
    year = car_def["year"]
    age = max(2024 - year, 1)
    mileage = random.randint(age * 5000, age * 25000)
    if mileage > 400000:
        mileage = random.randint(150000, 400000)

    condition_mult = 1.0 - (mileage / 500000) * 0.3
    problems = generate_problems()
    for p in problems:
        condition_mult -= p["mult"] * 0.3
    condition_mult = max(0.3, condition_mult)
    price = int(market_price * condition_mult * random.uniform(0.85, 1.1))
    price = max(price, 5000)

    seller = random.choice(SELLER_NAMES)

    return {
        "brand": brand,
        "model": model,
        "year": year,
        "mileage": mileage,
        "price": price,
        "market_price": market_price,
        "seller": seller,
        "problems": problems,
        "car_type": car_def["type"],
        "level_key": chosen_level,
        "wm_query": car_def["wm_query"],
        "base_price": car_def["base_price"],
    }

# ─── КЛАВИАТУРЫ ───────────────────────────────────────

def main_keyboard(user_id):
    player = get_player(user_id)
    is_admin = player and (player["is_admin"] or player["user_id"] == OWNER_ID)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton("🚗 Найти тачку"),
        types.KeyboardButton("🏠 Мой гараж"),
        types.KeyboardButton("💰 Баланс"),
        types.KeyboardButton("📊 Рынок"),
        types.KeyboardButton("🏆 Топ"),
        types.KeyboardButton("🎁 Бонус"),
        types.KeyboardButton("👤 Профиль"),
    )
    if is_admin:
        kb.add(
            types.KeyboardButton("👥 Игроки"),
            types.KeyboardButton("🚫 Чёрный список"),
            types.KeyboardButton("📢 Сообщение"),
        )
    return kb

def cancel_kb():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return kb

# ─── ПРОВЕРКА ДОСТУПА ─────────────────────────────────

def is_banned(user_id):
    player = get_player(user_id)
    if not player:
        return False
    return bool(player["is_banned"])

def is_admin(user_id):
    player = get_player(user_id)
    if not player:
        return False
    return bool(player["is_admin"]) or user_id == OWNER_ID

# ─── ХРАНЯЛИЩЕ СОСТОЯНИЙ ──────────────────────────────

user_listings = {}
user_state = {}

# ─── ОБРАБОТЧИКИ: СТАРТ И КОМАНДЫ ────────────────────

@bot.message_handler(commands=["start"])
def cmd_start(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or ""
    player = create_player(user_id, username)
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Вы заблокированы и не можете пользоваться ботом.")
        return
    name = message.from_user.first_name or "Игрок"
    text = (
        f"👋 Привет, {name}!\n\n"
        f"🏁 Добро пожаловать в «Перекуп Тачек»!\n\n"
        f"💰 Стартовый баланс: {format_money(100000)}\n"
        f"📦 Гараж: 1 место\n"
        f"⭐ Уровень: 1\n"
        f"🌟 Репутация: 50\n\n"
        f"Покупай тачки и мото дёшево — продавай дороже. "
        f"Зарабатывай опыт, прокачивай уровень, расширяй гараж!\n\n"
        f"Жми «🚗 Найти тачку», чтобы начать!"
    )
    bot.send_message(user_id, text, reply_markup=main_keyboard(user_id))

@bot.message_handler(commands=["help"])
def cmd_help(message):
    bot.send_message(message.chat.id,
        "📖 Помощь по «Перекуп Тачек»:\n\n"
        "🚗 Найти тачку — ищет 3-5 случайных объявлений\n"
        "🏠 Мой гараж — ваши тачки, ремонт, продажа\n"
        "💰 Баланс — деньги, уровень, репутация\n"
        "📊 Рынок — текущие цены на модели\n"
        "🏆 Топ — рейтинг по капиталу\n"
        "🎁 Бонус — +10 000 ₽ раз в 4 часа\n"
        "👤 Профиль — статистика игрока\n\n"
        "Команды админа: /admin /unadmin /admins /users /ban /unban /banlist")

# ─── АДМИН-КОМАНДЫ ────────────────────────────────────

@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(user_id, "Использование: /admin <код>")
        return
    code = args[1].strip()
    if code != ADMIN_CODE:
        bot.send_message(user_id, "❌ Неверный код.")
        return
    if user_id == OWNER_ID:
        bot.send_message(user_id, "👑 Вы уже владелец!")
        return
    player = get_player(user_id)
    if player and player["is_admin"]:
        bot.send_message(user_id, "✅ Вы уже админ.")
        return
    update_player(user_id, is_admin=1)
    bot.send_message(user_id, "✅ Вы стали админом!", reply_markup=main_keyboard(user_id))

@bot.message_handler(commands=["unadmin"])
def cmd_unadmin(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    if user_id == OWNER_ID:
        bot.send_message(user_id, "👑 Владелец не может снять себя.")
        return
    update_player(user_id, is_admin=0)
    bot.send_message(user_id, "✅ Вы сняли админку.", reply_markup=main_keyboard(user_id))

@bot.message_handler(commands=["admins"])
def cmd_admins(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT user_id, username FROM players WHERE is_admin=1 OR user_id=?", (OWNER_ID,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        bot.send_message(user_id, "Админов нет.")
        return
    text = "👥 Админы:\n\n"
    for r in rows:
        role = "👑 Владелец" if r["user_id"] == OWNER_ID else "🛡 Админ"
        text += f"{role} — {r['username'] or r['user_id']}\n"
    bot.send_message(user_id, text)

@bot.message_handler(commands=["users"])
def cmd_users(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM players")
    total = c.fetchone()["cnt"]
    c.execute("SELECT COUNT(*) as cnt FROM players WHERE is_banned=1")
    banned = c.fetchone()["cnt"]
    c.execute("SELECT user_id, username, balance, level FROM players ORDER BY balance DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    text = f"👥 Всего игроков: {total}\n🚫 Забанено: {banned}\n\nТоп-20 по балансу:\n\n"
    for i, r in enumerate(rows, 1):
        text += f"{i}. {r['username'] or r['user_id']} — {format_money(r['balance'])} (ур.{r['level']})\n"
    bot.send_message(user_id, text)

@bot.message_handler(commands=["ban"])
def cmd_ban(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(user_id, "Использование: /ban <user_id>")
        return
    try:
        target = int(args[1].strip())
    except ValueError:
        bot.send_message(user_id, "user_id должен быть числом.")
        return
    if target == OWNER_ID:
        bot.send_message(user_id, "👑 Владельца нельзя забанить.")
        return
    target_player = get_player(target)
    if not target_player:
        bot.send_message(user_id, "Игрок не найден.")
        return
    if target_player["is_admin"] and user_id != OWNER_ID:
        bot.send_message(user_id, "❌ Нельзя забанить админа (только владелец может).")
        return
    update_player(target, is_banned=1)
    bot.send_message(user_id, f"🚫 Игрок {target_player['username'] or target} забанен.")
    try:
        bot.send_message(target, "🚫 Вы заблокированы админом.")
    except Exception:
        pass

@bot.message_handler(commands=["unban"])
def cmd_unban(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(user_id, "Использование: /unban <user_id>")
        return
    try:
        target = int(args[1].strip())
    except ValueError:
        bot.send_message(user_id, "user_id должен быть числом.")
        return
    update_player(target, is_banned=0)
    bot.send_message(user_id, f"✅ Игрок {target} разбанен.")

@bot.message_handler(commands=["banlist"])
def cmd_banlist(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT user_id, username FROM players WHERE is_banned=1")
    rows = c.fetchall()
    conn.close()
    if not rows:
        bot.send_message(user_id, "Чёрный список пуст.")
        return
    text = "🚫 Чёрный список:\n\n"
    for r in rows:
        text += f"• {r['username'] or r['user_id']} (ID: {r['user_id']})\n"
    bot.send_message(user_id, text)

# ─── ОСНОВНОЕ МЕНЮ ───────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "🚗 Найти тачку")
def menu_find(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    player = get_player(user_id)
    if not player:
        create_player(user_id, message.from_user.username or "")
        player = get_player(user_id)

    current_cars = count_player_cars(user_id)
    if current_cars >= player["garage_size"]:
        bot.send_message(user_id,
            f"🏠 Гараж забит! У вас {current_cars} из {player['garage_size']} мест.\n"
            f"Продайте что-нибудь или прокачайте уровень.")
        return

    bot.send_message(user_id, "🔍 Ищем объявления на рынке…")
    n = random.randint(3, 5)
    listings = []
    for _ in range(n):
        lst = generate_listing(user_id)
        if lst:
            listings.append(lst)
    if not listings:
        bot.send_message(user_id, "🤷 Ничего не нашлось. Попробуйте позже.")
        return

    user_listings[user_id] = listings

    for i, lst in enumerate(listings):
        full_name = f"{lst['brand']} {lst['model']}"
        caption = (
            f"🚗 {full_name}\n"
            f"📅 Год: {lst['year']}\n"
            f"📏 Пробег: {lst['mileage']:,} км".replace(",", " ") + "\n"
            f"💰 Цена: {format_money(lst['price'])}\n"
            f"📊 Рыночная: {format_money(lst['market_price'])}\n"
            f"👤 Хозяин: {lst['seller']}\n"
            f"🏷 Тип: {lst['car_type']}\n"
            f"🔢 Уровень: {lst['level_key'] if lst['level_key'] <= 10 else 'Мото ' + str(lst['level_key'] // 11)}"
        )
        cb_prefix = f"lst_{i}"
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton(f"👀 Осмотреть (500 ₽)", callback_data=f"{cb_prefix}_inspect"),
            types.InlineKeyboardButton(f"👀👀 Диагностика (2000 ₽)", callback_data=f"{cb_prefix}_diag"),
            types.InlineKeyboardButton("💸 Купить", callback_data=f"{cb_prefix}_buy"),
            types.InlineKeyboardButton("🤝 Торговаться", callback_data=f"{cb_prefix}_trade"),
        )
        send_car_photo(user_id, lst["wm_query"], caption, kb)

# ─── INLINE ОБРАБОТЧИКИ ОБЪЯВЛЕНИЙ ───────────────────

@bot.callback_query_handler(func=lambda c: c.data.startswith("lst_"))
def cb_listing(call):
    user_id = call.from_user.id
    if is_banned(user_id):
        bot.answer_callback_query(call.id, "🚫 Вы забанены.")
        return
    parts = call.data.split("_")
    idx = int(parts[1])
    action = parts[2] if len(parts) > 2 else ""

    listings = user_listings.get(user_id, [])
    if idx >= len(listings):
        bot.answer_callback_query(call.id, "⏰ Объявление устарело.")
        return
    lst = listings[idx]
    player = get_player(user_id)
    if not player:
        return

    if action == "inspect":
        cost = 500
        if player["balance"] < cost:
            bot.answer_callback_query(call.id, "💸 Недостаточно денег для осмотра!")
            return
        update_player(user_id, balance=player["balance"] - cost)
        problems = lst["problems"]
        if problems:
            shown = random.choice(problems)
            text = (f"🔎 Осмотр: {lst['brand']} {lst['model']}\n\n"
                    f"⚠️ Найдена проблема:\n"
                    f"• {shown['name']} (влияет на цену ~{int(shown['mult']*100)}%)\n\n"
                    f"Возможно, есть и другие проблемы. "
                    f"Закажите полную диагностику за 2000 ₽, чтобы узнать всё.")
        else:
            text = f"🔎 Осмотр: {lst['brand']} {lst['model']}\n\n✅ Проблем не найдено! Чистая тачка."
        bot.answer_callback_query(call.id, "Осмотр проведён")
        bot.send_message(user_id, text)

    elif action == "diag":
        cost = 2000
        if player["balance"] < cost:
            bot.answer_callback_query(call.id, "💸 Недостаточно денег для диагностики!")
            return
        update_player(user_id, balance=player["balance"] - cost)
        problems = lst["problems"]
        if problems:
            text = f"🔬 Полная диагностика: {lst['brand']} {lst['model']}\n\n⚠️ Найденные проблемы:\n"
            total_mult = 0
            for p in problems:
                text += f"• {p['name']} (~{int(p['mult']*100)}%)\n"
                total_mult += p["mult"]
            text += f"\n📊 Общее снижение стоимости: ~{int(total_mult*100)}%\n"
            text += f"🔧 Рекомендация: {'покупка выгодна' if total_mult < 0.3 else 'лучше поторговаться'}"
        else:
            text = f"🔬 Полная диагностика: {lst['brand']} {lst['model']}\n\n✅ Тачка в идеальном состоянии! Проблем нет."
        bot.answer_callback_query(call.id, "Диагностика проведена")
        bot.send_message(user_id, text)

    elif action == "buy":
        current = count_player_cars(user_id)
        if current >= player["garage_size"]:
            bot.answer_callback_query(call.id, "🏠 Гараж забит!")
            return
        price = lst["price"]
        if player["balance"] < price:
            bot.answer_callback_query(call.id, "💸 Недостаточно денег!")
            return
        photo_url = get_car_photo(lst["wm_query"])
        conn = get_db()
        c = conn.cursor()
        problems_json = problems_to_json(lst["problems"])
        c.execute("""INSERT INTO player_cars
            (user_id, brand, model, year, car_type, base_price, market_price, buy_price,
             mileage, problems, photo_url, level_key, bought_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, lst["brand"], lst["model"], lst["year"], lst["car_type"],
             lst["base_price"], lst["market_price"], price,
             lst["mileage"], problems_json, photo_url, lst["level_key"], time.time()))
        conn.commit()
        conn.close()

        update_player(user_id, balance=player["balance"] - price,
                       total_deals=player["total_deals"] + 1)
        add_exp(user_id, int(price / 10000))

        bot.answer_callback_query(call.id, "✅ Куплено!")
        bot.send_message(user_id,
            f"✅ Вы купили {lst['brand']} {lst['model']} за {format_money(price)}!\n"
            f"🏠 Машина в гараже. Не забудьте отремонтировать перед продажей.")

    elif action == "trade":
        kb = types.InlineKeyboardMarkup(row_width=3)
        kb.add(
            types.InlineKeyboardButton("-5%", callback_data=f"lst_{idx}_trade_5"),
            types.InlineKeyboardButton("-10%", callback_data=f"lst_{idx}_trade_10"),
            types.InlineKeyboardButton("-20%", callback_data=f"lst_{idx}_trade_20"),
        )
        kb.add(types.InlineKeyboardButton("❌ Назад", callback_data=f"lst_{idx}_back"))
        bot.answer_callback_query(call.id)
        bot.send_message(user_id,
            f"🤝 Торговаться за {lst['brand']} {lst['model']}\n"
            f"Текущая цена: {format_money(lst['price'])}\n\n"
            f"Шансы хозяина согласиться:\n"
            f"• -5% → 90%\n• -10% → 60%\n• -20% → 30%", reply_markup=kb)

    elif action == "trade_5" or action == "trade_10" or action == "trade_20":
        pct = int(action.split("_")[1])
        chance = {5: 0.90, 10: 0.60, 20: 0.30}[pct]
        new_price = int(lst["price"] * (1 - pct / 100))
        if random.random() < chance:
            lst["price"] = new_price
            bot.answer_callback_query(call.id, f"✅ Согласен! -{pct}%")
            bot.send_message(user_id,
                f"🤝 {lst['seller']} согласился!\n"
                f"Новая цена: {format_money(new_price)} (−{pct}%)")
            full_name = f"{lst['brand']} {lst['model']}"
            new_caption = (
                f"🚗 {full_name}\n"
                f"📅 Год: {lst['year']}\n"
                f"📏 Пробег: {lst['mileage']:,} км".replace(",", " ") + "\n"
                f"💰 Цена: {format_money(new_price)} 🤝\n"
                f"📊 Рыночная: {format_money(lst['market_price'])}\n"
                f"👤 Хозяин: {lst['seller']}\n"
                f"🏷 Тип: {lst['car_type']}"
            )
            try:
                bot.edit_message_caption(user_id, call.message.message_id,
                    caption=new_caption, reply_markup=call.message.reply_markup)
            except Exception:
                pass
        else:
            bot.answer_callback_query(call.id, f"❌ Отказал! -{pct}%")
            bot.send_message(user_id,
                f"🤝 {lst['seller']} отказался торговаться на −{pct}%.\n"
                f"Цена осталась: {format_money(lst['price'])}")

    elif action == "back":
        bot.answer_callback_query(call.id)
        bot.delete_message(user_id, call.message.message_id)


# ─── ГАРАЖ ───────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "🏠 Мой гараж")
def menu_garage(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    player = get_player(user_id)
    if not player:
        bot.send_message(user_id, "Сначала /start")
        return
    cars = get_player_cars(user_id)
    if not cars:
        bot.send_message(user_id, "🏠 Ваш гараж пуст.\nЖмите «🚗 Найти тачку», чтобы найти машину!")
        return
    bot.send_message(user_id,
        f"🏠 Ваш гараж ({len(cars)}/{player['garage_size']} мест)\n")
    for car in cars:
        full_name = f"{car['brand']} {car['model']}"
        problems = problems_from_json(car["problems"])
        prob_text = ""
        if problems:
            prob_text = "\n⚠️ Проблемы:\n" + "\n".join(f"• {p['name']}" for p in problems)
        else:
            prob_text = "\n✅ Проблем нет"
        caption = (
            f"🚗 {full_name}\n"
            f"📅 Год: {car['year']}\n"
            f"📏 Пробег: {car['mileage']:,} км".replace(",", " ") + "\n"
            f"💰 Куплена за: {format_money(car['buy_price'])}\n"
            f"📊 Рыночная: {format_money(car['market_price'])}\n"
            f"🏷 Тип: {car['car_type']}\n"
            f"{prob_text}"
        )
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("🔧 Ремонт", callback_data=f"repair_{car['id']}"),
            types.InlineKeyboardButton("💸 Продать", callback_data=f"sell_{car['id']}"),
        )
        # ИСПРАВЛЕНО: ищем wm_query для локального файла
        wm_query = None
        for cd in get_all_car_defs():
            if cd["brand"] == car["brand"] and cd["model"] == car["model"]:
                wm_query = cd["wm_query"]
                break
        send_garage_car_photo(user_id, car["photo_url"], wm_query, caption, kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("repair_"))
def cb_repair(call):
    user_id = call.from_user.id
    if is_banned(user_id):
        return
    car_id = int(call.data.split("_")[1])
    car = get_player_car(car_id)
    if not car or car["user_id"] != user_id:
        bot.answer_callback_query(call.id, "Машина не найдена.")
        return
    problems = problems_from_json(car["problems"])
    if not problems:
        bot.answer_callback_query(call.id, "✅ Проблем нет, чинить нечего!")
        return
    kb = types.InlineKeyboardMarkup(row_width=1)
    for i, p in enumerate(problems):
        cost = repair_cost(p, car["base_price"])
        kb.add(types.InlineKeyboardButton(
            f"🔧 {p['name']} — {format_money(cost)}",
            callback_data=f"fix_{car_id}_{i}"))
    kb.add(types.InlineKeyboardButton("🔧 Ремонтировать всё",
        callback_data=f"fixall_{car_id}"))
    kb.add(types.InlineKeyboardButton("❌ Назад", callback_data="back_garage"))
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "🔧 Выберите проблему для ремонта:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("fix_") and not c.data.startswith("fixall_"))
def cb_fix(call):
    user_id = call.from_user.id
    parts = call.data.split("_")
    car_id = int(parts[1])
    prob_idx = int(parts[2])
    car = get_player_car(car_id)
    if not car or car["user_id"] != user_id:
        bot.answer_callback_query(call.id, "Машина не найдена.")
        return
    problems = problems_from_json(car["problems"])
    if prob_idx >= len(problems):
        bot.answer_callback_query(call.id, "Проблема не найдена.")
        return
    player = get_player(user_id)
    problem = problems[prob_idx]
    cost = repair_cost(problem, car["base_price"])
    if player["balance"] < cost:
        bot.answer_callback_query(call.id, "💸 Недостаточно денег!")
        return
    update_player(user_id, balance=player["balance"] - cost)
    problems.pop(prob_idx)
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE player_cars SET problems=? WHERE id=?",
              (problems_to_json(problems), car_id))
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, f"✅ {problem['name']} — отремонтировано!")
    bot.send_message(user_id,
        f"🔧 Отремонтировано: {problem['name']}\n"
        f"💰 Стоимость: {format_money(cost)}\n"
        f"📊 Осталось проблем: {len(problems)}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("fixall_"))
def cb_fixall(call):
    user_id = call.from_user.id
    car_id = int(call.data.split("_")[1])
    car = get_player_car(car_id)
    if not car or car["user_id"] != user_id:
        bot.answer_callback_query(call.id, "Машина не найдена.")
        return
    problems = problems_from_json(car["problems"])
    if not problems:
        bot.answer_callback_query(call.id, "✅ Проблем нет!")
        return
    player = get_player(user_id)
    total_cost = sum(repair_cost(p, car["base_price"]) for p in problems)
    total_cost = int(total_cost * 0.85)
    if player["balance"] < total_cost:
        bot.answer_callback_query(call.id, "💸 Недостаточно денег!")
        return
    update_player(user_id, balance=player["balance"] - total_cost)
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE player_cars SET problems='[]' WHERE id=?", (car_id,))
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, "✅ Всё отремонтировано! (−15%)")
    bot.send_message(user_id,
        f"🔧 Полный ремонт завершён!\n"
        f"💰 Стоимость: {format_money(total_cost)} (скидка 15%)\n"
        f"✅ Машина в идеальном состоянии!")

@bot.callback_query_handler(func=lambda c: c.data == "back_garage")
def cb_back_garage(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)
    bot.delete_message(user_id, call.message.message_id)

# ─── ПРОДАЖА ─────────────────────────────────────────

@bot.callback_query_handler(func=lambda c: c.data.startswith("sell_"))
def cb_sell(call):
    user_id = call.from_user.id
    if is_banned(user_id):
        return
    car_id = int(call.data.split("_")[1])
    car = get_player_car(car_id)
    if not car or car["user_id"] != user_id:
        bot.answer_callback_query(call.id, "Машина не найдена.")
        return
    now = time.time()
    if now < car.get("sell_cooldown", 0):
        remaining = int(car["sell_cooldown"] - now)
        bot.answer_callback_query(call.id, f"⏳ Подождите {remaining // 60} мин.")
        return
    full_name = f"{car['brand']} {car['model']}"
    problems = problems_from_json(car["problems"])
    prob_mult = sum(p["mult"] for p in problems) if problems else 0
    fair_price = int(car["market_price"] * (1 - prob_mult * 0.5))
    user_state[user_id] = {"action": "sell_price", "car_id": car_id, "fair_price": fair_price}
    bot.answer_callback_query(call.id)
    bot.send_message(user_id,
        f"💸 Продажа: {full_name}\n"
        f"📊 Рыночная цена: {format_money(car['market_price'])}\n"
        f"💡 Справедливая цена: {format_money(fair_price)}\n"
        f"✅ Если ≤ рыночной +10% — покупатель найдётся быстро.\n\n"
        f"Введите цену продажи (число):", reply_markup=cancel_kb())

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id, {}).get("action") == "sell_price")
def msg_sell_price(message):
    user_id = message.from_user.id
    state = user_state.get(user_id, {})
    if state.get("action") != "sell_price":
        return
    car_id = state["car_id"]
    car = get_player_car(car_id)
    if not car or car["user_id"] != user_id:
        user_state.pop(user_id, None)
        bot.send_message(user_id, "Машина не найдена.")
        return
    try:
        sell_price = int(message.text.replace(" ", "").replace("₽", ""))
    except ValueError:
        bot.send_message(user_id, "Введите число!")
        return
    if sell_price <= 0:
        bot.send_message(user_id, "Цена должна быть больше 0!")
        return

    fair_price = state["fair_price"]
    market_price = car["market_price"]
    player = get_player(user_id)
    full_name = f"{car['brand']} {car['model']}"

    max_acceptable = int(market_price * 1.1)
    if sell_price <= max_acceptable:
        conn = get_db()
        c = conn.cursor()
        sell_cd = time.time() + 300
        c.execute("UPDATE player_cars SET sell_price=?, sell_cooldown=? WHERE id=?",
                  (sell_price, sell_cd, car_id))
        conn.commit()
        conn.close()

        user_state.pop(user_id, None)
        bot.send_message(user_id,
            f"✅ {full_name} выставлена на продажу за {format_money(sell_price)}!\n"
            f"⏳ Покупатель найдётся через 5 минут. Приходите позже!")
        threading.Thread(target=sell_timer, args=(user_id, car_id, sell_price, fair_price), daemon=True).start()
    else:
        user_state.pop(user_id, None)
        bot.send_message(user_id,
            f"❌ Слишком дорого! Покупатель не готов платить {format_money(sell_price)}.\n"
            f"Максимум для быстрой продажи: {format_money(max_acceptable)}.\n"
            f"Попробуйте снова через «🏠 Мой гараж».")

def sell_timer(user_id, car_id, sell_price, fair_price):
    time.sleep(300)
    car = get_player_car(car_id)
    if not car or car["user_id"] != user_id:
        return
    if car.get("sell_price", 0) != sell_price:
        return
    full_name = f"{car['brand']} {car['model']}"
    player = get_player(user_id)

    bonus_mult = 1.0
    if player.get("rare_part_buff", 0) > time.time():
        bonus_mult = 1.10

    final_price = int(sell_price * bonus_mult)
    profit = final_price - car["buy_price"]

    if sell_price <= fair_price:
        rep_change = 2
    elif sell_price <= int(fair_price * 1.1):
        rep_change = 0
    else:
        rep_change = -3

    new_rep = max(0, min(100, player["reputation"] + rep_change))
    new_earned = player["total_earned"] + max(0, profit)
    new_best = max(player["best_deal"], profit) if profit > 0 else player["best_deal"]

    update_player(user_id, balance=player["balance"] + final_price,
                  reputation=new_rep, total_earned=new_earned,
                  best_deal=new_best, total_deals=player["total_deals"] + 1,
                  rare_part_buff=0)
    add_exp(user_id, int(final_price / 10000))

    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM player_cars WHERE id=?", (car_id,))
    conn.commit()
    conn.close()

    try:
        bot.send_message(user_id,
            f"💰 {full_name} продана за {format_money(final_price)}!\n"
            f"📈 Прибыль: {format_money(profit)}\n"
            f"🌟 Репутация: {'+' if rep_change > 0 else ''}{rep_change}\n"
            f"💰 Баланс: {format_money(player['balance'] + final_price)}")
    except Exception:
        pass

# ─── БАЛАНС ──────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "💰 Баланс")
def menu_balance(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    player = get_player(user_id)
    if not player:
        bot.send_message(user_id, "Сначала /start")
        return
    cars = get_player_cars(user_id)
    garage_value = sum(c["market_price"] for c in cars)
    capital = player["balance"] + garage_value
    text = (
        f"💰 Баланс: {format_money(player['balance'])}\n"
        f"🏠 Гараж: {format_money(garage_value)} ({len(cars)} тачек)\n"
        f"💎 Капитал: {format_money(capital)}\n\n"
        f"⭐ Уровень: {player['level']}\n"
        f"🎯 Опыт: {player['exp']} / {exp_for_level(player['level'])}\n"
        f"🌟 Репутация: {player['reputation']}/100\n"
        f"🏠 Размер гаража: {player['garage_size']} мест\n"
    )
    bot.send_message(user_id, text, reply_markup=main_keyboard(user_id))

# ─── РЫНОК ──────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "📊 Рынок")
def menu_market(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    player = get_player(user_id)
    if not player:
        bot.send_message(user_id, "Сначала /start")
        return
    plevel = player["level"]
    available = []
    for l in ALL_LEVELS:
        car_level = l if l <= 10 else l // 11
        if car_level <= plevel:
            available.append(l)

    text = "📊 Рынок тачек и мото:\n\n"
    for lvl in available:
        name = LEVEL_NAMES.get(lvl, f"Уровень {lvl}")
        text += f"━━━ {name} ━━━\n"
        for car in CARS[lvl]:
            model_key = f"{car['brand']} {car['model']}"
            price = get_market_price(lvl, car["brand"], car["model"])
            emoji = "🚗" if car["type"] == "Авто" else "🏍"
            text += f"{emoji} {model_key} — {format_money(price)}\n"
        text += "\n"
    bot.send_message(user_id, text)

# ─── ТОП ────────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "🏆 Топ")
def menu_top(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT user_id, username, balance, level FROM players WHERE is_banned=0 ORDER BY balance DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    if not rows:
        bot.send_message(user_id, "Пока нет игроков.")
        return
    entries = []
    for r in rows:
        cap = r["balance"]
        c2 = get_db()
        cc = c2.cursor()
        cc.execute("SELECT SUM(market_price) as total FROM player_cars WHERE user_id=?", (r["user_id"],))
        gar = cc.fetchone()
        if gar and gar["total"]:
            cap += gar["total"]
        c2.close()
        entries.append((r["user_id"], r["username"] or str(r["user_id"]), cap, r["level"]))

    entries.sort(key=lambda x: x[2], reverse=True)
    text = "🏆 Топ игроков по капиталу:\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, uname, cap, lvl) in enumerate(entries):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} {uname} — {format_money(cap)} (ур.{lvl})\n"
    bot.send_message(user_id, text)

# ─── БОНУС ──────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "🎁 Бонус")
def menu_bonus(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    player = get_player(user_id)
    if not player:
        bot.send_message(user_id, "Сначала /start")
        return
    now = time.time()
    cooldown = 4 * 3600
    if player["last_bonus"] + cooldown > now:
        remaining = int(player["last_bonus"] + cooldown - now)
        h = remaining // 3600
        m = (remaining % 3600) // 60
        bot.send_message(user_id, f"⏳ Бонус будет доступен через {h}ч {m}мин.")
        return
    bonus = 10000
    update_player(user_id, balance=player["balance"] + bonus, last_bonus=now)
    bot.send_message(user_id, f"🎁 Вы получили {format_money(bonus)}!\n💰 Баланс: {format_money(player['balance'] + bonus)}")

# ─── ГЕНЕРАЦИЯ КАРТИНКИ ГАРАЖА (ИСПРАВЛЕНО) ──────────

GARAGE_COLORS = {
    1:  (60, 60, 60), 2:  (70, 70, 72), 3:  (50, 60, 80), 4:  (40, 50, 90),
    5:  (50, 40, 100), 6:  (70, 40, 90), 7:  (90, 40, 80), 8:  (100, 50, 60),
    9:  (110, 70, 40), 10: (120, 90, 20),
}

GARAGE_TITLES = {
    1:  "Гараж-коробка", 2:  "Обычный гараж", 3:  "Тёплый паркинг",
    4:  "Бизнес-паркинг", 5:  "Премиум-паркинг", 6:  "Частный бокс",
    7:  "Автосалон-мини", 8:  "Шоурум", 9:  "Ангар", 10: "Элитная коллекция",
}

def _load_font(size, bold=True):
    """Загружает шрифт. Пробует несколько путей для Linux/Windows."""
    paths = []
    if bold:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
            "/usr/local/share/fonts/dejavu/DejaVuSans-Bold.ttf",
            "arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
    else:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
            "/usr/local/share/fonts/dejavu/DejaVuSans.ttf",
            "arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

def generate_garage_image(level, player):
    """Генерирует картинку-плашку гаража по уровню игрока."""
    width, height = 800, 200
    color = GARAGE_COLORS.get(level, GARAGE_COLORS[10])
    img = Image.new("RGB", (width, height), color)
    draw = ImageDraw.Draw(img)

    for y in range(height):
        shade = int(30 * (1 - y / height))
        r = min(255, color[0] + shade)
        g = min(255, color[1] + shade)
        b = min(255, color[2] + shade)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    title = GARAGE_TITLES.get(level, "Гараж")
    username = player.get("username", "") or f"ID:{player['user_id']}"
    info = f"Уровень {level} | Гараж {player['garage_size']} мест | Реп. {player['reputation']}"

    font_big = _load_font(36, bold=True)
    font_small = _load_font(18, bold=False)

    try:
        bbox = draw.textbbox((0, 0), title, font=font_big)
        tw = bbox[2] - bbox[0]
        draw.text(((width - tw) // 2, 30), title, fill=(255, 255, 255), font=font_big)
    except Exception:
        draw.text((100, 30), title, fill=(255, 255, 255), font=font_big)

    try:
        bbox2 = draw.textbbox((0, 0), info, font=font_small)
        tw2 = bbox2[2] - bbox2[0]
        draw.text(((width - tw2) // 2, 90), info, fill=(220, 220, 220), font=font_small)
    except Exception:
        draw.text((100, 90), info, fill=(220, 220, 220), font=font_small)

    stars = "⭐" * min(level, 10)
    try:
        bbox3 = draw.textbbox((0, 0), stars, font=font_small)
        tw3 = bbox3[2] - bbox3[0]
        draw.text(((width - tw3) // 2, 130), stars, fill="white", font=font_small)
    except Exception:
        draw.text((100, 130), stars, fill="white", font=font_small)

    # ИСПРАВЛЕНО: сохраняем во временную папку
    path = os.path.join(tempfile.gettempdir(), "garage_profile.png")
    img.save(path, "PNG")
    return path

# ─── ПРОФИЛЬ (с фото гаража по уровню) ───────────────

@bot.message_handler(func=lambda m: m.text == "👤 Профиль")
def menu_profile(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    player = get_player(user_id)
    if not player:
        bot.send_message(user_id, "Сначала /start")
        return
    cars = get_player_cars(user_id)
    garage_value = sum(c["market_price"] for c in cars)
    capital = player["balance"] + garage_value
    plevel = player["level"]
    garage_desc = get_garage_desc(plevel)
    name = message.from_user.first_name or "Игрок"
    role = "👑 Владелец" if user_id == OWNER_ID else ("🛡 Админ" if player["is_admin"] else "🎮 Игрок")

    text = (
        f"👤 {name}\n"
        f"🏷 {role}\n\n"
        f"⭐ Уровень: {plevel}\n"
        f"🎯 Опыт: {player['exp']} / {exp_for_level(plevel)}\n"
        f"🌟 Репутация: {player['reputation']}/100\n"
        f"💰 Капитал: {format_money(capital)}\n"
        f"💵 Деньги: {format_money(player['balance'])}\n"
        f"🏠 Гараж: {len(cars)}/{player['garage_size']} мест\n\n"
        f"━━━ Статистика ━━━\n"
        f"📊 Всего сделок: {player['total_deals']}\n"
        f"💵 Заработано всего: {format_money(player['total_earned'])}\n"
        f"🏆 Лучшая сделка: {format_money(player['best_deal'])}\n\n"
        f"🏠 Ваш гараж:\n{garage_desc}"
    )

    garage_img = generate_garage_image(plevel, player)

    try:
        with open(garage_img, "rb") as f:
            bot.send_photo(user_id, f, caption=text, reply_markup=main_keyboard(user_id))
    except Exception:
        bot.send_message(user_id, text, reply_markup=main_keyboard(user_id))

# ─── АДМИН: СОБЩЕНИЕ ВСЕМ ────────────────────────────

@bot.message_handler(func=lambda m: m.text == "📢 Сообщение")
def menu_broadcast(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    user_state[user_id] = {"action": "broadcast"}
    bot.send_message(user_id, "📢 Введите текст для рассылки всем игрокам:", reply_markup=cancel_kb())

@bot.message_handler(func=lambda m: m.text == "👥 Игроки")
def menu_players(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    cmd_users(message)

@bot.message_handler(func=lambda m: m.text == "🚫 Чёрный список")
def menu_banlist(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    cmd_banlist(message)

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id, {}).get("action") == "broadcast")
def msg_broadcast(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        user_state.pop(user_id, None)
        return
    text = message.text
    user_state.pop(user_id, None)
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT user_id FROM players WHERE is_banned=0")
    rows = c.fetchall()
    conn.close()
    sent = 0
    for r in rows:
        try:
            bot.send_message(r["user_id"], f"📢 {text}")
            sent += 1
        except Exception:
            pass
    bot.send_message(user_id, f"✅ Сообщение отправлено {sent} игрокам.", reply_markup=main_keyboard(user_id))

# ─── ОТМЕНА ─────────────────────────────────────────

@bot.callback_query_handler(func=lambda c: c.data == "cancel")
def cb_cancel(call):
    user_id = call.from_user.id
    user_state.pop(user_id, None)
    bot.answer_callback_query(call.id, "Отменено")
    bot.delete_message(user_id, call.message.message_id)
    bot.send_message(user_id, "❌ Действие отменено.", reply_markup=main_keyboard(user_id))

# ─── ФОНОВЫЕ ЗАДАЧИ ─────────────────────────────────

def hourly_event_loop():
    while True:
        time.sleep(3600)
        try:
            run_hourly_event()
        except Exception as e:
            print(f"Event error: {e}")

def run_hourly_event():
    event = random.choice(["gibdd", "crisis", "hype", "rare_part", "competitor"])
    now = time.time()
    duration = 3600

    conn = get_db()
    c = conn.cursor()

    if event == "gibdd":
        c.execute("SELECT user_id FROM players WHERE is_banned=0")
        rows = c.fetchall()
        conn.close()
        for r in rows:
            p = get_player(r["user_id"])
            if p and p["balance"] >= 5000:
                update_player(r["user_id"], balance=p["balance"] - 5000)
                try:
                    bot.send_message(r["user_id"], "🚨 ГИБДД оштрафовала вас на 5 000 ₽! Будьте внимательны на дороге.")
                except Exception:
                    pass

    elif event == "crisis":
        c.execute("INSERT INTO events (type, model_key, multiplier, active_until, created_at) VALUES (?, '', ?, ?, ?)",
                  ("crisis", 0.80, now + duration, now))
        conn.commit()
        conn.close()
        broadcast_text("📉 Кризис на авторынке! Все цены упали на 20% на следующий час.")

    elif event == "hype":
        all_defs = get_all_car_defs()
        chosen = random.choice(all_defs)
        model_key = f"{chosen['brand']} {chosen['model']}"
        c.execute("INSERT INTO events (type, model_key, multiplier, active_until, created_at) VALUES (?, ?, ?, ?, ?)",
                  ("hype", model_key, 2.0, now + duration, now))
        conn.commit()
        conn.close()
        broadcast_text(f"🔥 Хайп на {model_key}! Цена удвоена на следующий час!")

    elif event == "rare_part":
        c.execute("SELECT user_id FROM players WHERE is_banned=0")
        rows = c.fetchall()
        conn.close()
        for r in rows:
            update_player(r["user_id"], rare_part_buff=now + 7200)
            try:
                bot.send_message(r["user_id"], "💎 Вы нашли редкую запчасть! +10% к следующей продаже тачки!")
            except Exception:
                pass

    elif event == "competitor":
        all_defs = get_all_car_defs()
        chosen = random.choice(all_defs)
        model_key = f"{chosen['brand']} {chosen['model']}"
        c.execute("INSERT INTO events (type, model_key, multiplier, active_until, created_at) VALUES (?, ?, ?, ?, ?)",
                  ("hype", model_key, 0.5, now + duration, now))
        conn.commit()
        conn.close()
        broadcast_text(f"📉 Конкурент завалил рынок {model_key}! Цена упала вдвое на следующий час!")

def broadcast_text(text):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT user_id FROM players WHERE is_banned=0")
    rows = c.fetchall()
    conn.close()
    for r in rows:
        try:
            bot.send_message(r["user_id"], text)
        except Exception:
            pass

def market_update_loop():
    while True:
        time.sleep(3600)
        try:
            update_all_market_prices()
        except Exception as e:
            print(f"Market update error: {e}")

def expire_events_loop():
    while True:
        time.sleep(600)
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("DELETE FROM events WHERE active_until < ?", (time.time(),))
            conn.commit()
            conn.close()
        except Exception:
            pass

# ─── FLASK / WEBHOOK ───────────────────────────────

from flask import Flask, request, abort

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("Content-Type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "", 200
    abort(403)

# ─── ЗАПУСК ────────────────────────────────────────

def start_background():
    t1 = threading.Thread(target=hourly_event_loop, daemon=True)
    t2 = threading.Thread(target=market_update_loop, daemon=True)
    t3 = threading.Thread(target=expire_events_loop, daemon=True)
    t1.start()
    t2.start()
    t3.start()

def main():
    init_db()
    start_background()
    if WEBHOOK_URL:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=WEBHOOK_URL)
        print(f"Webhook set: {WEBHOOK_URL}")
        app.run(host="0.0.0.0", port=PORT)
    else:
        bot.remove_webhook()
        time.sleep(1)
        print("Polling mode started...")
        bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    main()
