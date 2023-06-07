import os
import logging
from datetime import time
import pytz

from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram.update import Update
from dotenv import load_dotenv

from APIs import getContact, lookUp, get_animes_current_season, getChapter, getRandomSong, correct_spelling

load_dotenv()

logging.basicConfig(filename='log_activity.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


MESSAGES = {
	'start' : 'أهلا!، هذا البوت فيه أوامر عشوائية سويتها بغرض التجربة، استخدم /help عشان تعرف الأوامر المقبولة',
	'help' : """أوامر البوت:
	/randomsong يرسل لك أغنية عشوائية
	/define يرجع لك تعريف كلمة في معجم
	/spell يصحح لك بعض الأخطاء الإملائية في الكلمة
	/animeseason يرسل لك لستة بأنميات الموسم أسبوعيا
	/getlatestchapter يرسل لك آخر تشابتر نزل لمانجا بترجمة انجليزية""",
	'unknown' : 'استخدم /help عشان تعرف الأوامر المقبولة'
}

def start(update: Update, context: CallbackContext):
	update.message.reply_text(MESSAGES['start'])
	logging.info('Command executed: /start')

def help(update: Update, context: CallbackContext):
	update.message.reply_text(MESSAGES['help'])
	logging.info('/help command executed')

def unknown(update: Update, context: CallbackContext):
	update.message.reply_text(MESSAGES['unknown'])
	logging.info('Unknown command executed')

def numberBook(update: Update, context: CallbackContext):
	try:
		phone = update.message.text.replace('/whodis ', '')
		if len(phone) != 10:
			update.message.reply_text('please send a valid number with command call (e.g. /whodis 0500000000)')
			return
		update.message.reply_text(getContact(phone))
	except Exception as e:
		logging.exception('An error occurred while calling getContact: {}'.format(str(e)))

def randomsong(update: Update, context: CallbackContext):
	try:
		update.message.reply_text(getRandomSong())
	except Exception as e:
		logging.exception('An error occurred while calling getRandomSong: {}'.format(str(e)))

def activate_animes_current_season(update: Update, context: CallbackContext):
	job_queue = context.job_queue
	job_queue.run_daily(animes_current_season, time=time(23, 35, 0, 0, pytz.timezone("Asia/Riyadh")), days=(1,), context={'chat_id': update.message.chat_id})
	context.bot.send_message(chat_id=update.message.chat_id, text="You will receieve anime updates weekly every Tues at 11:35 PM")
	
def animes_current_season(context: CallbackContext):
	try:
		messages = get_animes_current_season()
		for message in messages:
			context.bot.send_message(chat_id=context.job.context['chat_id'], text=message)
	except Exception as e:
		logging.exception('An error occurred while calling get_animes_current_season: {}'.format(str(e)))

def spell(update: Update, context: CallbackContext):
	try:
		text = update.message.text.replace('/spell ', '')
		text = update.message.text.replace('/spell', '')
		if len(text) < 2:
			update.message.reply_text('please send a sentence with command call (e.g. /spell فاكهه لذيذه)')
			return
		update.message.reply_text(correct_spelling(text))
	except Exception as e:
		logging.exception('An error occurred while calling correct_spelling: {}'.format(str(e)))

def process(dictlist, update: Update):
    if type(dictlist) == str:
        update.message.reply_text(dictlist)
        return
    acceptableDictionaries = ['المعجم: الرائد', 'المعجم: المعجم الوسيط',
                              'المعجم: اللغة العربية المعاصر', 'المعجم: مختار الصحاح'] #to avoid spamming
    for definition in dictlist:
        if definition['dictionary'] in acceptableDictionaries:
            response = definition['word'] + ':\n'
            response = response + definition['meaning'] + '\n'
            response = response + definition['dictionary'] + '\n'
            update.message.reply_text(response)

def fromDictionary(update: Update, context: CallbackContext):
	try:
		text = update.message.text.replace('/define ', '')
		text = update.message.text.replace('/define', '')
		if len(text) < 2:
			update.message.reply_text('please send word with command call (e.g. /define قرنبيط)')
			return
		definitions = lookUp(text)
		process(definitions, update)
	except Exception as e:
		logging.exception('An error occurred while calling lookUp: {}'.format(str(e)))


	
def MangaChapter(update: Update, context: CallbackContext):
	try:
		name = update.message.text.replace('/getlatestchapter ', '')
		name = update.message.text.replace('/getlatestchapter', '')
		if len(name) < 2:
			update.message.reply_text('please send manga name with command call (e.g. /getlatestchapter one piece)')
			return
		update.message.reply_text('please wait, this may take a while.')
		info = getChapter(name)
		if info['success']:
			try:
				context.bot.send_document(chat_id=update.effective_chat.id,document=info['file'], filename=info['filename'])
				update.message.reply_text('please be informed that the mangaAPI may be outdated.')
			except:
				update.message.reply_text(f"sorry, chapter could not be sent for some reason, try reading it online {info['url']}")
		else:
			update.message.reply_text(info['Exception'])
	except Exception as e:
		logging.exception('An error occurred while calling getChapter: {}'.format(str(e)))


def setUp(telegram_token):

	updater = Updater(telegram_token, use_context=True)
	dispatcher = updater.dispatcher
	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_handler(CommandHandler('help', help))
	dispatcher.add_handler(CommandHandler('randomsong', randomsong))
	# dispatcher.add_handler(CommandHandler('whodis', numberBook))
	dispatcher.add_handler(CommandHandler('define', fromDictionary))
	dispatcher.add_handler(CommandHandler('animeseason', activate_animes_current_season))
	dispatcher.add_handler(CommandHandler('getlatestchapter', MangaChapter))
	dispatcher.add_handler(CommandHandler('spell', spell))
		
	dispatcher.add_handler(MessageHandler(Filters.text, unknown))
	dispatcher.add_handler(MessageHandler(Filters.command, unknown))

	return updater


if __name__ == "__main__":
	telegram_token = os.getenv("TELEGRAM_TOKEN")
	updater = setUp(telegram_token)

	# updater.start_polling()
	# print('now running')
	# updater.idle()
	updater.start_webhook(
        listen='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        url_path=telegram_token,
        webhook_url='https://swissarmybot.onrender.com/{}'.format(telegram_token)
    )
