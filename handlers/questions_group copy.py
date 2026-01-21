import logging
import os
import uuid
import random
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from forms import *

logger = logging.getLogger(__name__)

async def start_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        user_id = update.effective_user.id
    elif update.message:
        user_id = update.effective_user.id
    else:
        logger.error("No se pudo obtener el ID del usuario en start_questions.")
        return ConversationHandler.END

    context.user_data['current_question_index'] = 0
    context.user_data['waiting_for_decision'] = False

    # Obtener todas las preguntas de selección múltiple y abiertas de tipo "grupal" o "ambos"
    multiple_choice_questions = list(preguntas_seleccion_multiple_collection.find({
        "$or": [{"tipo_tarea": "grupal"}, {"tipo_tarea": "ambos"}]
    }))
    open_questions = list(preguntas_abiertas_collection.find({
        "$or": [{"tipo_tarea": "grupal"}, {"tipo_tarea": "ambos"}]
    }))

    # Marcar tipo de pregunta
    for q in multiple_choice_questions:
        q['tipo_pregunta'] = 'seleccion_multiple'
    for q in open_questions:
        q['tipo_pregunta'] = 'abierta'

    # Agrupar preguntas abiertas por el identificador de grupo
    open_questions_groups = {}
    for question in open_questions:
        group_key = question['pregunta_id'].split('.')[0]
        if group_key not in open_questions_groups:
            open_questions_groups[group_key] = []
        open_questions_groups[group_key].append(question)

    # Primera pregunta obligatoria (G-1.n)
    mandatory_group = open_questions_groups.pop('G-1', None)
    if not mandatory_group:
        logger.error("No se encontraron preguntas del grupo G-1.")
        return ConversationHandler.END

    # Selección de tres grupos aleatorios adicionales excluyendo G-1
    available_groups = list(open_questions_groups.keys())
    if len(available_groups) < 3:
        logger.error("No hay suficientes grupos de preguntas abiertas para seleccionar tres grupos.")
        return ConversationHandler.END

    selected_groups_keys = random.sample(available_groups, 3)
    selected_open_questions = []
    for group_key in selected_groups_keys:
        selected_open_questions.extend(open_questions_groups[group_key])

    # Marcar tipo de pregunta
    for question in selected_open_questions:
        question['tipo_pregunta'] = 'abierta'

    # Crear la secuencia final de preguntas, colocando la pregunta obligatoria primero
    questions = []
    questions.extend(multiple_choice_questions[:3])
    questions.extend(mandatory_group)  # Añadir las preguntas del grupo G-1 como primeras
    questions.extend(selected_open_questions)  # Añadir los tres grupos aleatorios
    questions.extend(multiple_choice_questions[3:])

    context.user_data['questions'] = questions

    logger.info(f"Total de preguntas cargadas: {len(context.user_data['questions'])}")

    return await ask_next_question(update, context)


async def handle_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id

        # Check if bot is waiting for a decision after an audio was sent
        if context.user_data.get('waiting_for_decision', False):
            await context.bot.send_message(chat_id=chat_id, text="\u2753 Por favor, elijan si desean enviar otro audio o continuar antes de grabar un nuevo audio.")
            return PREGUNTAS_GRUPAL

        if update.callback_query:
            query = update.callback_query
            user_id = update.effective_user.id
            await query.answer()
            respuesta = query.data

            if respuesta.startswith("opcion_"):
                opcion = respuesta.split("_", 1)[1]
                respuesta_id = str(uuid.uuid4())
                respuestas_collection.insert_one({
                    'respuesta_id': respuesta_id,
                    'pregunta_id': context.user_data['current_question']['pregunta_id'],
                    'usuario_id': str(user_id),
                    'pareja_id': context.user_data.get('pareja_id'),
                    'respuesta': opcion,
                    'fecha_respuesta': datetime.utcnow()
                })
                await context.bot.send_message(chat_id=chat_id, text="\u2705 ¡Gracias! Tu respuesta ha sido registrada con éxito.")
            else:
                await context.bot.send_message(chat_id=chat_id, text="\u2753 Selecciona una opción válida de la lista.")
                return PREGUNTAS_GRUPAL

        elif update.message:
            user_id = update.effective_user.id

            if context.user_data['current_question'].get('tipo_pregunta') == 'abierta':
                if update.message.voice:
                    # Set waiting for decision to True
                    context.user_data['waiting_for_decision'] = True

                    file = await update.message.voice.get_file()
                    file_path = f"audios/{user_id}_{context.user_data['current_question']['pregunta_id']}_{uuid.uuid4()}.ogg"
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    await file.download_to_drive(file_path)
                    respuestas_collection.insert_one({
                        'respuesta_id': str(uuid.uuid4()),
                        'pregunta_id': context.user_data['current_question']['pregunta_id'],
                        'usuario_id': str(user_id),
                        'pareja_id': context.user_data.get('pareja_id'),
                        'respuesta': file_path,
                        'fecha_respuesta': datetime.utcnow()
                    })
                    await context.bot.send_message(chat_id=chat_id, text="\u2705 Respuesta registrada.")
                    keyboard = [
                        [InlineKeyboardButton("Enviar otro audio", callback_data='enviar_otro_audio')],
                        [InlineKeyboardButton("Continuar", callback_data='continuar')]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await context.bot.send_message(chat_id=chat_id, text="¿Desean enviar otro audio o continuar con la siguiente pregunta?", reply_markup=reply_markup)
                    return PREGUNTAS_GRUPAL
                else:
                    await context.bot.send_message(chat_id=chat_id, text="\u2753 Por favor, envíen una nota de voz como respuesta.")
                    return PREGUNTAS_GRUPAL

        # Advance to next question
        context.user_data['current_question_index'] += 1
        return await ask_next_question(update, context)

    except Exception as e:
        if update.callback_query:
            chat_id = update.callback_query.message.chat.id
        elif update.message:
            chat_id = update.message.chat.id
        else:
            chat_id = None

        if chat_id:
            logger.error(f"Error en handle_questions: {e}")
            await context.bot.send_message(chat_id=chat_id, text="Ocurrió un error al procesar su respuesta. Inténtelo de nuevo.")
        else:
            logger.error(f"Error en handle_questions: {e} - No se pudo determinar el chat_id.")

        return PREGUNTAS_GRUPAL

async def handle_additional_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    chat_id = query.message.chat.id

    if query.data == 'enviar_otro_audio':
        # Set waiting for decision to False, allowing the user to send another audio
        context.user_data['waiting_for_decision'] = False
        await context.bot.send_message(chat_id=chat_id, text="Por favor, graben otro audio para esta misma pregunta.")
    elif query.data == 'continuar':
        # Set waiting for decision to False, allowing to move to the next question
        context.user_data['waiting_for_decision'] = False
        context.user_data['current_question_index'] += 1
        return await ask_next_question(update, context)

    return PREGUNTAS_GRUPAL

async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data.get('current_question_index', 0)
    if index < len(context.user_data.get('questions', [])):
        question = context.user_data['questions'][index]
        context.user_data['current_question'] = question

        chat_id = update.effective_chat.id

        if question.get('tipo_pregunta') == 'seleccion_multiple':
            options = question.get('opciones', [])
            if not options:
                await context.bot.send_message(chat_id=chat_id, text="No hay opciones disponibles para esta pregunta.")
                context.user_data['current_question_index'] += 1
                return await ask_next_question(update, context)

            keyboard = [[InlineKeyboardButton(opcion, callback_data=f"opcion_{opcion}")] for opcion in options]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=chat_id,
                text="\U0001F4AC {0}\nSeleccionen una de las siguientes opciones:".format(question['pregunta']),
                reply_markup=reply_markup
            )
            return PREGUNTAS_GRUPAL

        elif question.get('tipo_pregunta') == 'abierta':
            # Mensaje simple indicando que es una pregunta de voz
            await context.bot.send_message(
                chat_id=chat_id,
                text="Esta es una pregunta de voz:"
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text="\U0001F5E3 {0}".format(question['pregunta'])
            )
            return PREGUNTAS_GRUPAL

    else:
        chat_id = update.effective_chat.id
        keyboard = [
            [InlineKeyboardButton("\U0001F501 Volver a empezar", callback_data='restart')],
            [InlineKeyboardButton("\U0001F6AA Salir", callback_data='exit')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=chat_id,
            text="\U0001F44D ¡Gracias por completar el cuestionario!\nSi desean volver a empezar, seleccionen una opción a continuación:",
            reply_markup=reply_markup
        )
        return PREGUNTAS_GRUPAL

