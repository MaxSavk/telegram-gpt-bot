from openai import OpenAI
from telethon.sync import TelegramClient
from telethon import events
from dotenv import load_dotenv
import os

load_dotenv()
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient("session", api_id, api_hash)

async def ask_gpt(message_text):
    try:
        response = client_ai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты очень грубый парень, который явно не рад сообщению"},
                {"role": "user", "content": message_text}
            ],
            temperature=0.8,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT ERROR]: {e}")
        return "Что-то пошло не так 😕"


async def main():
    await client.start()
    me = await client.get_me()

    print(f"Привет, {me.first_name}!")
    print(f"Username: @{me.username}")
    print(f"ID: {me.id}")
    print("\nТвои последние диалоги:")

    async for dialog in client.iter_dialogs(limit=10):
        print(f"- {dialog.name} (id: {dialog.id})")

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    try:
        sender = await event.get_sender()
        name = sender.first_name if sender else "Неизвестный"
    except Exception as e:
        name = "Неизвестный"
        print(f"[⚠️ Ошибка получения отправителя]: {e}")
    
    text = event.message.message
    print(f"\n✉️ Новое сообщение от {name}: {text}")
    
    reply = await ask_gpt(text)
    print(f"\n🤖 GPT-ответ: {reply}")
    await event.reply(reply)

with client:
    client.loop.run_until_complete(main())
    print("\nОжидаю новые сообщения... (Ctrl+C для выхода)")
    client.run_until_disconnected()
