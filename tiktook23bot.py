import requests
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# التوكن الخاص بالبوت
TOKEN = os.getenv("TOKEN")

# معرف القناة (استبدله بمعرف قناتك)
CHANNEL_USERNAME = "@hussaindev"

# معرف الأدمن (تم وضع معرفك هنا)
ADMIN_ID = 5087035940  # معرفك الجديد

# قائمة لتتبع المستخدمين الذين استخدموا البوت
unique_users = set()

# دالة الترحيب (عند دخول مستخدم جديد)
async def welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for member in update.message.new_chat_members:
        user_id = member.id
        username = member.username if member.username else "No username"
        name = member.first_name
        # إشعار الأدمن
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📢 مستخدم جديد دخل البوت:\n👤 الاسم: {name}\n🆔 يوزر: @{username}\n🔑 معرف: {user_id}"
        )
        # إرسال رسالة ترحيب للمستخدم
        await update.message.reply_text("بوت تحميل من تيك توك بدون علامه مائيه قناة @hussaindev")

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
    user = update.message.from_user
    user_id = user.id
    username = user.username if user.username else "No username"
    name = user.first_name

    # تحقق إذا كان المستخدم جديدًا وأضفه إلى قائمة المستخدمين
    if user_id not in unique_users:
        unique_users.add(user_id)
        # إشعار الأدمن بمستخدم جديد
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 مستخدم جديد بدأ استخدام البوت:\n👤 الاسم: {name}\n🆔 يوزر: @{username}\n🔑 معرف: {user_id}\n📊 عدد المستخدمين الآن: {len(unique_users)}"
        )

    # إذا كان المستخدم قد اختار "لا تشتراك" من قبل، لا يظهر له خيار الاشتراك مرة أخرى
    if context.user_data.get("continue_without_sub", False):
        await update.message.reply_text("😃 دز رابط الفيديو انتظرك")
        return

    if await is_user_member(user_id, context):
        await update.message.reply_text("مرحبا دزلي رايط الفيديو وراح احمله الك ❤️‍🔥.")
    else:
        # إنشاء زرين: اشتراك أو متابعة دون اشتراك
        keyboard = [
            [InlineKeyboardButton("🫶اشترك بالقناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("🚬لا تشتراك", callback_data="continue_without_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "قناتي الخاصة اشترك بيها يمكن تفيدك",
            reply_markup=reply_markup
        )

# دالة لمعالجة الضغط على الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "continue_without_sub":
        # حفظ حالة المستخدم (اختياره "لا تشتراك")
        context.user_data["continue_without_sub"] = True
        await query.edit_message_text(" 😃 دز رابط الفيديو انتظرك ")

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
    user = update.message.from_user
    user_id = user.id
    username = user.username if user.username else "No username"
    name = user.first_name

    # تحقق إذا كان المستخدم جديدًا وأضفه إلى قائمة المستخدمين
    if user_id not in unique_users:
        unique_users.add(user_id)
        # إشعار الأدمن بمستخدم جديد
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 مستخدم جديد بدأ استخدام البوت:\n👤 الاسم: {name}\n🆔 يوزر: @{username}\n🔑 معرف: {user_id}\n📊 عدد المستخدمين الآن: {len(unique_users)}"
        )

    message = update.message.text
    if 'tiktok.com' in message:
        video_url = download_tiktok_video(message)
        if video_url:
            await update.message.reply_text(f'انتظر جاي ينزل من: {video_url}')
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video_url)
            # إرسال رسالة بعد تحميل الفيديو
            await update.message.reply_text("🫶  هذا الفيديو و تدلل ياحلو  (اشترك بالقناة @hussaindev)")
        else:
            await update.message.reply_text(' صار خطأ، عيد المحاولة .')
    else:
        await update.message.reply_text('🙄 الرابط الي دزيته خطأ تأكد منه')

# دالة لعرض قائمة المستخدمين
async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # تحقق إذا كان المستخدم أدمن
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 هذا الأمر خاص بالأدمن فقط.")
        return

    if not unique_users:
        await update.message.reply_text("📊 لا يوجد مستخدمون حتى الآن.")
        return

    # إنشاء رسالة تحتوي على قائمة المستخدمين
    message = "📊 قائمة المستخدمين الذين استخدموا البوت:\n\n"
    for user_id in unique_users:
        message += f"🆔 معرف المستخدم: {user_id}\n"

    # إرسال الرسالة إلى الأدمن
    await update.message.reply_text(message)

# الدالة الرئيسية لتشغيل البوت
def main() -> None:
    application = Application.builder().token(TOKEN).connect_timeout(60).read_timeout(60).build()

    # إضافة معالج لرسالة الترحيب
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_message))

    # تعيين معالجات الأوامر والرسائل
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("users", show_users))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # إضافة معالج للأزرار (Inline Keyboard)
    application.add_handler(CallbackQueryHandler(button_handler))

    # بدء تشغيل البوت
    application.run_polling()

if __name__ == '__main__':
    main()
