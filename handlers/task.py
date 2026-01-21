from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from datetime import datetime
from forms import TIPO_TAREA, tareas_collection
from handlers import consent_individual, consent_group
import logging

logger = logging.getLogger(__name__)

async def start_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Mensaje de bienvenida personalizado sin emojis visuales
        welcome_message = (
            "¡Hola! Bienvenido al bot de documentación de la diversidad lingüística de las Islas Canarias. "
            "Queremos ayudarte a preservar y compartir las particularidades y riquezas de nuestro idioma. "
            "Para empezar, selecciona el tipo de tarea que quieres realizar:"
        )
        
        keyboard = [
            [InlineKeyboardButton("\U0001F9CD Tarea Individual", callback_data='tarea_individual')],
            [InlineKeyboardButton("\U0001F46A Tarea Grupal", callback_data='tarea_grupal')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Manejo de posibles contextos (mensaje normal o consulta)
        if update.message:
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.message.reply_text(welcome_message, reply_markup=reply_markup)
            
        return TIPO_TAREA
    except Exception as e:
        logger.error(f"Error en start_task: {e}")
        if update.message:
            await update.message.reply_text("\U0000274C Ha ocurrido un error al intentar seleccionar la tarea. Por favor, intenta de nuevo.")
        elif update.callback_query:
            await update.callback_query.message.reply_text("\U0000274C Ha ocurrido un error al intentar seleccionar la tarea. Por favor, intenta de nuevo.")
        return ConversationHandler.END

async def handle_task_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        task_type = query.data

        if task_type not in ['tarea_individual', 'tarea_grupal']:
            await query.edit_message_text("\U000026A0 Selección no válida. Por favor, elige una opción válida: \U0001F9CD Tarea Individual o \U0001F46A Tarea Grupal.")
            return TIPO_TAREA

        tipo_tarea = 'individual' if task_type == 'tarea_individual' else 'grupal'
        tareas_collection.insert_one({
            'usuario_id': str(user_id),
            'tipo_tarea': tipo_tarea,
            'fecha_seleccion': datetime.utcnow()
        })

        # Mensaje de confirmación de selección
        if tipo_tarea == 'individual':
            selected_task_message = "\U00002705 Has elegido una Tarea Individual. Vamos a comenzar a recoger esos detalles únicos del habla canaria."
            logger.info("Redirigiendo a consentimiento individual")
            await query.edit_message_text(selected_task_message)

            # Llamada al siguiente paso para tarea individual
            return await consent_individual.show_consent_individual(context, user_id=user_id)

        else:
            selected_task_message = "\U00002705 Has elegido una Tarea Grupal. ¡Qué bien! Será genial ver cómo se desarrolla el trabajo en grupo para reflejar la diversidad del lenguaje en nuestras islas."
            logger.info("Redirigiendo a consentimiento grupal")
            await query.edit_message_text(selected_task_message)

            # Llamada al siguiente paso para tarea grupal
            return await consent_group.show_consent_group(context, user_id=user_id)

    except Exception as e:
        logger.error(f"Error en handle_task_selection: {e}")
        if update.callback_query:
            await update.callback_query.message.reply_text("\U0000274C Ha ocurrido un error al procesar tu selección. Volvamos a intentarlo desde el principio.")
        return await start_task(update, context)

