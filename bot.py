import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Union, List
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from dbhelper import DBHelper
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
import json
import config
db = DBHelper()
conn = sqlite3.connect('users.sqlite', check_same_thread=False)
updater = Updater(config.token, use_context=True)

f = open('translate.json', encoding='utf-8')
data = json.load(f)

# start command


def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if db.get_user(chat_id) == None:
        db.add_user(chat_id, "en")
    lang = db.get_lang(chat_id)
    if update.message.from_user.username == None:
        username = update.message.from_user.first_name
    else:
        username = '@' + update.message.from_user.username
    update.message.reply_text(
        f"{data['hello'][lang]} {username}. {data['welcome'][lang]} {data['help'][lang]} ")

# set language command


def set_lang(update: Update, context: CallbackContext):
    button_list = [
        InlineKeyboardButton("🇬🇧English", callback_data="en"),
        InlineKeyboardButton("🇦🇿Azərbaycanca", callback_data="az")
    ]
    chat_id = update.message.chat_id
    if db.get_user(chat_id) == None:
        db.add_user(chat_id, "en")
    lang = db.get_lang(chat_id)
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=len(button_list)))
    update.message.reply_text(
        data['lang'][lang], reply_markup=reply_markup)

# build buttons fuction


def build_menu(
    buttons: List[InlineKeyboardButton],
    n_cols: int,
    header_buttons: Union[InlineKeyboardButton,
                          List[InlineKeyboardButton]] = None,
    footer_buttons: Union[InlineKeyboardButton,
                          List[InlineKeyboardButton]] = None
) -> List[List[InlineKeyboardButton]]:
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons if isinstance(
            header_buttons, list) else [header_buttons])
    if footer_buttons:
        menu.append(footer_buttons if isinstance(
            footer_buttons, list) else [footer_buttons])
    return menu

# button callback


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    lang = db.get_lang(query.message.chat_id)
    if query.data == "en":
        db.set_lang(query.message.chat_id, "en")
        query.edit_message_text(
            data['lang_changed']['en'], reply_markup=None)
    elif query.data == "az":
        db.set_lang(query.message.chat_id, "az")
        query.edit_message_text(
            data['lang_changed']['az'], reply_markup=None)

# help command


def help(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if db.get_user(chat_id) == None:
        db.add_user(chat_id, "en")
    lang = db.get_lang(chat_id)
    update.message.reply_text(f"""
    /calculate  -  {data['calculate'][lang]} {data['enter'][lang]} {data['example'][lang]}  /calculate 175 75
/set_lang  -  {data['set_lang'][lang]}
/about_bmi  -  {data['about_bmi'][lang]}""")

# about bmi command


def about_bmi(update: Update, context: CallbackContext):
    lang = db.get_lang(update.message.chat_id)
    update.message.reply_text(f"""{data['info_about_bmi'][lang]}""")

# calculate command


def calculate(update: Update, context: CallbackContext):
    user_input = update.message.text
    chat_id = update.message.chat_id
    if db.get_user(chat_id) == None:
        db.add_user(chat_id, "en")
    lang = db.get_lang(chat_id)
    update.message.reply_text(calculate_bmi(user_input, lang))

# check if user input is number


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


# calculate bmi fuction


def calculate_bmi(user_input, lang):
    user_input = user_input.replace("/calculate@testbot12673_bot ", "")
    user_input = user_input.replace("/calculate ", "")

    user_input = user_input.split()
    if len(user_input) == 2:
        height_input = user_input[0]
        weight_input = user_input[1]
        if isfloat(height_input) and isfloat(weight_input):
            height = float(height_input)
            weight = float(weight_input)
            healty_weight_low = 18.5*(height/100)**2
            healty_weight_up = 24.9*(height/100)**2
            healty_weight_low = round(healty_weight_low, 3)
            healty_weight_up = round(healty_weight_up, 3)
            healty_weight = f"{data['healty_weight'][lang] } {healty_weight_low} {data['to'][lang] } {healty_weight_up} {data['kg'][lang]}"
            if height > 250 or height < 50 or height == 0:
                return data['height_error'][lang]
            elif weight > 300 or weight < 1:
                return data['weight_error'][lang]
            else:
                bmi = weight / (height / 100) ** 2
                bmi_round = round(bmi, 3)
                if bmi <= 18.4:
                    return f"{data['bmi'][lang]} {bmi_round} {data['underweight'][lang] } {healty_weight}"
                elif bmi > 18.4 and bmi <= 24.9:
                    return f"{data['bmi'][lang]} {bmi_round} {data['normal'][lang] } {healty_weight}"
                elif bmi > 24.9 and bmi <= 29.9:
                    return f"{data['bmi'][lang]} {bmi_round} {data['overweight'][lang] } {healty_weight}"
                elif bmi > 29.9:
                    return f"{data['bmi'][lang]} {bmi_round} {data['obese'][lang] } {healty_weight}"
        elif not isfloat(height_input):
            return data['height_error'][lang]
        else:
            return data['weight_error'][lang]
    else:
        return f"{data['enter'][lang]} {data['example'][lang]} /calculate 175 75"


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('calculate', calculate))
updater.dispatcher.add_handler(CommandHandler('set_lang', set_lang))
updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.dispatcher.add_handler(CommandHandler('about_bmi', about_bmi))
updater.start_polling()
