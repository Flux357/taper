import telebot
from telebot import types
import sqlite3
import time
from datetime import datetime, timedelta

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8601248930:AAHU7-mIvmn8SrzZ9qWgMsTYgxyfoMQQt4Q"

bot = telebot.TeleBot(BOT_TOKEN)


# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            product_name TEXT,
            price TEXT,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    cur.execute("SELECT * FROM admins WHERE user_id=?", (8093996396,))
    if not cur.fetchone():
        cur.execute("INSERT INTO admins (user_id) VALUES (?)", (8093996396,))

    cur.execute("SELECT * FROM config WHERE key='requisites'")
    if not cur.fetchone():
        cur.execute("INSERT INTO config (key, value) VALUES (?, ?)",
                    ("requisites", "2202208885663253 (Сбербанк)"))

    conn.commit()
    conn.close()


def get_products():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name, description, price FROM products")
    products = cur.fetchall()
    conn.close()
    return products


def get_product_by_id(product_id):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name, description, price FROM products WHERE id=?", (product_id,))
    product = cur.fetchone()
    conn.close()
    return product


def add_product(name, description, price):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
                (name, description, price))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


def update_product(product_id, field, value):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE products SET {field}=? WHERE id=?", (value, product_id))
    conn.commit()
    conn.close()


def get_admins():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM admins")
    admins = [row[0] for row in cur.fetchall()]
    conn.close()
    return admins


def add_admin(user_id):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


def remove_admin(user_id):
    if user_id == 8093996396:
        return False
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    return True


def add_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) 
            VALUES (?, ?, ?, ?)
        """, (user_id, username, first_name, last_name))
        conn.commit()
    except:
        try:
            cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            conn.commit()
        except:
            pass
    conn.close()


def get_all_users():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = [row[0] for row in cur.fetchall()]
    conn.close()
    return users


def get_total_users():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()
    return count


def get_users_registered_today():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*) FROM users 
            WHERE DATE(registered_date) = DATE('now')
        """)
        count = cur.fetchone()[0]
    except:
        count = 0
    conn.close()
    return count


def add_purchase(user_id, product_id, product_name, price):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO purchases (user_id, product_id, product_name, price, status) 
        VALUES (?, ?, ?, ?, 'pending')
    """, (user_id, product_id, product_name, price))
    conn.commit()
    conn.close()


def get_total_purchases():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM purchases")
    count = cur.fetchone()[0]
    conn.close()
    return count


def get_purchases_today():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM purchases 
        WHERE DATE(purchase_date) = DATE('now')
    """)
    count = cur.fetchone()[0]
    conn.close()
    return count


def get_total_revenue():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("SELECT price FROM purchases")
    prices = cur.fetchall()
    conn.close()
    
    total = 0
    for price in prices:
        price_str = price[0]
        num = ''.join(filter(lambda x: x.isdigit() or x == '.', price_str))
        if num:
            total += float(num)
    return total


def get_revenue_today():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT price FROM purchases 
        WHERE DATE(purchase_date) = DATE('now')
    """)
    prices = cur.fetchall()
    conn.close()
    
    total = 0
    for price in prices:
        price_str = price[0]
        num = ''.join(filter(lambda x: x.isdigit() or x == '.', price_str))
        if num:
            total += float(num)
    return total


def get_popular_products():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT product_name, COUNT(*) as count 
        FROM purchases 
        GROUP BY product_name 
        ORDER BY count DESC 
        LIMIT 5
    """)
    products = cur.fetchall()
    conn.close()
    return products


def get_recent_purchases(limit=5):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, product_name, price, purchase_date 
        FROM purchases 
        ORDER BY purchase_date DESC 
        LIMIT ?
    """, (limit,))
    purchases = cur.fetchall()
    conn.close()
    return purchases


def get_requisites():
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("SELECT value FROM config WHERE key='requisites'")
    req = cur.fetchone()
    conn.close()
    return req[0] if req else "Реквизиты не заданы"


def set_requisites(new_value):
    conn = sqlite3.connect('shop.db')
    cur = conn.cursor()
    cur.execute("UPDATE config SET value=? WHERE key='requisites'", (new_value,))
    conn.commit()
    conn.close()


# ========== ХРАНИЛИЩА ==========
pending_payments = {}
admin_states = {}


# ========== ИНЛАЙН КЛАВИАТУРЫ ==========
def main_menu_keyboard(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🛍 Товары", callback_data="menu_products"),
        types.InlineKeyboardButton("ℹ️ О нас", callback_data="menu_about")
    )
    markup.add(
        types.InlineKeyboardButton("❓ Помощь", callback_data="menu_help")
    )
    
    if user_id in get_admins():
        markup.add(types.InlineKeyboardButton("🔧 Админ-панель", callback_data="menu_admin"))
    
    return markup


def products_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    products = get_products()
    for product in products:
        markup.add(types.InlineKeyboardButton(
            text=f"{product[1]} - {product[3]}",
            callback_data=f"product_{product[0]}"
        ))
    markup.add(types.InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu"))
    return markup


def product_detail_keyboard(product_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("💳 Показать реквизиты", callback_data=f"req_{product_id}"))
    markup.add(types.InlineKeyboardButton("✅ Я оплатил", callback_data=f"pay_{product_id}"))
    markup.add(types.InlineKeyboardButton("🔙 К списку товаров", callback_data="back_to_products"))
    return markup


def admin_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ Добавить товар", callback_data="admin_add_product"),
        types.InlineKeyboardButton("❌ Удалить товар", callback_data="admin_del_product"),
        types.InlineKeyboardButton("✏️ Изменить товар", callback_data="admin_edit_product")
    )
    markup.add(
        types.InlineKeyboardButton("👑 Добавить админа", callback_data="admin_add_admin"),
        types.InlineKeyboardButton("🗑 Удалить админа", callback_data="admin_remove_admin")
    )
    markup.add(
        types.InlineKeyboardButton("💰 Изменить реквизиты", callback_data="admin_change_req"),
        types.InlineKeyboardButton("📢 Рассылка", callback_data="admin_mailing")
    )
    markup.add(
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("📋 Последние покупки", callback_data="admin_recent_purchases")
    )
    markup.add(types.InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu"))
    return markup


def stats_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👥 Пользователи", callback_data="stats_users"),
        types.InlineKeyboardButton("💰 Выручка", callback_data="stats_revenue"),
        types.InlineKeyboardButton("📦 Продажи", callback_data="stats_sales"),
        types.InlineKeyboardButton("⭐ Популярное", callback_data="stats_popular"),
        types.InlineKeyboardButton("📋 Полный отчёт", callback_data="stats_full"),
        types.InlineKeyboardButton("🔙 Назад в админку", callback_data="back_to_admin")
    )
    return markup


def edit_product_choice_keyboard(product_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📝 Изменить название", callback_data=f"edit_name_{product_id}"),
        types.InlineKeyboardButton("📄 Изменить описание", callback_data=f"edit_desc_{product_id}"),
        types.InlineKeyboardButton("💰 Изменить цену", callback_data=f"edit_price_{product_id}"),
        types.InlineKeyboardButton("🔙 Назад к товарам", callback_data="admin_edit_product")
    )
    return markup


def products_list_for_edit_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    products = get_products()
    for product in products:
        markup.add(types.InlineKeyboardButton(
            f"📦 {product[1]} (ID: {product[0]})", 
            callback_data=f"edit_select_{product[0]}"
        ))
    markup.add(types.InlineKeyboardButton("🔙 Назад в админку", callback_data="back_to_admin"))
    return markup


# ========== ОБРАБОТЧИКИ КОМАНД ==========
@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    add_user(user_id, username, first_name, last_name)

    bot.send_message(
        message.chat.id,
        "Приветсвуем тебя в нашем DevBot, спасибо что зашел к нам. Здесь мы делаем сайты и боты в телеграм под заказ.",
        reply_markup=main_menu_keyboard(user_id)
    )


@bot.message_handler(commands=['admin'])
def cmd_admin(message):
    user_id = message.from_user.id
    if user_id not in get_admins():
        bot.send_message(message.chat.id, "⛔ У вас нет доступа к админ-панели.")
        return

    bot.send_message(message.chat.id, "🔧 Админ-панель", reply_markup=admin_keyboard())


@bot.message_handler(commands=['cancel'])
def cancel_action(message):
    user_id = message.from_user.id
    if user_id in admin_states:
        del admin_states[user_id]
        bot.send_message(message.chat.id, "❌ Действие отменено!", reply_markup=admin_keyboard())
    elif user_id in pending_payments:
        del pending_payments[user_id]
        bot.send_message(message.chat.id, "❌ Оплата отменена!", reply_markup=main_menu_keyboard(user_id))
    else:
        bot.send_message(message.chat.id, "❌ Нет активных действий для отмены.")


# ========== ИНЛАЙН ОБРАБОТЧИКИ ==========
@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_to_menu(call):
    user_id = call.from_user.id
    bot.edit_message_text(
        "Приветсвуем тебя в нашем DevBot, спасибо что зашел к нам. Здесь мы делаем сайты и боты в телеграм под заказ.",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=main_menu_keyboard(user_id)
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_admin")
def back_to_admin(call):
    bot.edit_message_text("🔧 Админ-панель", call.message.chat.id, call.message.message_id,
                         reply_markup=admin_keyboard())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "menu_products")
def menu_products(call):
    products = get_products()
    if not products:
        bot.edit_message_text("📭 Товаров пока нет.", call.message.chat.id, call.message.message_id)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=types.InlineKeyboardMarkup().add(
                                          types.InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")
                                      ))
    else:
        bot.edit_message_text("📦 Наши товары:", call.message.chat.id, call.message.message_id)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=products_keyboard())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "menu_about")
def menu_about(call):
    text = (
        "❓ *Почему мы?*\n\n"
        "✅ Делаем ботов и сайты за 1-3 дня (в зависимости от его сложности).\n"
        "✅ Более 150+ успешно запущенных проектов.\n"
        "✅ Работаем честно и прозрачно - без скрытых платежей\n"
        "✅ После сдачи проекта бесплатная поддержка 7 дней.\n\n"
        "🚀 Мы не просто делаем ботов и сайты - мы помогаем вам зарабатывать."
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=types.InlineKeyboardMarkup().add(
                                      types.InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")
                                  ))
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "menu_help")
def menu_help(call):
    text = "📞 По всем вопросам: @instalvl"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=types.InlineKeyboardMarkup().add(
                                      types.InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")
                                  ))
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "menu_admin")
def menu_admin(call):
    user_id = call.from_user.id
    if user_id not in get_admins():
        bot.answer_callback_query(call.id, "Нет доступа", show_alert=True)
        return
    
    bot.edit_message_text("🔧 Админ-панель", call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=admin_keyboard())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_products")
def back_to_products(call):
    products = get_products()
    if not products:
        bot.edit_message_text("📭 Товаров пока нет.", call.message.chat.id, call.message.message_id)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=types.InlineKeyboardMarkup().add(
                                          types.InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")
                                      ))
    else:
        bot.edit_message_text("📦 Наши товары:", call.message.chat.id, call.message.message_id)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=products_keyboard())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def view_product(call):
    product_id = int(call.data.split("_")[1])
    product = get_product_by_id(product_id)

    if not product:
        bot.answer_callback_query(call.id, "Товар не найден")
        return

    text = f"*{product[1]}*\n\n{product[2]}\n\n💰 Цена: {product[3]}"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=product_detail_keyboard(product_id))
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("req_"))
def show_requisites(call):
    req = get_requisites()
    bot.answer_callback_query(call.id, f"💳 Реквизиты для оплаты: {req}", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def payment_start(call):
    product_id = int(call.data.split("_")[1])
    product = get_product_by_id(product_id)

    if not product:
        bot.answer_callback_query(call.id, "Товар не найден")
        return

    pending_payments[call.from_user.id] = {
        'product_id': product[0],
        'product_name': product[1],
        'price': product[3]
    }

    bot.send_message(
        call.message.chat.id,
        "📸 Пожалуйста, отправьте *чек об оплате* (фото).\n\n"
        "После получения чека администратор проверит оплату и свяжется с вами.\n\n"
        "Если передумали, отправьте /cancel",
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id, "Ожидаем ваш чек")


# ========== ОБРАБОТКА ЧЕКОВ ==========
@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = message.from_user.id
    
    print(f"📸 Получено фото от пользователя {user_id}")  # Отладка

    if user_id not in pending_payments:
        bot.send_message(message.chat.id, "❓ Вы не начинали оплату. Сначала выберите товар и нажмите «Я оплатил».")
        return

    payment_info = pending_payments.pop(user_id)
    product_id = payment_info['product_id']
    product_name = payment_info['product_name']
    price = payment_info['price']
    
    # Сохраняем покупку
    add_purchase(user_id, product_id, product_name, price)
    
    # Получаем список админов
    admins = get_admins()
    file_id = message.photo[-1].file_id
    
    # Формируем информацию о пользователе
    user_mention = f"@{message.from_user.username}" if message.from_user.username else f"id{user_id}"
    user_fullname = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
    
    # Отправляем уведомление пользователю
    bot.send_message(
        message.chat.id,
        f"✅ *Спасибо за оплату!*\n\n"
        f"📦 Товар: {product_name}\n"
        f"💰 Сумма: {price}\n\n"
        f"Ваш чек отправлен администратору. Ожидайте подтверждения в ближайшее время.\n\n"
        f"По вопросам: @instalvl",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(user_id)
    )
    
    # Отправляем уведомление всем админам
    for admin_id in admins:
        try:
            caption = (
                f"🟢 *НОВАЯ ОПЛАТА!*\n\n"
                f"👤 Покупатель: {user_mention}\n"
                f"👤 Имя: {user_fullname}\n"
                f"📦 Товар: {product_name}\n"
                f"💰 Сумма: {price}\n"
                f"🆔 ID: {user_id}\n"
                f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"📎 *Чек ниже:*"
            )
            bot.send_photo(admin_id, file_id, caption=caption, parse_mode="Markdown")
            print(f"✅ Уведомление отправлено админу {admin_id}")  # Отладка
        except Exception as e:
            print(f"❌ Не удалось отправить админу {admin_id}: {e}")
    
    print(f"✅ Оплата от {user_id} обработана успешно")  # Отладка


# ========== СТАТИСТИКА ==========
@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def show_stats_menu(call):
    user_id = call.from_user.id
    if user_id not in get_admins():
        bot.answer_callback_query(call.id, "Нет доступа", show_alert=True)
        return
    
    bot.edit_message_text("📊 *Выберите тип статистики:*", call.message.chat.id, 
                         call.message.message_id, parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=stats_keyboard())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "stats_users")
def stats_users(call):
    total_users = get_total_users()
    users_today = get_users_registered_today()
    
    text = (
        "👥 *Статистика пользователей*\n\n"
        f"📊 Всего пользователей: *{total_users}*\n"
        f"🆕 Зарегистрировалось сегодня: *{users_today}*\n"
    )
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=stats_keyboard())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "stats_revenue")
def stats_revenue(call):
    total_revenue = get_total_revenue()
    revenue_today = get_revenue_today()
    
    text = (
        "💰 *Статистика выручки*\n\n"
        f"📈 Общая выручка: *{total_revenue:,.0f}₽*\n"
        f"📆 Выручка за сегодня: *{revenue_today:,.0f}₽*\n"
    )
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=stats_keyboard())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "stats_sales")
def stats_sales(call):
    total_purchases = get_total_purchases()
    purchases_today = get_purchases_today()
    
    text = (
        "📦 *Статистика продаж*\n\n"
        f"📊 Всего продаж: *{total_purchases}*\n"
        f"🆕 Продаж сегодня: *{purchases_today}*\n"
    )
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=stats_keyboard())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "stats_popular")
def stats_popular(call):
    popular = get_popular_products()
    
    if not popular:
        text = "⭐ *Популярные товары*\n\nПока нет продаж."
    else:
        text = "⭐ *Топ-5 популярных товаров*\n\n"
        for i, (name, count) in enumerate(popular, 1):
            text += f"{i}. {name} - *{count}* продаж\n"
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=stats_keyboard())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "stats_full")
def stats_full(call):
    total_users = get_total_users()
    users_today = get_users_registered_today()
    total_revenue = get_total_revenue()
    revenue_today = get_revenue_today()
    total_purchases = get_total_purchases()
    purchases_today = get_purchases_today()
    popular = get_popular_products()
    
    text = (
        "📊 *ПОЛНЫЙ ОТЧЁТ*\n\n"
        "👥 *Пользователи*\n"
        f"├ Всего: {total_users}\n"
        f"└ За сегодня: {users_today}\n\n"
        "💰 *Выручка*\n"
        f"├ Всего: {total_revenue:,.0f}₽\n"
        f"└ За сегодня: {revenue_today:,.0f}₽\n\n"
        "📦 *Продажи*\n"
        f"├ Всего: {total_purchases}\n"
        f"└ За сегодня: {purchases_today}\n\n"
        "⭐ *Популярные товары*\n"
    )
    
    if popular:
        for i, (name, count) in enumerate(popular, 1):
            text += f"{i}. {name} - {count} шт.\n"
    else:
        text += "Пока нет продаж"
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=stats_keyboard())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "admin_recent_purchases")
def show_recent_purchases(call):
    user_id = call.from_user.id
    if user_id not in get_admins():
        bot.answer_callback_query(call.id, "Нет доступа", show_alert=True)
        return
    
    purchases = get_recent_purchases(10)
    
    if not purchases:
        text = "📋 *Последние покупки*\n\nПока нет покупок."
    else:
        text = "📋 *Последние 10 покупок*\n\n"
        for purchase in purchases:
            user_id, product_name, price, date = purchase
            date_str = date[:16] if date else "неизвестно"
            text += f"👤 ID: {user_id}\n📦 {product_name} - {price}\n📅 {date_str}\n\n"
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, 
                                  reply_markup=types.InlineKeyboardMarkup().add(
                                      types.InlineKeyboardButton("🔙 Назад в админку", callback_data="back_to_admin")
                                  ))
    bot.answer_callback_query(call.id)


# ========== ИЗМЕНЕНИЕ ТОВАРА ==========
@bot.callback_query_handler(func=lambda call: call.data == "admin_edit_product")
def edit_product_choice(call):
    user_id = call.from_user.id
    if user_id not in get_admins():
        bot.answer_callback_query(call.id, "Нет доступа", show_alert=True)
        return
    
    products = get_products()
    if not products:
        bot.edit_message_text("📭 *Нет товаров для редактирования*\n\nДобавьте товары через 'Добавить товар'", 
                             call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                     reply_markup=types.InlineKeyboardMarkup().add(
                                         types.InlineKeyboardButton("🔙 Назад в админку", callback_data="back_to_admin")
                                     ))
        bot.answer_callback_query(call.id)
        return
    
    text = "✏️ *Выберите товар для редактирования:*"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=products_list_for_edit_keyboard())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_select_"))
def edit_select_product(call):
    product_id = int(call.data.split("_")[2])
    product = get_product_by_id(product_id)
    
    if not product:
        bot.answer_callback_query(call.id, "Товар не найден")
        return
    
    text = f"✏️ *Редактирование товара*\n\n"
    text += f"📦 ID: {product[0]}\n"
    text += f"📝 Название: `{product[1]}`\n"
    text += f"📄 Описание: `{product[2]}`\n"
    text += f"💰 Цена: `{product[3]}`\n\n"
    text += "Что хотите изменить?"
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, 
                                  reply_markup=edit_product_choice_keyboard(product_id))
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_name_"))
def edit_product_name(call):
    product_id = int(call.data.split("_")[2])
    admin_states[call.from_user.id] = {
        'action': 'edit_product',
        'product_id': product_id,
        'field': 'name'
    }
    bot.send_message(call.message.chat.id, 
                    "📝 Введите *новое название* товара:\n\nЧтобы отменить, отправьте /cancel",
                    parse_mode="Markdown")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_desc_"))
def edit_product_desc(call):
    product_id = int(call.data.split("_")[2])
    admin_states[call.from_user.id] = {
        'action': 'edit_product',
        'product_id': product_id,
        'field': 'description'
    }
    bot.send_message(call.message.chat.id, 
                    "📄 Введите *новое описание* товара:\n\nЧтобы отменить, отправьте /cancel",
                    parse_mode="Markdown")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_price_"))
def edit_product_price(call):
    product_id = int(call.data.split("_")[2])
    admin_states[call.from_user.id] = {
        'action': 'edit_product',
        'product_id': product_id,
        'field': 'price'
    }
    bot.send_message(call.message.chat.id, 
                    "💰 Введите *новую цену* товара (например: 1500₽):\n\nЧтобы отменить, отправьте /cancel",
                    parse_mode="Markdown")
    bot.answer_callback_query(call.id)


# ========== АДМИН ОБРАБОТЧИКИ ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_") and not call.data.startswith("admin_stats") and not call.data.startswith("admin_recent") and call.data not in ["admin_edit_product"])
def admin_callback(call):
    user_id = call.from_user.id
    if user_id not in get_admins():
        bot.answer_callback_query(call.id, "Нет доступа", show_alert=True)
        return

    action = call.data.replace("admin_", "")

    if action == "add_product":
        bot.send_message(call.message.chat.id, "Введите *название товара*:\n\nЧтобы отменить, отправьте /cancel", parse_mode="Markdown")
        admin_states[user_id] = {'action': 'add_product', 'step': 1}
        bot.answer_callback_query(call.id)

    elif action == "del_product":
        products = get_products()
        if not products:
            bot.send_message(call.message.chat.id, "Нет товаров для удаления.")
        else:
            text = "Введите ID товара для удаления:\n\n"
            for p in products:
                text += f"🔹 ID {p[0]}: {p[1]} - {p[3]}\n"
            text += "\nЧтобы отменить, отправьте /cancel"
            bot.send_message(call.message.chat.id, text)
            admin_states[user_id] = {'action': 'del_product', 'step': 1}
        bot.answer_callback_query(call.id)

    elif action == "add_admin":
        bot.send_message(call.message.chat.id, "Введите Telegram ID пользователя, которого хотите сделать админом:\n\nЧтобы отменить, отправьте /cancel")
        admin_states[user_id] = {'action': 'add_admin', 'step': 1}
        bot.answer_callback_query(call.id)

    elif action == "remove_admin":
        admins = get_admins()
        text = "Список админов (ID):\n\n"
        for a in admins:
            text += f"🔹 {a}\n"
        text += "\nВведите ID админа для удаления (себя удалить нельзя):\n\nЧтобы отменить, отправьте /cancel"
        bot.send_message(call.message.chat.id, text)
        admin_states[user_id] = {'action': 'remove_admin', 'step': 1}
        bot.answer_callback_query(call.id)

    elif action == "change_req":
        bot.send_message(
            call.message.chat.id,
            f"Текущие реквизиты:\n`{get_requisites()}`\n\nВведите новые реквизиты:\n\nЧтобы отменить, отправьте /cancel",
            parse_mode="Markdown"
        )
        admin_states[user_id] = {'action': 'change_req', 'step': 1}
        bot.answer_callback_query(call.id)

    elif action == "mailing":
        bot.send_message(call.message.chat.id, "Введите текст для рассылки:\n\nЧтобы отменить, отправьте /cancel")
        admin_states[user_id] = {'action': 'mailing', 'step': 1}
        bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: message.from_user.id in admin_states)
def handle_admin_input(message):
    user_id = message.from_user.id
    state = admin_states[user_id]
    action = state['action']

    if action == 'edit_product':
        product_id = state['product_id']
        field = state['field']
        new_value = message.text
        
        update_product(product_id, field, new_value)
        
        field_names = {
            'name': 'Название',
            'description': 'Описание',
            'price': 'Цену'
        }
        
        bot.send_message(message.chat.id, 
                        f"✅ {field_names[field]} товара успешно изменено!\n\nНовое значение: {new_value}",
                        reply_markup=admin_keyboard())
        del admin_states[user_id]
        return

    if action == 'add_product':
        if state['step'] == 1:
            admin_states[user_id]['name'] = message.text
            admin_states[user_id]['step'] = 2
            bot.send_message(message.chat.id, "Введите *описание товара*:\n\nЧтобы отменить, отправьте /cancel", parse_mode="Markdown")
        elif state['step'] == 2:
            admin_states[user_id]['desc'] = message.text
            admin_states[user_id]['step'] = 3
            bot.send_message(message.chat.id, "Введите *цену* (например: 1500₽):\n\nЧтобы отменить, отправьте /cancel", parse_mode="Markdown")
        elif state['step'] == 3:
            name = admin_states[user_id]['name']
            desc = admin_states[user_id]['desc']
            price = message.text
            add_product(name, desc, price)
            bot.send_message(message.chat.id, "✅ Товар добавлен!", reply_markup=admin_keyboard())
            del admin_states[user_id]

    elif action == 'del_product':
        try:
            product_id = int(message.text)
            delete_product(product_id)
            bot.send_message(message.chat.id, "✅ Товар удалён!", reply_markup=admin_keyboard())
        except:
            bot.send_message(message.chat.id, "❌ Ошибка: введите числовой ID", reply_markup=admin_keyboard())
        del admin_states[user_id]

    elif action == 'add_admin':
        try:
            new_admin_id = int(message.text)
            add_admin(new_admin_id)
            bot.send_message(message.chat.id, f"✅ Админ {new_admin_id} добавлен!", reply_markup=admin_keyboard())
        except:
            bot.send_message(message.chat.id, "❌ Ошибка: введите числовой ID", reply_markup=admin_keyboard())
        del admin_states[user_id]

    elif action == 'remove_admin':
        try:
            remove_id = int(message.text)
            if remove_id == 8093996396:
                bot.send_message(message.chat.id, "❌ Нельзя удалить главного администратора!", reply_markup=admin_keyboard())
            else:
                if remove_admin(remove_id):
                    bot.send_message(message.chat.id, f"✅ Админ {remove_id} удалён!", reply_markup=admin_keyboard())
                else:
                    bot.send_message(message.chat.id, "❌ Такого админа нет", reply_markup=admin_keyboard())
        except:
            bot.send_message(message.chat.id, "❌ Ошибка: введите числовой ID", reply_markup=admin_keyboard())
        del admin_states[user_id]

    elif action == 'change_req':
        set_requisites(message.text)
        bot.send_message(message.chat.id, f"✅ Реквизиты изменены:\n`{message.text}`", parse_mode="Markdown",
                         reply_markup=admin_keyboard())
        del admin_states[user_id]

    elif action == 'mailing':
        text = message.text
        bot.send_message(message.chat.id, "📢 Начинаю рассылку...")

        users = get_all_users()
        count = 0
        for uid in users:
            try:
                bot.send_message(uid, text, parse_mode="Markdown")
                count += 1
                time.sleep(0.05)
            except:
                pass

        bot.send_message(message.chat.id, f"✅ Рассылка завершена. Отправлено {count} пользователям.",
                         reply_markup=admin_keyboard())
        del admin_states[user_id]


# ========== ЗАПУСК БОТА ==========
if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("🤖 Бот DevBot успешно запущен!")
    print("=" * 50)
    print("\n📌 Доступные команды:")
    print("  /start - Главное меню")
    print("  /admin - Админ-панель")
    print("  /cancel - Отмена текущего действия")
    print("\n🔧 Функции админ-панели:")
    print("  ➕ Добавить товар")
    print("  ❌ Удалить товар")
    print("  ✏️ Изменить товар")
    print("  👑 Добавить админа")
    print("  🗑 Удалить админа")
    print("  💰 Изменить реквизиты")
    print("  📢 Рассылка")
    print("  📊 Статистика")
    print("  📋 Последние покупки")
    print("\n📸 При оплате:")
    print("  - Пользователь получает подтверждение")
    print("  - Администратор получает фото чека")
    print("\n" + "=" * 50)
    bot.infinity_polling()
