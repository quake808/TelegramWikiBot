# -*- coding: utf-8 -*-
#!usr/bin/env python

import telebot
import config
import cherrypy
import requests
import wikipediaapi
from telebot import types

WEBHOOK_HOST = 'IP'
WEBHOOK_PORT = 88  
WEBHOOK_LISTEN = 'IP' 

WEBHOOK_SSL_CERT = './webhook_cert.pem'  
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

bot = telebot.TeleBot (config.token)

class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)

            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.from_user.id,
            '<b>ВикиБот</b> - это целая википедия в одном боте. '
            'Просто отправьте неизвестное вам слово или термин и в ответ получите его определение.', parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    wiki_wiki = wikipediaapi.Wikipedia('ru')
    usertext = message.text
    page_py = wiki_wiki.page(usertext)
    print("Page - Title: %s" % page_py.title)
    print("Page - Summary: %s" % page_py.summary[0:60])
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="📖 Открыть на Wikipedia", callback_data="Открыть",
                                                 url=page_py.fullurl)
    keyboard.add(callback_button)
    bot.send_message(message.chat.id,
                     "<b>Заголовок:</b> \n" + page_py.title + "\n \n"
                     "<b>Описание:</b> \n" + page_py.summary + "\n", parse_mode='HTML', reply_markup=keyboard)

cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

"""
bot.polling(none_stop=True, interval=0)
"""