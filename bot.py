import telebot
import requests
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔐 TOKENS (Railway env)
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# 📢 CHANNEL (SENING KANAL)
CHANNEL_USERNAME = "@Taiman_your_crash"
CHANNEL_LINK = "https://t.me/Taiman_your_crash"

# 🧠 MEMORY
user_memory = {}

# 🎯 LOADING STICKER
LOADING_STICKER = "CAACAgIAAxkBAAFIN3Np731vD7qE7U9ghxgsxOzSdmQYNQACm6kAAqFWgEsWApxtB7YTlDsE"

# 🤖 MODELS
MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "mistralai/mistral-7b-instruct"
]

# 📡 AI FUNCTION
def generate_ai(messages):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    for model in MODELS:
        data = {
            "model": model,
            "messages": messages
        }

        try:
            res = requests.post(url, headers=headers, json=data, timeout=30)

            if res.status_code != 200:
                continue

            result = res.json()
            return result["choices"][0]["message"]["content"]

        except:
            continue

    return "❌ AI javob bermadi."

# ✂️ CLEAN CODE FIX
def split_code(text):
    if "```" in text:
        parts = text.split("```")

        explanation = parts[0].strip()
        code = parts[1].strip()

        lines = code.split("\n")

        # remove language tag
        if lines and lines[0].lower() in [
            "python", "javascript", "js", "html", "css", "bash", "java"
        ]:
            lines = lines[1:]

        clean_code = "\n".join(lines)

        return explanation, clean_code

    return text.strip(), None

# 🔍 CHECK SUBSCRIPTION
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)

        return member.status in ["member", "administrator", "creator"]

    except:
        return False

# 🚫 NOT SUB MESSAGE
def not_subscribed_message(chat_id):
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=CHANNEL_LINK)
    )

    markup.add(
        InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
    )

    bot.send_message(
        chat_id,
        "❌ Botdan foydalanish uchun kanalga obuna bo‘ling!",
        reply_markup=markup
    )

# 👋 START
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Salom!\n\n"
        "🤖 AI Code Bot\n\n"
        "📌 Botdan foydalanish uchun kanalga obuna bo‘ling."
    )

# 📩 MAIN HANDLER
@bot.message_handler(func=lambda message: True)
def handle(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text

    # 🔥 CHECK SUB
    if not check_subscription(user_id):
        not_subscribed_message(chat_id)
        return

    # ⏳ STICKER LOADING
    bot.send_sticker(chat_id, LOADING_STICKER)

    history = user_memory.get(user_id, [])

    messages = [
        {
            "role": "system",
            "content": "You are a senior software engineer. Always explain first, then provide clean working code."
        }
    ]

    for msg in history[-6:]:
        messages.append(msg)

    messages.append({
        "role": "user",
        "content": text
    })

    response = generate_ai(messages)

    # memory save
    history.append({"role": "user", "content": text})
    history.append({"role": "assistant", "content": response})
    user_memory[user_id] = history

    explanation, code = split_code(response)

    bot.send_message(chat_id, f"📄 Sharh:\n{explanation}")

    if code:
        bot.send_message(chat_id, f"```\n{code}\n```", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "⚠️ Kod topilmadi.")

# 🔘 CALLBACK CHECK SUB
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check(call):
    user_id = call.from_user.id

    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "✅ Tasdiqlandi!")
        bot.send_message(call.message.chat.id, "🎉 Endi botdan foydalanishingiz mumkin!")
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna emassiz!")
        not_subscribed_message(call.message.chat.id)

# 🚀 RUN
print("🤖 Bot ishga tushdi...")
bot.infinity_polling()