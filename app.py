import telegram
import html
import json
import logging
import traceback
from datetime import date
from telegram import Update, ParseMode, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)
from InMemDb import InMemDb


GENDER, PHOTO, LOCATION, BIO, S_LOCATION, DESCRIPTION = range(6)
TOKEN = '1389694102:AAFkvMe3o9JIhs2MpuAcUVFDI3RBL7EPQbQ'
POINTS = 300
InMemDb = InMemDb()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

DEV_CHAT_ID = "456258978"

#location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
#custom_keyboard = [[location_keyboard]]
#reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
# bot.send_message(chat_id=yo_id, text="Would you mind sharing your location and contact with me?", reply_markup=reply_markup)
# bot.get_file(u.message.photo[-1]).download("sdfdsa.jpg")
# print([u.message.photo for u in updates if u.message.photo])


def send(update, context):
    if InMemDb.user_exists(update.message.chat_id):
        update.message.reply_text('Primero manda una foto del residuo!', reply_markup=ReplyKeyboardRemove())
        return PHOTO
    return update.message.reply_text("Para comenzar utiliza /start")


def start(update, context):
    if InMemDb.user_exists(update.message.chat_id):
        update.message.reply_text(f"{update.message.from_user.first_name}, para reportar un residuo utiliza /send")
    else:
        InMemDb.new_user(update.message.chat_id, update.message.from_user.first_name)
        reply_keyboard = [['Hombre', 'Mujer', 'Otre']]
        update.message.reply_text(
            f'Hola {update.message.from_user.first_name}, como va? Comenzaremos con unas breves preguntas. '
            f'-> {update.message.from_user.first_name} <- Sera tu nombre de usuario.'
            'Manda /cancel para cancelar.\n\n Podes indicarme tu genero? (Es para fines estadísticos)',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return GENDER


def gender(update, context):
    user = update.message.from_user
    logger.info("Genero de %s: %s", user.first_name, update.message.text)
    InMemDb.update_gender(update.message.chat_id, update.message.text)
    update.message.reply_text(f'Muy bien, muchas gracias {user.first_name}. A continuación puedes indicarnos'
                              f' algo que te describa como ciudadano')
    return BIO


def bio(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    InMemDb.update_bio(update.message.chat_id, update.message.text)
    update.message.reply_text('Perfecto! Ya terminamos. Ahora si queres podes empezar a usar la aplicacion para'
                              f' mandarnos la e-basura que encuentres! Cada colaboración correspondera a {POINTS} puntos')
    update.message.reply_text(f'{user.first_name}, gracias por colaborar!'
                              f' Pulse /help para conocer la ayuda. /send para enviar una foto del residuo encontrado.')
    return ConversationHandler.END


def rcv_description(update, context):
    user = update.message.from_user
    InMemDb.add_user_report_description(update.message.chat_id, update.message.text)
    logger.info("Descripcion del RAEE %s ", update.message.text)
    update.message.reply_text(f'Muy bien, muchas gracias {user.first_name}. Se le ha recompensado con {POINTS}. '
                              f'Puede chequear cuantos puntos posee cliqueando /points')
    #report_new_raee_to_admin(update.message.chat_id, context)
    InMemDb.add_points(update.message.chat_id, POINTS)
    return ConversationHandler.END


def report_new_raee_to_admin(user_chat_id, context):
    report = InMemDb.last_reports()
    context.bot.send_message(chat_id=DEV_CHAT_ID, text=report)


def check_points(update, context):
    user = update.message.from_user
    logger.info("User %s wants to check points", user.first_name)
    points = InMemDb.user_points(update.message.chat_id)
    update.message.reply_text(f'Puntos actuales son: {points[0]}')


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(f'Chau {user.first_name}, nos vemos pronto!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def help_callback(update, context):
    msg = "Hola soy el bot que te ayudara a ser un ciudadano responsable." \
          "Para registrarte puedes mandar /start o si ya estas registrado y quieres reportar un residuo electrónico " \
          "puedes pulsar /send. Para chequear tus puntos actuales puedes pulsar /check_points." \
          "Muchas gracias por ser un buen ciudadano!"
    update.message.reply_text(msg)


def error_handler(update: Update, context: CallbackContext):
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb = ''.join(tb_list)
    message = (
        'An exception was raised while handling an update\n'
        '<pre>update = {}</pre>\n\n'
        '<pre>context.chat_data = {}</pre>\n\n'
        '<pre>context.user_data = {}</pre>\n\n'
        '<pre>{}</pre>'
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(str(context.chat_data)),
        html.escape(str(context.user_data)),
        html.escape(tb)
    )
    context.bot.send_message(chat_id=DEV_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


def rcv_location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    InMemDb.add_user_report_location(update.message.chat_id, user_location.latitude, user_location.longitude )
    logger.info("Ubicacion de %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude)
    update.message.reply_text(f'Muy bien, muchas gracias {user.first_name}. Por favor describa '
                              f'brevemente el objeto encontrado.')
    return DESCRIPTION


def rcv_photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    InMemDb.new_report_w_pic(update.message.chat_id, f'{user.first_name}_{update.message.chat_id}_{str(date.today())}.jpg')
    photo_file.download(f'{user.first_name}_{update.message.chat_id}_{str(date.today())}.jpg')
    logger.info("Imagen de %s: %s", user.first_name, f'{user.first_name}_{update.message.chat_id}_{str(date.today())}.jpg')
    update.message.reply_text('Perfecto, ahora manda la ubicacion del residuo encontrado!')
    location_keyboard = telegram.KeyboardButton(text="Enviar ubicacion", request_location=True)
    custom_keyboard = [[location_keyboard]]
    update.message.reply_text('Ubicacion: ', reply_markup=ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True))
    return LOCATION


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    conv_handler_start = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        allow_reentry=True,
        states={
            GENDER: [MessageHandler(Filters.regex('^(Hombre|Mujer|Otre)$'), gender)],
            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    conv_handler_send = ConversationHandler(
        entry_points=[CommandHandler('send', send)],
        allow_reentry=True,
        states={
            PHOTO: [MessageHandler(Filters.photo, rcv_photo)],
            LOCATION: [MessageHandler(Filters.location, rcv_location)],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, rcv_description)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler_start)
    dp.add_handler(conv_handler_send)
    dp.add_handler(CommandHandler("points", check_points))
    dp.add_handler(CommandHandler("help", help_callback))
    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()


"""

3.x) WebHook ngrok

"""



"""
GENDER, PHOTO, LOCATION, BIO = range(4)


def start(update, context):
    reply_keyboard = [['Boy', 'Girl', 'Other']]

    update.message.reply_text(
        'Hi! My name is Professor Bot. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'Are you a boy or a girl?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return GENDER


def gender(update, context):
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('I see! Please send me a photo of yourself, '
                              'so I know what you look like, or send /skip if you don\'t want to.',
                              reply_markup=ReplyKeyboardRemove())

    return PHOTO


def photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Gorgeous! Now, send me your location please, '
                              'or send /skip if you don\'t want to.')

    return LOCATION


def skip_photo(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')

    return LOCATION


def location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    update.message.reply_text('Maybe I can visit you sometime! '
                              'At last, tell me something about yourself.')

    return BIO


def skip_location(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! '
                              'At last, tell me something about yourself.')

    return BIO


def bio(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],

            PHOTO: [MessageHandler(Filters.photo, photo),
                    CommandHandler('skip', skip_photo)],

            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],

            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

"""
