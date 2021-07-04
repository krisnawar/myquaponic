import telebot
import time, datetime

bot = telebot.TeleBot('1247524897:AAHAdZGhWNky6_gQfjAMduzVPhxqPDqiURM')

#@bot.message_handler(commands=['halo'])
#def send_welcome(message):
#	bot.reply_to(message, 'Halo juga')

#bot.polling()

while True:
	bot.send_message('1469794072', 'Boom Message')
	time.sleep(5)
