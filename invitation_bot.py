#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is the echobot published https://docs.python-telegram-bot.org/en/stable/examples.echobot.html with a few modifications.

import logging
import os
import json

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Load config 
CONFIG_FILE = "resources/config.json"
CONFIG = None
with open(CONFIG_FILE) as f:
        CONFIG = json.loads(f.read())

#TODO: Delete it
PASS = '1234'

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    #Initialize users dict
    if context.user_data.get('users') is None:
         context.user_data["users"] = {}

    # Add user to users dict
    context.user_data.get("users")[user.id] = {"attempts": 0, "blocked": True}
    
    # Send greetings message
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Can you give us an invitation code?",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message. This is highly modified """

    # Get the user from the users dict, using the user_id from the received message
    user_from_message = context.user_data.get("users").get(update.message.from_user['id'])

    # if user is not blocked -> echo message
    if user_from_message.get('blocked') is False:
        await update.message.reply_text(update.message.text)
    else:
        # User have tried 3 or more times
        if user_from_message.get('attempts') > 2:
            user_from_message['attempts'] += 1
            await update.message.reply_text("Sorry. You are blocked. To restart use /start")
        else:
            user_from_message['attempts'] += 1
            # User inputs a correct invitation value
            if update.message.text == PASS:
                user_from_message['blocked'] = False
                await update.message.reply_text("Congrats! You've unlocked the echo bot")
            # User inputs a wrong invitation value but still have chances
            else:
                await update.message.reply_text("Wrong code!")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ['TG_INVITATION_BOT_TOKEN']).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()