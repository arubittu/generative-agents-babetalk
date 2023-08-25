import logging
import openai.error
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from collections import deque
from GenAgent import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

users = {}
intro_text = "Heyyy, I'm zaina, whats your name?"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text= intro_text)  

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = MemoryStream(user_id)
        initialize_MemoryStream(users[user_id]) # add default memories to memstream
        
    # Get the response from the GPT model
    try: 
        response_text = agent(users[user_id],update.message.text).run()
        # send query
    except openai.error.ServiceUnavailableError or openai.error.RateLimitError:
        response_text = "what? say that again?"

    # Send the response to the user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    
# async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     text_caps = ' '.join(context.args).upper()
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

if __name__ == '__main__':
    application = ApplicationBuilder().token('6226973193:AAHfYUzcDmjPopa3tXLakDylBIiKDiNzKwg').build()
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Document.ALL), echo)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    
    application.run_polling()
