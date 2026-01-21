# handlers/exit.py

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler 
import logging

logger = logging.getLogger(__name__)

async def handle_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        chat_id = query.message.chat.id

        # Mensaje de agradecimiento con emoticonos en UTF-8
        await context.bot.send_message(chat_id=chat_id, text="¡Gracias por participar! \U0001F60A\U0001F44B Hasta la próxima. \U0001F31F")
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error en handle_exit: {e}")
        if update.callback_query:
            chat_id = update.callback_query.message.chat.id
            # Mensaje de error con emoticonos en UTF-8
            await context.bot.send_message(chat_id=chat_id, text="\U000026A0\U0000FE0F Ocurrió un error al salir. \U0001F615 Inténtalo de nuevo.")
        return ConversationHandler.END
