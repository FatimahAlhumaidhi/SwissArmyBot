import os
from datetime import time
import pytz

from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram.update import Update
from dotenv import load_dotenv

from APIs import getContact, lookUp, get_animes_current_season, getChapter
from models import spotify

load_dotenv()

MESSAGES = {
	'start' : 'أهلا!، هذا البوت فيه أوامر عشوائية سويتها بغرض التجربة، استخدم /help عشان تعرف الأوامر المقبولة',
	'help' : """أوامر البوت:
	/randomsong يرسل لك أغنية عشوائية
	/define يرجع لك تعريف كلمة في معجم
	/whodis ترسل رقم سعودي ويعطيك الأسماء المسجلة له
	/animeseason يرسل لك لستة بأنميات الموسم أسبوعيا
	/getlatestchapter يرسل لك آخر تشابتر نزل لمانجا بترجمة انجليزية""",
	'unknown' : 'استخدم /help عشان تعرف الأوامر المقبولة'
}
	
def start(update: Update, context: CallbackContext):
	update.message.reply_text(MESSAGES['start'])

def help(update: Update, context: CallbackContext):
	update.message.reply_text(MESSAGES['help'])

def unknown(update: Update, context: CallbackContext):
	update.message.reply_text(MESSAGES['unknown'])

def numberBook(update: Update, context: CallbackContext):
	phone = update.message.text.replace('/whodis ', '') 
	update.message.reply_text(getContact(phone))

def randomsong(update: Update, context: CallbackContext):
	client = spotify()
	song = client.randomSong()
	update.message.reply_text(song)


def activate_animes_current_season(update: Update, context: CallbackContext):
	context.bot.send_message(chat_id=update.message.chat_id, text="You will receieve this weekly every Tues at 11:35 PM")
	job_queue = updater.job_queue
	job_queue.run_daily(animes_current_season, time=time(23, 35, 0, 0, pytz.timezone("Asia/Riyadh")), days=(1,), context=update.message.chat_id)
	
def animes_current_season(context: CallbackContext):
	messages = get_animes_current_season()
	for message in messages:
		context.bot.send_message(chat_id=context.job.context, text=message)


def process(dictlist, update: Update):
    if type(dictlist) == str:
        update.message.reply_text(dictlist)
        return
    acceptableDictionaries = ['المعجم: الرائد', 'المعجم: المعجم الوسيط',
                              'المعجم: لسان العرب', 'المعجم: اللغة العربية المعاصر'] #to avoid spamming
    for definition in dictlist:
        if definition['dictionary'] in acceptableDictionaries:
            response = definition['word'] + ':\n'
            response = response + definition['meaning'] + '\n'
            response = response + definition['dictionary'] + '\n'
            update.message.reply_text(response)

def fromDictionary(update: Update, context: CallbackContext):
	text = update.message.text.replace('/define ', '') 
	definitions = lookUp(text) 
	process(definitions, update)

	
def MangaChapter(update: Update, context: CallbackContext):
	name = update.message.text.replace('/getlatestchapter ', '')
	update.message.reply_text('please wait, this may take a while.')
	info = getChapter(name)
	if info['success']:
		try:
			context.bot.send_document(chat_id=update.effective_chat.id,document=open(info['file'], 'rb'), filename=info['file'])
			update.message.reply_text('please be informed that the mangaAPI may be outdated.')
		except:
			update.message.reply_text(f"sorry, chapter could not be sent for some reason, try reading it online {info['url']}")
		os.remove(info['file'])
	else:
		update.message.reply_text(info['Exception'])


def setUp(telegram_token):

	updater = Updater(telegram_token, use_context=True)
	dispatcher = updater.dispatcher
	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_handler(CommandHandler('help', help))
	dispatcher.add_handler(CommandHandler('randomsong', randomsong))
	dispatcher.add_handler(CommandHandler('whodis', numberBook))
	dispatcher.add_handler(CommandHandler('define', fromDictionary))
	dispatcher.add_handler(CommandHandler('animeseason', activate_animes_current_season, pass_job_queue=True))
	dispatcher.add_handler(CommandHandler('getlatestchapter', MangaChapter))
		
	dispatcher.add_handler(MessageHandler(Filters.text, unknown))
	dispatcher.add_handler(MessageHandler(Filters.command, unknown))

	return updater


if __name__ == "__main__":
	telegram_token = os.getenv("TELEGRAM_TOKEN")
	webhook = os.getenv("WEB_HOOK")
	updater = setUp(telegram_token)

	# updater.start_polling()
	# print('now running')
	# updater.idle()
	updater.start_webhook(listen="0.0.0.0", 
		       port=int(os.environ.get('PORT', 8443)),
		       url_path=telegram_token,
		       webhook_url='https://{}.herokuapp.com/{}'.format(webhook, telegram_token))
	# updater.bot.setWebhook('https://{}.herokuapp.com/{}'.format(webhook, telegram_token))
