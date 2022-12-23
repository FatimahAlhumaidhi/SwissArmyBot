import os
import json

from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram.update import Update
from dotenv import load_dotenv

from APIs import getContact, lookUp
from models import spotify

load_dotenv()

MESSAGES = {
	'start' : 'أهلا!، هذا البوت فيه أوامر عشوائية سويتها بغرض التجربة، استخدم /help عشان تعرف الأوامر المقبولة',
	'help' : """أوامر البوت:
	/spell يتحقق من صحة الإملاء في جملة عربية
	/gimme يرسل لك أغنية عشوائية
	/whatdis يرجع لك تعريف كلمة من معجم صغير
	/whodis ترسل رقم سعودي ويعطيك الأسماء المسجلة له
	/correct يصحح لك صياغة جملة عربية""",
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

def spoti(update: Update, context: CallbackContext):
	client = spotify()
	song = client.randomSong()
	update.message.reply_text(song)


def process(dictlist, update: Update, context: CallbackContext):
    if type(dictlist) == str:
        update.message.reply_text(dictlist)
        return
    acceptableDictionaries = ['المعجم: الرائد', 'المعجم: المعجم الوسيط',
                              'المعجم: لسان العرب', 'المعجم: عربي عامة',
                              'المعجم: القاموس المحيط', 'المعجم: اللغة العربية المعاصر']
    for definition in dictlist:
        if definition['dictionary'] in acceptableDictionaries:
            response = definition['word'] + ':\n'
            response = response + definition['meaning'] + '\n'
            response = response + definition['dictionary'] + '\n'
            update.message.reply_text(response)


def fromDictionary(update: Update, context: CallbackContext):
	text = update.message.text.replace('/whatdis ', '') 
	print(text)
	definitions = lookUp(text) 
	process(definitions, update, context)
	

# TODO: 
def checkSpell(update: Update, context: CallbackContext):
	update.message.reply_text('sorry, I have not implement this yet.')

def grammer(update: Update, context: CallbackContext):
	update.message.reply_text('sorry, I have not implement this yet.')
	
def setUp():
	telegram_token = os.getenv("TELEGRAM_TOKEN")

	updater = Updater(telegram_token, use_context=True)
	updater.dispatcher.add_handler(CommandHandler('start', start))
	updater.dispatcher.add_handler(CommandHandler('help', help))
	updater.dispatcher.add_handler(CommandHandler('gimme', spoti))
	updater.dispatcher.add_handler(CommandHandler('whodis', numberBook))
	updater.dispatcher.add_handler(CommandHandler('whatdis', fromDictionary))
		
	updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
	updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

	return updater



updater = setUp()
updater.start_polling()
print('now running:')
updater.idle()
# updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get('PORT', 5000)), url_path=telegram_token)
# updater.bot.setWebhook('https://arabicfixmebot.herokuapp.com/' + telegram_token)
