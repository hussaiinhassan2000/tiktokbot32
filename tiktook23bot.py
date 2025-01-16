import requests
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# التوكن الخاص بالبوت
TOKEN = os.getenv("TOKEN")

# معرف القناة (استبدله بمعرف قناتك)
CHANNEL_USERNAME = "@hussaindev"

# دالة للتحقق من عضوية المستخدم في القناة
async def is_user_member(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

# دالة لبدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if await is_user_member(user_id, context):
        await update.message.reply_text('مرحبًا! أرسل لي رابط فيديو من TikTok وسأقوم بتحميله لك.')
    else:
        # إنشاء زرين: اشتراك أو متابعة دون اشتراك
        keyboard = [
            [InlineKeyboardButton("اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("متابعة دون اشتراك", callback_data="continue_without_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "مرحبًا! يمكنك الاشتراك في القناة أو متابعة استخدام البوت دون اشتراك.",
            reply_markup=reply_markup
        )

# دالة لمعالجة الضغط على الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "continue_without_sub":
        await query.edit_message_text("لقد اخترت متابعة استخدام البوت دون اشتراك. يمكنك الآن استخدام البوت.")

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

    # إضافة معالج للأزرار (Inline Keyboard)
    application.add_handler(CallbackQueryHandler(button_handler))

    # بدء تشغيل البوت
    application.run_polling()

if __name__ == '__main__':
    main()
