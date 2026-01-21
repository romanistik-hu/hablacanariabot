import logging
import os
import uuid
from datetime import datetime
import random
from itertools import groupby

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from forms import *

logger = logging.getLogger(__name__)

import random
from itertools import groupby

async def start_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not user_id:
        logger.error("No se pudo obtener el ID del usuario en start_questions.")
        return ConversationHandler.END

    context.user_data['current_question_index'] = 0
    context.user_data['waiting_for_decision'] = False

    # Selección aleatoria de preguntas de selección múltiple y abiertas
    multiple_choice_questions = list(preguntas_seleccion_multiple_collection.aggregate([
        {"$match": {"$or": [{"tipo_tarea": "individual"}, {"tipo_tarea": "ambos"}]}},
        {"$sample": {"size": 15}}
    ]))

    open_questions = list(preguntas_abiertas_collection.find({
        "$or": [{"tipo_tarea": "individual"}, {"tipo_tarea": "ambos"}]
    }))

    # Agrupar preguntas abiertas por el identificador de grupo
    open_questions_groups = {}
    for question in open_questions:
        group_key = question['pregunta_id'].split('.')[0]
        if group_key not in open_questions_groups:
            open_questions_groups[group_key] = []
        open_questions_groups[group_key].append(question)

    # Selección aleatoria de grupos de preguntas abiertas
    selected_groups_keys = random.sample(open_questions_groups.keys(), min(7, len(open_questions_groups)))
    selected_open_questions = []
    for group_key in selected_groups_keys:
        group_questions = open_questions_groups[group_key]
        selected_open_questions.extend(group_questions)

    # Marcar tipo de pregunta
    for question in multiple_choice_questions:
        question['tipo_pregunta'] = 'seleccion_multiple'
    for question in selected_open_questions:
        question['tipo_pregunta'] = 'abierta'

    # Intercalar las preguntas de acuerdo a la secuencia requerida para 7 grupos
    questions = []
    mc_index = 0
    open_index = 0
    
    # Calcular tamaños de cada grupo
    group_sizes = [len(open_questions_groups[key]) for key in selected_groups_keys]
    
    # Distribución intercalada para 7 grupos:
    # MC(3) → Open(1) → MC(2) → Open(2) → MC(2) → Open(3) → MC(2) → Open(4) → MC(2) → Open(5) → MC(2) → Open(6) → MC(2) → Open(7)
    
    questions.extend(multiple_choice_questions[mc_index:mc_index+3])  # MC: 0-2
    mc_index += 3
    
    # Grupo 1
    questions.extend(selected_open_questions[open_index:open_index+group_sizes[0]])
    open_index += group_sizes[0]
    
    questions.extend(multiple_choice_questions[mc_index:mc_index+2])  # MC: 3-4
    mc_index += 2
    
    # Grupo 2
    questions.extend(selected_open_questions[open_index:open_index+group_sizes[1]])
    open_index += group_sizes[1]
    
    questions.extend(multiple_choice_questions[mc_index:mc_index+2])  # MC: 5-6
    mc_index += 2
    
    # Grupo 3
    questions.extend(selected_open_questions[open_index:open_index+group_sizes[2]])
    open_index += group_sizes[2]
    
    questions.extend(multiple_choice_questions[mc_index:mc_index+2])  # MC: 7-8
    mc_index += 2
    
    # Grupo 4
    questions.extend(selected_open_questions[open_index:open_index+group_sizes[3]])
    open_index += group_sizes[3]
    
    questions.extend(multiple_choice_questions[mc_index:mc_index+2])  # MC: 9-10
    mc_index += 2
    
    # Grupo 5
    questions.extend(selected_open_questions[open_index:open_index+group_sizes[4]])
    open_index += group_sizes[4]
    
    questions.extend(multiple_choice_questions[mc_index:mc_index+2])  # MC: 11-12
    mc_index += 2
    
    # Grupo 6
    questions.extend(selected_open_questions[open_index:open_index+group_sizes[5]])
    open_index += group_sizes[5]
    
    questions.extend(multiple_choice_questions[mc_index:mc_index+2])  # MC: 13-14
    mc_index += 2
    
    # Grupo 7
    questions.extend(selected_open_questions[open_index:open_index+group_sizes[6]])

    context.user_data['questions'] = questions

    logger.info(f"Total de preguntas cargadas: {len(context.user_data['questions'])}")

    return await ask_next_question(update, context)

async def handle_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id

        if context.user_data.get('waiting_for_decision', False):
            return PREGUNTAS_INDIVIDUAL

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
                    'pareja_id': None,
                    'respuesta': opcion,
                    'fecha_respuesta': datetime.utcnow()
                })
                await query.edit_message_reply_markup(reply_markup=None)
                await context.bot.send_message(chat_id=chat_id, text="\u2705 Respuesta registrada.")
            elif respuesta == 'enviar_otro_audio':
                context.user_data['waiting_for_decision'] = False
                await query.edit_message_reply_markup(reply_markup=None)
                await context.bot.send_message(chat_id=chat_id, text="Graba otro audio.")
            elif respuesta == 'continuar':
                context.user_data['waiting_for_decision'] = False
                await query.edit_message_reply_markup(reply_markup=None)
                context.user_data['current_question_index'] += 1
                return await ask_next_question(update, context)
            else:
                await context.bot.send_message(chat_id=chat_id, text="Selecciona una opción válida de la lista.")
                return PREGUNTAS_INDIVIDUAL

        elif update.message:
            user_id = update.effective_user.id

            if context.user_data['current_question'].get('tipo_pregunta') == 'abierta':
                if update.message.voice:
                    try:
                        context.user_data['waiting_for_decision'] = True

                        file = await update.message.voice.get_file()
                        file_path = f"audios/{user_id}_{context.user_data['current_question']['pregunta_id']}_{uuid.uuid4()}.ogg"
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        await file.download_to_drive(file_path)

                        # Insertar la respuesta en la colección
                        respuestas_collection.insert_one({
                            'respuesta_id': str(uuid.uuid4()),
                            'pregunta_id': context.user_data['current_question']['pregunta_id'],
                            'usuario_id': str(user_id),
                            'pareja_id': None,
                            'respuesta': file_path,
                            'fecha_respuesta': datetime.utcnow()
                        })

                        # Enviar confirmación
                        await context.bot.send_message(chat_id=chat_id, text="\u2705 Respuesta guardada")

                        # Teclado de opciones para continuar o grabar otro audio
                        keyboard = [
                            [InlineKeyboardButton("Enviar otro audio", callback_data='enviar_otro_audio')],
                            [InlineKeyboardButton("Continuar", callback_data='continuar')]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await context.bot.send_message(chat_id=chat_id, text="¿Deseas enviar otro audio o continuar con la siguiente pregunta?", reply_markup=reply_markup)

                    except Exception as e:
                        logger.error(f"Error al manejar el archivo de voz: {e}")
                        await context.bot.send_message(chat_id=chat_id, text="Ocurrió un error al procesar tu nota de voz. Inténtalo de nuevo.")
                    
                    return PREGUNTAS_INDIVIDUAL
                else:
                    await context.bot.send_message(chat_id=chat_id, text="Por favor, envía una nota de voz como respuesta.")
                    return PREGUNTAS_INDIVIDUAL

        context.user_data['current_question_index'] += 1
        return await ask_next_question(update, context)

    except Exception as e:
        chat_id = update.callback_query.message.chat.id if update.callback_query else update.message.chat.id if update.message else None
        if chat_id:
            logger.error(f"Error en handle_questions: {e}")
            await context.bot.send_message(chat_id=chat_id, text="Ocurrió un error al procesar tu respuesta. Inténtalo de nuevo.")
        else:
            logger.error(f"Error en handle_questions: {e} - No se pudo determinar el chat_id.")

        return PREGUNTAS_INDIVIDUAL

async def handle_additional_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    chat_id = query.message.chat.id

    if query.data == 'enviar_otro_audio':
        # Set waiting for decision to False, allowing the user to send another audio
        context.user_data['waiting_for_decision'] = False
        await context.bot.send_message(chat_id=chat_id, text="Por favor, graba otro audio.")
    elif query.data == 'continuar':
        # Set waiting for decision to False, allowing to move to the next question
        context.user_data['waiting_for_decision'] = False
        context.user_data['current_question_index'] += 1
        return await ask_next_question(update, context)

    return PREGUNTAS_INDIVIDUAL
    
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
                text="\U0001F4AC {0}".format(question['pregunta']),
                reply_markup=reply_markup
            )
            return PREGUNTAS_INDIVIDUAL

        elif question.get('tipo_pregunta') == 'abierta':
            await context.bot.send_message(
                chat_id=chat_id,
                text="Esta es una pregunta de voz:"
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text="\U0001F5E3 {0}".format(question['pregunta'])
            )
            return PREGUNTAS_INDIVIDUAL

    else:
        chat_id = update.effective_chat.id
        keyboard = [
            [InlineKeyboardButton("\U0001F501 Volver a empezar", callback_data='restart')],
            [InlineKeyboardButton("\U0001F6AA Salir", callback_data='exit')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=chat_id,
            text="\U0001F44D ¡Gracias por completar el cuestionario!\nSi deseas volver a empezar, selecciona una opción a continuación:",
            reply_markup=reply_markup
        )
        return PREGUNTAS_INDIVIDUAL


async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    await context.bot.send_message(chat_id=chat_id, text="Empezamos de nuevo desde el principio.")
    return TIPO_TAREA
