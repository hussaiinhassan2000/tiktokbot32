import requests
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# التوكن الخاص بالبوت
TOKEN = os.getenv("TOKEN")

# دالة لبدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('مرحبًا! أرسل لي رابط فيديو من TikTok وسأقوم بتحميله لك.')

# دالة لتحميل الفيديو من TikTok باستخدام خدمة بديلة
def download_tiktok_video(url):
    api_url = f'https://www.tikwm.com/api/?url={url}'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'play' in data['data']:
            video_url = data['data']['play']
            return video_url
        elif 'data' in data and 'wmplay' in data['data']:
            video_url = data['data']['wmplay']
            return video_url
    return None

# دالة لمعالجة الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    if 'tiktok.com' in message:
        video_url = download_tiktok_video(message)
        if video_url:
            await update.message.reply_text(f'جارٍ تنزيل الفيديو من: {video_url}')
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video_url)
        else:
            await update.message.reply_text('فشل في تنزيل الفيديو. الرجاء المحاولة مرة أخرى.')
    else:
        await update.message.reply_text('الرجاء إرسال رابط فيديو صحيح من TikTok.')

def main() -> None:
    application = Application.builder().token(TOKEN).connect_timeout(60).read_timeout(60).build()

    # تعيين معالجات الأوامر والرسائل
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # بدء تشغيل البوت
    application.run_polling()

if __name__ == '__main__':
    main()
