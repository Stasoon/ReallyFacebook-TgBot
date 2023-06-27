from datetime import datetime
from hashlib import md5

import peewee
from loguru import logger
import telebot

from keep_alive import keep_alive


db = peewee.SqliteDatabase('bot.db', check_same_thread=False)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class ChannelPostHash(BaseModel):
    post_date = peewee.DateField()
    chat_id = peewee.CharField()
    post_text_hash = peewee.CharField()


TOKEN = '5627085125:AAGWw8sFj66ESP_6clUINIovAd0lp63frgc'
bot = telebot.TeleBot(TOKEN)


@bot.channel_post_handler(content_types=['text', 'photo'])
def channel_post_checker(message):
    chat_id = message.chat.id
    message_id = message.id
    post_date = datetime.fromtimestamp(message.date).date()
    post_content_type = message.content_type
    if post_content_type == 'text':
        post_text = message.text
    elif post_content_type == 'photo':
        caption = message.caption
        if not caption:
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            logger.info(f'Delete image - {message_id}')
            return
        post_text = caption.replace('[ Фотография ]', '').strip()
    else:
        post_text = ''

    if 'https://www.facebook.com' in post_text:
        facebook_profile = post_text.split('https://www.facebook.com/')[-1]
        facebook_url = f"https://www.facebook.com/{facebook_profile}"
        post_text = post_text.replace(facebook_url, '').strip()
        markup = telebot.types.InlineKeyboardMarkup()
        button_url = telebot.types.InlineKeyboardButton(text='Связаться с автором объявления', url=facebook_url)
        markup.add(button_url)
        bot.edit_message_text(post_text, chat_id, message_id, reply_markup=markup)

    post_text_hash = md5(post_text.encode()).hexdigest()
    _, created = ChannelPostHash.get_or_create(post_date=post_date, chat_id=chat_id, post_text_hash=post_text_hash)
    if not created:
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        logger.info(f'Delete duplicate - {message_id}')


@bot.message_handler()
def show_message(message):
    logger.warning(message)


if __name__ == '__main__':
    keep_alive()
    ChannelPostHash.create_table()
    logger.info('Bot Started')
    bot.polling()