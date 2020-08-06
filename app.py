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
DEV_CHAT_ID = "456258978"
POINTS = 300
InMemDb = InMemDb()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


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


def report_new_raee_to_admin(user_chat_id, context):
    report = InMemDb.last_reports()
    context.bot.send_message(chat_id=DEV_CHAT_ID, text=report)


def check_points(update, context):
    user = update.message.from_user
    logger.info("User %s wants to check points", user.first_name)
    points = InMemDb.user_points(update.message.chat_id)
    update.message.reply_text(f'Puntos actuales son: {points[0]}')


def rcv_photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    InMemDb.new_report_w_pic(update.message.chat_id,
                             f'{user.first_name}_{update.message.chat_id}_{str(date.today())}.jpg')
    photo_file.download(f'{user.first_name}_{update.message.chat_id}_{str(date.today())}.jpg')
    logger.info("Imagen de %s: %s", user.first_name,
                f'{user.first_name}_{update.message.chat_id}_{str(date.today())}.jpg')
    update.message.reply_text('Perfecto, ahora manda la ubicacion del residuo encontrado!')
    location_keyboard = telegram.KeyboardButton(text="Enviar ubicacion", request_location=True)
    custom_keyboard = [[location_keyboard]]
    update.message.reply_text('Ubicacion: ', reply_markup=ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True))
    return LOCATION


def rcv_location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    InMemDb.add_user_report_location(update.message.chat_id, user_location.latitude, user_location.longitude)
    logger.info("Ubicacion de %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude)
    update.message.reply_text(f'Muy bien, muchas gracias {user.first_name}. Por favor describa '
                              f'brevemente el objeto encontrado.')
    return DESCRIPTION


def rcv_description(update, context):
    user = update.message.from_user
    InMemDb.add_user_report_description(update.message.chat_id, update.message.text)
    logger.info("Descripcion del RAEE %s ", update.message.text)
    update.message.reply_text(f'Muy bien, muchas gracias {user.first_name}. Se le ha recompensado con {POINTS}. '
                              f'Puede chequear cuantos puntos posee cliqueando /points')
    # report_new_raee_to_admin(update.message.chat_id, context)
    InMemDb.add_points(update.message.chat_id, POINTS)
    return ConversationHandler.END


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
