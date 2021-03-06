from threading import Thread
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from bot import LOGGER, dispatcher
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage, sendMarkup
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper import button_build

def list_buttons(update, context):
    user_id = update.message.from_user.id
    try:
        key = update.message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return sendMessage('๐๐๐ง๐ ๐ ๐ฌ๐๐๐ซ๐๐ก ๐ค๐๐ฒ ๐๐ฅ๐จ๐ง๐  ๐ฐ๐ข๐ญ๐ก ๐๐จ๐ฆ๐ฆ๐๐ง๐ ๐', context.bot, update)
    buttons = button_build.ButtonMaker()
    buttons.sbutton("แดสษชแด แด สแดแดแด", f"types {user_id} root")
    buttons.sbutton("สแดแดแดสsษชแด แด", f"types {user_id} recu")
    buttons.sbutton("แดแดษดแดแดส", f"types {user_id} cancel")
    button = InlineKeyboardMarkup(buttons.build_menu(2))
    sendMarkup('Choose option to list.', context.bot, update, button)

def select_type(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    msg = query.message
    key = msg.reply_to_message.text.split(" ", maxsplit=1)[1]
    data = query.data
    data = data.split(" ")
    if user_id != int(data[1]):
        query.answer(text="Mind Your Own Business Dude!", show_alert=True)
    elif data[2] in ["root", "recu"]:
        query.answer()
        buttons = button_build.ButtonMaker()
        buttons.sbutton("าแดสแดแดสs", f"types {user_id} folders {data[2]}")
        buttons.sbutton("าษชสแดs", f"types {user_id} files {data[2]}")
        buttons.sbutton("สแดแดส", f"types {user_id} both {data[2]}")
        buttons.sbutton("แดแดษดแดแดส", f"types {user_id} cancel")
        button = InlineKeyboardMarkup(buttons.build_menu(2))
        editMessage('Choose option to list.', msg, button)
    elif data[2] in ["files", "folders", "both"]:
        query.answer()
        list_method = data[3]
        item_type = data[2]
        editMessage(f"<b>๐๐๐๐ซ๐๐ก๐ข๐ง๐  ๐๐จ๐ซ <i>{key}</i> Please Wait...</b>", msg)
        Thread(target=_list_drive, args=(key, msg, list_method, item_type)).start()
    else:
        query.answer()
        editMessage("๐ฅ๐ข๐ฌ๐ญ ๐ก๐๐ฌ ๐๐๐๐ง ๐๐๐ง๐๐๐ฅ๐๐!๐", msg)

def _list_drive(key, bmsg, list_method, item_type):
    LOGGER.info(f"listing: {key}")
    list_method = list_method == "recu"
    gdrive = GoogleDriveHelper()
    msg, button = gdrive.drive_list(key, isRecursive=list_method, itemType=item_type)
    if button:
        editMessage(msg, bmsg, button)
    else:
        editMessage(f'๐ ๐๐จ ๐ซ๐๐ฌ๐ฎ๐ฅ๐ญ ๐๐จ๐ฎ๐ง๐ ๐๐จ๐ซ <i>{key}</i>\nUse better keywords', bmsg)

list_handler = CommandHandler(BotCommands.ListCommand, list_buttons, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
list_type_handler = CallbackQueryHandler(select_type, pattern="types", run_async=True)
search_handler = CommandHandler( BotCommands.SearchCommand, list_buttons,filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,run_async=True,)
dispatcher.add_handler(search_handler)
dispatcher.add_handler(list_handler)
dispatcher.add_handler(list_type_handler)
