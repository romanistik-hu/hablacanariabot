# consent_group.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from forms import consentimientos_collection, textos_consentimientos_collection, CONSENTIMIENTO_GRUPAL
from datetime import datetime
from handlers.group import start_group_registration
import logging

logger = logging.getLogger(__name__)

async def show_consent_group(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    try:
        consentimiento_text = textos_consentimientos_collection.find_one({"version": "1.0_grupal"})
        if consentimiento_text:
            # Crear los botones en línea para "Aceptar" y "Rechazar"
            keyboard = [
                [InlineKeyboardButton("\U0001F91D Aceptar", callback_data='aceptar_consentimiento_grupal')],
                [InlineKeyboardButton("\U0001F6AB Rechazar", callback_data='rechazar_consentimiento_grupal')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=user_id,
                text=f"\U0001F4DD {consentimiento_text['texto_consentimiento']}\n\nPor favor, seleccionen una opción para continuar:",
                reply_markup=reply_markup
            )
            return CONSENTIMIENTO_GRUPAL
        else:
            await context.bot.send_message(chat_id=user_id, text="No se encontró el texto del consentimiento grupal para la versión 1.0_grupal.")
            return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error en show_consent_group: {e}")
        await context.bot.send_message(chat_id=user_id, text="Ocurrió un error al mostrar el consentimiento grupal.")
        return ConversationHandler.END

async def handle_consent_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        decision = query.data

        if decision == 'aceptar_consentimiento_grupal':
            estado = 'firmado'
            await query.edit_message_text("\U00002705 Han aceptado el consentimiento. ¡Gracias por vuestra confianza! A continuación, comenzaremos a recolectar los datos.")
            # Registrar el consentimiento firmado en la base de datos
            consentimientos_collection.insert_one({
                'usuario_id': str(user_id),
                'fecha_consentimiento': datetime.utcnow(),
                'estado': estado,
                'version_consentimiento': '1.0_grupal'
            })
            return await start_group_registration(update, context)

        elif decision == 'rechazar_consentimiento_grupal':
            estado = 'rechazado'
            await query.edit_message_text("\U0001F6AB Han rechazado el consentimiento. Lamentamos que no puedan continuar, pero respetamos vuestra decisión.")
            # Registrar el consentimiento rechazado en la base de datos
            consentimientos_collection.insert_one({
                'usuario_id': str(user_id),
                'fecha_consentimiento': datetime.utcnow(),
                'estado': estado,
                'version_consentimiento': '1.0_grupal'
            })
            return ConversationHandler.END

        else:
            await query.edit_message_text("\U000026A0 Selección no válida. Por favor, seleccionen 'Aceptar' o 'Rechazar'.")
            return CONSENTIMIENTO_GRUPAL

    except Exception as e:
        logger.error(f"Error en handle_consent_group: {e}")
        await context.bot.send_message(chat_id=user_id, text="Ocurrió un error al manejar el consentimiento grupal.")
        return ConversationHandler.END

