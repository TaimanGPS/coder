import telebot
import requests
import os

# 🔐 ENV TOKENLAR (Railway variables)
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# 🧠 USER MEMORY (RAM)
user_memory = {}

# 🔁 MODEL fallback
MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "mistralai/mistral-7b-instruct"
]

# 📡 AI so‘rov
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

        except Exception as e:
            print("ERROR:", e)
            continue

    return "❌ AI javob bermadi."

# ✂️ explanation + code ajratish
def split_code(text):
    if "```" in text:
        parts = text.split("```")
        explanation = parts[0]
        code = parts[1]
        return explanation.strip(), code.strip()
    return text.strip(), None

# 👋 START
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Salom!\n\n"
        "🤖 Men Code AI Botman\n\n"
        "💡 Buyruqlar:\n"
        "- python kod yoz\n"
        "- kodni tuzat\n"
        "- optimizatsiya qil\n\n"
        "🧠 Men oxirgi kodingni eslab qolaman!"
    )

# 📩 MAIN HANDLER
@bot.message_handler(func=lambda message: True)
def handle(message):
    user_id = message.from_user.id
    text = message.text

    bot.send_message(message.chat.id, "⏳ O‘ylayapman...")

    # 🧠 memory
    history = user_memory.get(user_id, [])

    if "shu kodni" in text.lower() and history:
        text = f"Oldingi kod:\n{history[-1]['content']}\n\n{text}"

    messages = [
        {
            "role": "system",
            "content": "You are a senior programmer. Explain first, then code in ``` ```."
        }
    ]

    # tarix
    for msg in history[-6:]:
        messages.append(msg)

    messages.append({
        "role": "user",
        "content": text
    })

    # AI response
    response = generate_ai(messages)

    # memory save
    history.append({"role": "user", "content": text})
    history.append({"role": "assistant", "content": response})
    user_memory[user_id] = history

    # split
    explanation, code = split_code(response)

    # send explanation
    bot.send_message(message.chat.id, f"📄 Sharh:\n{explanation}")

    # send code
    if code:
        bot.send_message(message.chat.id, f"```\n{code}\n```", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "⚠️ Kod topilmadi.")

# 🚀 RUN
print("🤖 Bot ishga tushdi...")
bot.infinity_polling()