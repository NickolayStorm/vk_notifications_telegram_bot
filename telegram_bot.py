#! /usr/bin/python

from telegram import Updater
import logging
from vk_messages import VkUser


TOKEN = 'XXXXXXXXXXXXXX'
updater = Updater(TOKEN)

# Job Q for reading message updates
q = updater.job_queue

# Dictionary to store users by its id
vk_tokens = {}

# Vk application id
vk_app_id = "5344498"

# Enable Logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Helpfull function just for DRY
def put_worker_to_q(update, vk_user):
    def worker_send_messages(bot):
        messages = vk_user.get_new_messages()
        if messages:
            msg = "\n".join(messages)
            bot.sendMessage(update.message.chat_id, text=msg)
    q.put(worker_send_messages, 5, repeat=True)


def help(bot, update):
    # log_params('help', update)
    help_text = """Usage:
    /gettoken
        Returns link to vk auth token.
    /registrate <mytoken>
        Registrate your token to system. \
After that your vk notifications will be there.
    /stop
        Forget your token and stop your notifications.
    """
    bot.sendMessage(update.message.chat_id, help_text)


# Returns link for getting vk token
def get_vk_token(bot, update):
    resolutions = "friends,messages,offline"
    redirect_page = "https://oauth.vk.com/blank.html"

    text = "Your link: "
    text += "https://oauth.vk.com/authorize?client_id="
    text += vk_app_id
    text += "&display=page&redirect_uri="
    text += redirect_page
    text += "&scope="
    text += resolutions
    text += "&response_type=token&v=5.45"
    bot.sendMessage(update.message.chat_id, text=text)


# Put new token in vk dict and put new worker to an job
def registrate_vk_token(bot, update, args):
    if len(args) != 1:
        text = "Usage:\n/registrate <YOUR_TOKEN>"
        bot.sendMessage(update.message.chat_id, text=text)
        return

    telegram_user = update.message.from_user["id"]
    token = args[0]
    print("New token: %s" % token)

    try:
        vk_user = VkUser(token)
        vk_tokens.update([(telegram_user, vk_user)])

        put_worker_to_q(update, vk_user)

        text = "Your token registrate successful."
    except:
        text = "Token error"

    bot.sendMessage(update.message.chat_id, text=text)


# Remove user from dict and help
# This function should be rewrite (stop all workers, WTF?)!
def stop(bot, update):

    telegram_user = update.message.from_user["id"]
    try:
        vk_tokens.pop(telegram_user)

        q.stop()

        for u in vk_tokens.values():
            put_worker_to_q(update, u)

        text = "Your token removed successful."

    except KeyError:
        text = "Your token does not exist."

    bot.sendMessage(update.message.chat_id, text)


def main():
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers for Telegram messages
    dp.addTelegramCommandHandler("help", help)
    dp.addTelegramCommandHandler("gettoken", get_vk_token)
    dp.addTelegramCommandHandler("registrate", registrate_vk_token)
    dp.addTelegramCommandHandler("stop", stop)
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
