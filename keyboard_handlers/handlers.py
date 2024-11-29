import os
import sys

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, InputMediaPhoto, Bot
# from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

sys.path.append("../")
from db_handlers.handlers import *
from third_party.picture_redactor import *
from third_party.ops import *
from  balls_admin import Orders


async def cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = update.effective_user.name
    dict_of_nicks = dict(get_id_and_nicknames_from_DB())

    ordered_common_balls_info = get_ordered_common_balls_from_DB(dict_of_nicks[nickname])
    ordered_shaped_balls_info = get_ordered_shaped_balls_from_DB(dict_of_nicks[nickname])

    common_pictures_paths = [i[3] for i in ordered_common_balls_info]
    for i in range(len(common_pictures_paths)):
        common_pictures_paths[i] = gen_picture_path(common_pictures_paths[i], balloon_type="common")
    shaped_pictures_paths = [i[2] for i in ordered_shaped_balls_info]
    for i in range(len(shaped_pictures_paths)):
        shaped_pictures_paths[i] = gen_picture_path(shaped_pictures_paths[i], balloon_type="shaped")

    pictures_paths = common_pictures_paths + shaped_pictures_paths
    chat_id = update.effective_chat.id
    i = 1
    list_of_media = []
    media_per_msg = []
    for path in pictures_paths:
        trash_path = add_sign_to_picture_and_save_to_trash(path, "[" + str(i) + "]")
        with open(trash_path, 'rb') as file:
            media_per_msg.append(InputMediaPhoto(file))
            i += 1
        if i % 10 == 0:
            list_of_media.append(media_per_msg)
            media_per_msg = []
    if i % 10 != 0:
        list_of_media.append(media_per_msg)
        media_per_msg = []

    for msg in list_of_media:
        await context.bot.send_media_group(chat_id, msg)
    path_to_trash_dir = remove_last_segment_in_path(trash_path)
    trash_files_names = os.listdir(path_to_trash_dir)
    for file_name in trash_files_names:
        os.remove(os.path.join(path_to_trash_dir, file_name))

    ordered_own_balls_info = get_own_shaped_balls_from_DB(dict_of_nicks[nickname])
    text = gen_cart_msg(ordered_common_balls_info, ordered_shaped_balls_info, ordered_own_balls_info)

    await update.message.reply_text('''\U0001F388 Ваша корзина:\n\n_Если в сообщении выше не видно номеров на картинках, откройте их, пожалуйста, по одной и убедитесь в правильности бронирования_\n\n'''
                                + text, parse_mode="Markdown")


def gen_orders_msg(common_orders=None, shaped_orders=None, own_orders=None):
    all_orders = ""

    if common_orders:
        for i in range(len(common_orders)):
            all_orders += (f"[{i+1}] -- заказано {common_orders[i][6]} шт, "
                           f"итоговая стоимость - {common_orders[i][6] * common_orders[i][7]}₽ ({common_orders[i][8]})\n")
    if shaped_orders:
        for i in range(len(shaped_orders)):
            all_orders += (f"[{i + len(common_orders) + 1}] -- заказано {shaped_orders[i][4]} шт, "
                           f"итоговая стоимость - {shaped_orders[i][4] * shaped_orders[i][5]}₽ ({shaped_orders[i][6]})\n")

    if own_orders:
        all_orders += f"\nСвоих шариков заказано: {sum(list(map(lambda x: x[0], own_orders)))} шт"

    return str(all_orders)


def customers_nicks_keybord():
    all_nicks = set()
    keyboard = [[]]

    for types in get_orders():
        if types:
            for l in types:
                all_nicks.add(l[-1])

    for nick in all_nicks:
        keyboard[0].append(InlineKeyboardButton(nick, callback_data="confirm_orders"))

    return keyboard


keyboard_dict = {
    "start": {
        "keyboard": [
            [
                InlineKeyboardButton("Заказы", callback_data="show_orders"),
                InlineKeyboardButton("База", callback_data="edit_db"),
            ]
        ],
        "text": "Привет, я Balooadmin. С моей помощью ты можешь управлять заказами и каталогом шариков"
    },
    "show_orders": {
        "keyboard": customers_nicks_keybord(),
        "text": (gen_orders_msg(*get_orders()) + "\n\nВыбери пользователя, заказ которого ты хочешь обработать")
    },
    "confirm_orders": {
        "keyboard": [],
        "text": "Вы уверены, что выбрали нужный заказ? Для подтвержденмя напиши [ПОДВЕРДИТЬ]"
    },
    "edit_db": {
        "keyboard": [
            [
                InlineKeyboardButton("Добавить слот", callback_data="add_item"),
                InlineKeyboardButton("Удалить слот", callback_data="delete_item"),
            ]
        ],
        "text": "Здесь ты можешь изменять базу с каталогом шариков"
    },
    "add_item": {
        "keyboard":[

        ],
        "text": "Для обновления или пополнения товров, напиши тип шарика (фигруный или обычный).../"
                "/напиши сообщение по примеру [тип, материал/подтип, (цвет)]"
        #TODO решить в какой форме сделать пополнение: по окну на параметр или задавать все параметры в одном сообщении
    },
    "delete_item": {
        "keyboard": [

        ],
        "text": "Для удаления товров, напиши тип шарика (фигруный или обычный).../"
                "/напиши сообщение по примеру [тип, материал/подтип, (цвет)]"
        #TODO решить в какой форме сделать пополнение: по окну на параметр или задавать все параметры в одном сообщении
    }
}

#   "": {
#       "keyboard": [
#
#       ],
#       "text": ""
#   },


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard_level = "start"
    reply_markup = InlineKeyboardMarkup(keyboard_dict[keyboard_level]['keyboard'])
    await update.message.reply_text(
        keyboard_dict[keyboard_level]['text'],
        reply_markup=reply_markup)


async def back(query, context):
    keyboard_level = query.data.split("|")[1]
    #TODO особые хендлеры для сломанных клавиатур
    await query.edit_message_text(keyboard_dict[keyboard_level]['text'],
                                  reply_markup=InlineKeyboardMarkup(keyboard_dict[keyboard_level]['keyboard']))



async def show_orders(query):
    orders = Orders()

    # dict_of_nicks = dict(get_customers())
    # #TODO Получить список путей к картинкам всех заказанных шариков
    # ordered_common_balls_info = get_ordered_common_balls_from_DB(dict_of_nicks[nickname])
    # ordered_shaped_balls_info = get_ordered_shaped_balls_from_DB(dict_of_nicks[nickname])
    #
    # common_pictures_paths = [i[3] for i in ordered_common_balls_info]
    # for i in range(len(common_pictures_paths)):
    #     common_pictures_paths[i] = gen_picture_path(common_pictures_paths[i], balloon_type="common")
    # shaped_pictures_paths = [i[2] for i in ordered_shaped_balls_info]
    # for i in range(len(shaped_pictures_paths)):
    #     shaped_pictures_paths[i] = gen_picture_path(shaped_pictures_paths[i], balloon_type="shaped")
    #
    # pictures_paths = common_pictures_paths + shaped_pictures_paths
    # chat_id = update.effective_chat.id
    # i = 1
    # list_of_media = []
    # media_per_msg = []
    # for path in pictures_paths:
    #     trash_path = add_sign_to_picture_and_save_to_trash(path, "[" + str(i) + "]")
    #     with open(trash_path, 'rb') as file:
    #         media_per_msg.append(InputMediaPhoto(file))
    #         i += 1
    #     if i % 10 == 0:
    #         list_of_media.append(media_per_msg)
    #         media_per_msg = []
    # if i % 10 != 0:
    #     list_of_media.append(media_per_msg)
    #     media_per_msg = []
    #
    # for msg in list_of_media:
    #     await context.bot.send_media_group(chat_id, msg)
    # path_to_trash_dir = remove_last_segment_in_path(trash_path)
    # trash_files_names = os.listdir(path_to_trash_dir)
    # for file_name in trash_files_names:
    #     os.remove(os.path.join(path_to_trash_dir, file_name))
    #
    # ordered_own_balls_info = get_own_shaped_balls_from_DB(dict_of_nicks[nickname])
    # text = gen_cart_msg(ordered_common_balls_info, ordered_shaped_balls_info, ordered_own_balls_info)


    keyboard_level = "show_orders"
    text = keyboard_dict[keyboard_level]['text']
    reply_markup = InlineKeyboardMarkup(keyboard_dict[keyboard_level]['keyboard'])
    await query.edit_message_text(text, reply_markup=reply_markup)


async def confirm_orders(update: Update):
    keyboard_level = "confirm_orders"
    await update.message.reply_text(
        keyboard_dict[keyboard_level]['text'],
        reply_markup=InlineKeyboardMarkup(keyboard_dict[keyboard_level]['keyboard']))



async def edit_db(update: Update):
    keyboard_level = "edit_db"
    await update.message.reply_text(
        keyboard_dict[keyboard_level]['text'],
        reply_markup=InlineKeyboardMarkup(keyboard_dict[keyboard_level]['keyboard']))


async def add_item(update: Update):
    keyboard_level = "add_item"
    await update.message.reply_text(
        keyboard_dict[keyboard_level]['text'],
        reply_markup=InlineKeyboardMarkup(keyboard_dict[keyboard_level]['keyboard']))


async def delete_item(update: Update):
    keyboard_level = "delete_item"
    await update.message.reply_text(
        keyboard_dict[keyboard_level]['text'],
        reply_markup=InlineKeyboardMarkup(keyboard_dict[keyboard_level]['keyboard']))


if __name__ == "__main__":
    print(gen_orders_msg(*get_orders()))