# consent_individual.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from forms import consentimientos_collection, textos_consentimientos_collection, CONSENTIMIENTO_INDIVIDUAL
from datetime import datetime
from handlers.individual import start_individual_registration
import logging

logger = logging.getLogger(__name__)

async def show_consent_individual(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    try:
        consentimiento_text = textos_consentimientos_collection.find_one({"version": "1.0"})
        if consentimiento_text:
            # Crear los botones en línea para "Aceptar" y "Rechazar"
            keyboard = [
                [InlineKeyboardButton("\U0001F91D Aceptar", callback_data='aceptar_consentimiento')],
                [InlineKeyboardButton("\U0001F6AB Rechazar", callback_data='rechazar_consentimiento')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=user_id,
                text=f"\U0001F4DD {consentimiento_text['texto_consentimiento']}\n\nPor favor, selecciona una opción para continuar:",
                reply_markup=reply_markup
            )
            return CONSENTIMIENTO_INDIVIDUAL
        else:
            await context.bot.send_message(chat_id=user_id, text="No se encontró el texto del consentimiento para la versión 1.0.")
            return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error en show_consent_individual: {e}")
        await context.bot.send_message(chat_id=user_id, text="Ocurrió un error al mostrar el consentimiento individual.")
        return ConversationHandler.END

async def handle_consent_individual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        decision = query.data

        if decision == 'aceptar_consentimiento':
            estado = 'firmado'
            await query.edit_message_text("\U00002705 Has aceptado el consentimiento. ¡Gracias por tu confianza! A continuación, comenzaremos a recolectar tus datos.")
            # Registrar el consentimiento firmado en la base de datos
            consentimientos_collection.insert_one({
                'usuario_id': str(user_id),
                'fecha_consentimiento': datetime.utcnow(),
                'estado': estado,
                'version_consentimiento': '1.0'
            })
            return await start_individual_registration(update, context)

        elif decision == 'rechazar_consentimiento':
            estado = 'rechazado'
            await query.edit_message_text("\U0001F6AB Has rechazado el consentimiento. Lamentamos que no puedas continuar, pero respetamos tu decisión.")
            # Registrar el consentimiento rechazado en la base de datos
            consentimientos_collection.insert_one({
                'usuario_id': str(user_id),
                'fecha_consentimiento': datetime.utcnow(),
                'estado': estado,
                'version_consentimiento': '1.0'
            })
            return ConversationHandler.END

        else:
            await query.edit_message_text("\U000026A0 Selección no válida. Por favor, elige 'Aceptar' o 'Rechazar'.")
            return CONSENTIMIENTO_INDIVIDUAL

    except Exception as e:
        logger.error(f"Error en handle_consent_individual: {e}")
        await context.bot.send_message(chat_id=user_id, text="Ocurrió un error al manejar el consentimiento individual.")
        return ConversationHandler.END

