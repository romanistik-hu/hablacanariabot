# handlers/restart.py

from telegram import Update
from telegram.ext import ContextTypes
from handlers import task # Asegúrate de que 'task.py' está en el directorio raíz
import logging

logger = logging.getLogger(__name__)

async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        chat_id = query.message.chat.id

        # Mensaje de reinicio con emoticonos en UTF-8
        await context.bot.send_message(chat_id=chat_id, text="¡Empezaremos de nuevo!")

        # Llamar a la función start_task para reiniciar el cuestionario
        return await task.start_task(update, context)

    except Exception as e:
        logger.error(f"Error en handle_restart: {e}")
        if update.callback_query:
            chat_id = update.callback_query.message.chat.id
            # Mensaje de error con emoticonos en UTF-8
            await context.bot.send_message(chat_id=chat_id, text="\U000026A0\U0000FE0F Ups, algo salió mal al intentar reiniciar. \U0001F615 Por favor, inténtalo de nuevo.")
        return ConversationHandler.END

