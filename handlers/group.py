# group.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from forms import *
import logging
import uuid
from datetime import datetime
from handlers.questions_group import start_questions
import re
import random

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Configuración interna para manejo de ubicaciones geográficas en grupos
_LOCATION_CONFIG = {
    'nacimiento': {
        'states': {
            'country_selection_1': PAIS_NACIMIENTO_PARTICIPANTE_1_SELECTION,
            'country_selection_2': PAIS_NACIMIENTO_PARTICIPANTE_2_SELECTION,
            'country_input_1': PAIS_NACIMIENTO_PARTICIPANTE_1_INPUT,
            'country_input_2': PAIS_NACIMIENTO_PARTICIPANTE_2_INPUT,
            'province_selection_1': PROVINCIA_NACIMIENTO_PARTICIPANTE_1_SELECTION,
            'province_selection_2': PROVINCIA_NACIMIENTO_PARTICIPANTE_2_SELECTION,
            'province_input_1': PROVINCIA_NACIMIENTO_PARTICIPANTE_1_INPUT,
            'province_input_2': PROVINCIA_NACIMIENTO_PARTICIPANTE_2_INPUT,
            'municipio_input_1': MUNICIPIO_NACIMIENTO_PARTICIPANTE_1_INPUT,
            'municipio_input_2': MUNICIPIO_NACIMIENTO_PARTICIPANTE_2_INPUT
        },
        'data_keys': {
            'country_1': 'pais_nacimiento_participante_1',
            'country_2': 'pais_nacimiento_participante_2',
            'province_1': 'provincia_nacimiento_participante_1',
            'province_2': 'provincia_nacimiento_participante_2',
            'municipio_1': 'municipio_nacimiento_participante_1',
            'municipio_2': 'municipio_nacimiento_participante_2'
        },
        'messages': {
            'country_question': '\U0001F30D ¿En qué país naciste?',
            'province_question': '¿En qué provincia naciste?',
            'municipio_question': '¿En qué municipio naciste?'
        },
        'next_flow': 'crianza'
    },
    'crianza': {
        'states': {
            'country_selection_1': PAIS_CRIANZA_PARTICIPANTE_1_SELECTION,
            'country_selection_2': PAIS_CRIANZA_PARTICIPANTE_2_SELECTION,
            'country_input_1': PAIS_CRIANZA_PARTICIPANTE_1_INPUT,
            'country_input_2': PAIS_CRIANZA_PARTICIPANTE_2_INPUT,
            'province_selection_1': PROVINCIA_CRIANZA_PARTICIPANTE_1_SELECTION,
            'province_selection_2': PROVINCIA_CRIANZA_PARTICIPANTE_2_SELECTION,
            'province_input_1': PROVINCIA_CRIANZA_PARTICIPANTE_1_INPUT,
            'province_input_2': PROVINCIA_CRIANZA_PARTICIPANTE_2_INPUT,
            'municipio_input_1': MUNICIPIO_CRIANZA_PARTICIPANTE_1_INPUT,
            'municipio_input_2': MUNICIPIO_CRIANZA_PARTICIPANTE_2_INPUT
        },
        'data_keys': {
            'country_1': 'pais_crianza_participante_1',
            'country_2': 'pais_crianza_participante_2',
            'province_1': 'provincia_crianza_participante_1',
            'province_2': 'provincia_crianza_participante_2',
            'municipio_1': 'municipio_crianza_participante_1',
            'municipio_2': 'municipio_crianza_participante_2'
        },
        'messages': {
            'country_question': '\U0001F30E ¿En qué país creciste?',
            'province_question': '¿En qué provincia creciste?',
            'municipio_question': '¿En qué municipio creciste?'
        },
        'next_flow': 'residencia'
    },
    'residencia': {
        'states': {
            'country_selection_1': PAIS_RESIDENCIA_PARTICIPANTE_1_SELECTION,
            'country_selection_2': PAIS_RESIDENCIA_PARTICIPANTE_2_SELECTION,
            'country_input_1': PAIS_RESIDENCIA_PARTICIPANTE_1_INPUT,
            'country_input_2': PAIS_RESIDENCIA_PARTICIPANTE_2_INPUT,
            'province_selection_1': PROVINCIA_RESIDENCIA_PARTICIPANTE_1_SELECTION,
            'province_selection_2': PROVINCIA_RESIDENCIA_PARTICIPANTE_2_SELECTION,
            'province_input_1': PROVINCIA_RESIDENCIA_PARTICIPANTE_1_INPUT,
            'province_input_2': PROVINCIA_RESIDENCIA_PARTICIPANTE_2_INPUT,
            'municipio_input_1': MUNICIPIO_RESIDENCIA_PARTICIPANTE_1_INPUT,
            'municipio_input_2': MUNICIPIO_RESIDENCIA_PARTICIPANTE_2_INPUT
        },
        'data_keys': {
            'country_1': 'pais_residencia_participante_1',
            'country_2': 'pais_residencia_participante_2',
            'province_1': 'provincia_residencia_participante_1',
            'province_2': 'provincia_residencia_participante_2',
            'municipio_1': 'municipio_residencia_participante_1',
            'municipio_2': 'municipio_residencia_participante_2'
        },
        'messages': {
            'country_question': '\U0001F30F ¿En qué país vives actualmente?',
            'province_question': '¿En qué provincia vives actualmente?',
            'municipio_question': '¿En qué municipio vives actualmente?'
        },
        'next_flow': 'tiempo_residencia'
    }
}

# ============================================================================
# FUNCIONES GENÉRICAS INTERNAS PARA MANEJO DE UBICACIONES GEOGRÁFICAS
# ============================================================================

async def _handle_country_generic(update, context, context_type, participant_number):
    """
    Función genérica interna para manejar la selección de país.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
        participant_number: Número del participante (1 o 2)
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        config = _LOCATION_CONFIG[context_type]
        
        keyboard = [
            [InlineKeyboardButton("\U0001F1EA\U0001F1F8 España", callback_data='espana')],
            [InlineKeyboardButton("\U0001F310 Otro", callback_data='otro_pais')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            config['messages']['country_question'], 
            reply_markup=reply_markup
        )
        return config['states'][f'country_selection_{participant_number}']
        
    except Exception as e:
        logger.error(f"Error en _handle_country_generic para {context_type} participante {participant_number}: {e}")
        await update.message.reply_text("Ocurrió un error al procesar tu selección.")
        return ConversationHandler.END

async def _handle_country_selection_generic(update, context, context_type, participant_number):
    """
    Función genérica interna para manejar la selección de país.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
        participant_number: Número del participante (1 o 2)
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        query = update.callback_query
        await query.answer()
        pais = query.data
        config = _LOCATION_CONFIG[context_type]
        
        if pais == 'otro_pais':
            await query.edit_message_text("Por favor, escribe el nombre de tu país:")
            return config['states'][f'country_input_{participant_number}']
        else:
            context.user_data[config['data_keys'][f'country_{participant_number}']] = 'España'
            await query.edit_message_text("\U00002705 Has seleccionado: España.")
            return await _handle_province_generic(update, context, context_type, participant_number)
            
    except Exception as e:
        logger.error(f"Error en _handle_country_selection_generic para {context_type} participante {participant_number}: {e}")
        await context.bot.send_message(chat_id=query.from_user.id, text="Ocurrió un error al procesar tu selección.")
        return ConversationHandler.END

async def _handle_country_input_generic(update, context, context_type, participant_number):
    """
    Función genérica interna para manejar la entrada manual de país.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
        participant_number: Número del participante (1 o 2)
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        config = _LOCATION_CONFIG[context_type]
        context.user_data[config['data_keys'][f'country_{participant_number}']] = update.message.text
        return await _handle_province_generic(update, context, context_type, participant_number)
        
    except Exception as e:
        logger.error(f"Error en _handle_country_input_generic para {context_type} participante {participant_number}: {e}")
        await update.message.reply_text("Ocurrió un error al registrar tu país. Inténtalo de nuevo.")
        return ConversationHandler.END

async def _handle_province_generic(update, context, context_type, participant_number):
    """
    Función genérica interna para manejar la selección de provincia.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
        participant_number: Número del participante (1 o 2)
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        config = _LOCATION_CONFIG[context_type]
        
        if context.user_data.get(config['data_keys'][f'country_{participant_number}']) == 'España':
            keyboard = [
                [InlineKeyboardButton("Santa Cruz de Tenerife", callback_data='tenerife')],
                [InlineKeyboardButton("Las Palmas", callback_data='las_palmas')],
                [InlineKeyboardButton("Otra", callback_data='otra_provincia')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.message:
                await update.message.reply_text(config['messages']['province_question'], reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.message.reply_text(config['messages']['province_question'], reply_markup=reply_markup)
            
            return config['states'][f'province_selection_{participant_number}']
        else:
            if update.message:
                await update.message.reply_text("Por favor, escribe el nombre de tu provincia:")
            elif update.callback_query:
                await update.callback_query.message.reply_text("Por favor, escribe el nombre de tu provincia:")
            
            return config['states'][f'province_input_{participant_number}']
            
    except Exception as e:
        logger.error(f"Error en _handle_province_generic para {context_type} participante {participant_number}: {e}")
        await update.message.reply_text("Ocurrió un error al procesar tu selección.")
        return ConversationHandler.END

async def _handle_province_selection_generic(update, context, context_type, participant_number):
    """
    Función genérica interna para manejar la selección de provincia.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
        participant_number: Número del participante (1 o 2)
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        query = update.callback_query
        await query.answer()
        provincia = query.data
        config = _LOCATION_CONFIG[context_type]
        
        provincias_display = {
            'tenerife': 'Santa Cruz de Tenerife',
            'las_palmas': 'Las Palmas',
            'otra_provincia': 'Otra'
        }
        
        if provincia == 'otra_provincia':
            await query.edit_message_text("Por favor, escribe el nombre de tu provincia:")
            return config['states'][f'province_input_{participant_number}']
        else:
            provincia_display = provincias_display.get(provincia, provincia)
            context.user_data[config['data_keys'][f'province_{participant_number}']] = provincia_display
            await query.edit_message_text(f"\U00002705 Has seleccionado: {provincia_display}.")
            await context.bot.send_message(chat_id=query.from_user.id, text=config['messages']['municipio_question'])
            return config['states'][f'municipio_input_{participant_number}']
            
    except Exception as e:
        logger.error(f"Error en _handle_province_selection_generic para {context_type} participante {participant_number}: {e}")
        await context.bot.send_message(chat_id=query.from_user.id, text="Ocurrió un error al procesar tu selección.")
        return ConversationHandler.END

async def _handle_province_input_generic(update, context, context_type, participant_number):
    """
    Función genérica interna para manejar la entrada manual de provincia.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
        participant_number: Número del participante (1 o 2)
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        config = _LOCATION_CONFIG[context_type]
        context.user_data[config['data_keys'][f'province_{participant_number}']] = update.message.text
        await update.message.reply_text(config['messages']['municipio_question'])
        return config['states'][f'municipio_input_{participant_number}']
        
    except Exception as e:
        logger.error(f"Error en _handle_province_input_generic para {context_type} participante {participant_number}: {e}")
        await update.message.reply_text("Ocurrió un error al registrar tu provincia. Inténtalo de nuevo.")
        return ConversationHandler.END

async def _handle_municipio_generic(update, context, context_type, participant_number):
    """
    Función genérica interna para manejar la entrada de municipio.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
        participant_number: Número del participante (1 o 2)
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        config = _LOCATION_CONFIG[context_type]
        context.user_data[config['data_keys'][f'municipio_{participant_number}']] = update.message.text
        
        # Determinar el siguiente flujo basado en el contexto
        if context_type == 'nacimiento':
            return await _handle_country_generic(update, context, 'crianza', participant_number)
        elif context_type == 'crianza':
            return await _handle_country_generic(update, context, 'residencia', participant_number)
        elif context_type == 'residencia':
            # Para residencia, mostrar menú de tiempo de residencia
            keyboard = [
                [InlineKeyboardButton("\U0001F4A1 Toda la vida", callback_data='toda_la_vida')],
                [InlineKeyboardButton("\U0001F553 Más de 5 años", callback_data='mas_de_5')],
                [InlineKeyboardButton("\U0001F551 Entre 3 y 5 años", callback_data='entre_3_y_5')],
                [InlineKeyboardButton("\U0001F550 Entre 1 y 3 años", callback_data='entre_1_y_3')],
                [InlineKeyboardButton("\U0001F55C Menos de un año", callback_data='menos_de_1')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("¿Cuánto tiempo has vivido en tu lugar de residencia actual?", reply_markup=reply_markup)
            return TIEMPO_RESIDENCIA_PARTICIPANTE_1 if participant_number == 1 else TIEMPO_RESIDENCIA_PARTICIPANTE_2
        else:
            logger.error(f"Contexto de ubicación desconocido: {context_type}")
            return ConversationHandler.END
            
    except Exception as e:
        logger.error(f"Error en _handle_municipio_generic para {context_type} participante {participant_number}: {e}")
        await update.message.reply_text("Ocurrió un error al registrar tu municipio. Inténtalo de nuevo.")
        return ConversationHandler.END

async def start_group_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['participant_number'] = 1
        context.user_data['pareja_id'] = str(uuid.uuid4())

        chat_id = update.message.chat_id if update.message else update.callback_query.from_user.id
        await context.bot.send_message(chat_id=chat_id, text=f"Se ha creado un ID de pareja único: {context.user_data['pareja_id']}")
        
        return await papel_participante(update, context)

    except Exception as e:
        logger.error(f"Error en start_group_registration: {e}")
        chat_id = update.message.chat_id if update.message else update.callback_query.from_user.id
        await context.bot.send_message(chat_id=chat_id, text="Ocurrió un error al iniciar el registro grupal.")
        return ConversationHandler.END

async def papel_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    participant_number = context.user_data.get('participant_number', 1)

    keyboard = [
        [InlineKeyboardButton("\U0001F393 Estudiante", callback_data='papel_estudiante')],
        [InlineKeyboardButton("\U0001F3EB Profesor", callback_data='papel_profesor')],
        [InlineKeyboardButton("\U0001F52C Investigador", callback_data='papel_investigador')],
        [InlineKeyboardButton("\U0001F464 Otro", callback_data='papel_otro')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    chat_id = update.message.chat_id if update.message else update.callback_query.from_user.id
    await context.bot.send_message(chat_id=chat_id, text=f"Participante {participant_number}, por favor, selecciona tu papel:", reply_markup=reply_markup)
    
    return PAPEL_PARTICIPANTE_1 if participant_number == 1 else PAPEL_PARTICIPANTE_2

async def handle_papel_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        decision = query.data
        participant_number = context.user_data['participant_number']

        if decision == 'papel_otro':
            await query.edit_message_text("\U00002753 Por favor, especifica tu papel:")
            return OTRO_PAPEL_PARTICIPANTE_1 if participant_number == 1 else OTRO_PAPEL_PARTICIPANTE_2
        else:
            papel_map = {
                'papel_estudiante': 'Estudiante',
                'papel_profesor': 'Docente',
                'papel_investigador': 'Investigador(a)'
            }
            context.user_data[f'papel_participante_{participant_number}'] = papel_map.get(decision, 'Otro')
            await query.edit_message_text(f"\U00002705 Has seleccionado: {context.user_data[f'papel_participante_{participant_number}']}.")
            await context.bot.send_message(chat_id=query.from_user.id, text="\U0001F4E7 Por favor, proporciona tu correo electrónico:")
            return EMAIL_PARTICIPANTE_1 if participant_number == 1 else EMAIL_PARTICIPANTE_2

    except Exception as e:
        logger.error(f"Error en handle_papel_participante: {e}")
        await context.bot.send_message(chat_id=query.from_user.id, text="Ocurrió un error al manejar la selección del papel del participante.")
        return ConversationHandler.END

async def otro_papel_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    participant_number = context.user_data['participant_number']
    context.user_data[f'papel_participante_{participant_number}'] = update.message.text
    await update.message.reply_text("\U0001F4E7 Por favor, proporciona tu correo electrónico:", reply_markup=ReplyKeyboardRemove())
    return EMAIL_PARTICIPANTE_1 if participant_number == 1 else EMAIL_PARTICIPANTE_2

async def email_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    participant_number = context.user_data['participant_number']
    email_text = update.message.text

    if EMAIL_REGEX.match(email_text):
        context.user_data[f'email_participante_{participant_number}'] = email_text
        await update.message.reply_text("\U0001F464 ¿Cuál es tu nombre?", reply_markup=ReplyKeyboardRemove())
        return NOMBRE_PARTICIPANTE_1 if participant_number == 1 else NOMBRE_PARTICIPANTE_2
    else:
        await update.message.reply_text("El correo electrónico proporcionado no es válido. Por favor, ingresa un correo electrónico válido:")
        return EMAIL_PARTICIPANTE_1 if participant_number == 1 else EMAIL_PARTICIPANTE_2

async def nombre_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    participant_number = context.user_data['participant_number']
    context.user_data[f'nombre_participante_{participant_number}'] = update.message.text
    await update.message.reply_text("\U0001F4C5 ¿En qué año naciste?", reply_markup=ReplyKeyboardRemove())
    return ANIO_NACIMIENTO_PARTICIPANTE_1 if participant_number == 1 else ANIO_NACIMIENTO_PARTICIPANTE_2

async def anio_nacimiento_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        participant_number = context.user_data['participant_number']
        anio_nacimiento = int(update.message.text)
        current_year = datetime.now().year
        age = current_year - anio_nacimiento

        if age < 18:
            await update.message.reply_text("\U000026A0 Debes ser mayor de 18 años. Por favor, introduce un año válido.")
            return ANIO_NACIMIENTO_PARTICIPANTE_1 if participant_number == 1 else ANIO_NACIMIENTO_PARTICIPANTE_2
        if age > 120:
            await update.message.reply_text("\U000026A0 La edad debe estar entre 18 y 120 años. Por favor, introduce un año válido.")
            return ANIO_NACIMIENTO_PARTICIPANTE_1 if participant_number == 1 else ANIO_NACIMIENTO_PARTICIPANTE_2

        context.user_data[f'anio_nacimiento_participante_{participant_number}'] = anio_nacimiento

        keyboard = [
            [InlineKeyboardButton("\U0001F468\u200D\U0001F393 Masculino", callback_data='genero_masculino')],
            [InlineKeyboardButton("\U0001F469\u200D\U0001F393 Femenino", callback_data='genero_femenino')],
            [InlineKeyboardButton("\U0001F9D1 Otro", callback_data='genero_otro')],
            [InlineKeyboardButton("\U0001F636 Prefiero no decirlo", callback_data='genero_prefiero_no_decirlo')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("\U0001F3C3 ¿Cuál es tu género?", reply_markup=reply_markup)
        return GENERO_PARTICIPANTE_1 if participant_number == 1 else GENERO_PARTICIPANTE_2

    except ValueError:
        await update.message.reply_text("\U0001F4A1 Por favor, introduce un año válido (solo números).")
        return ANIO_NACIMIENTO_PARTICIPANTE_1 if participant_number == 1 else ANIO_NACIMIENTO_PARTICIPANTE_2
    except Exception as e:
        logger.error(f"Error en anio_nacimiento_participante: {e}")
        await update.message.reply_text("Ocurrió un error al registrar tu año de nacimiento. Inténtalo de nuevo.")
        return ConversationHandler.END

async def genero_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        decision = query.data

        genero_map = {
            'genero_masculino': 'Masculino',
            'genero_femenino': 'Femenino',
            'genero_otro': 'Otro',
            'genero_prefiero_no_decirlo': 'Prefiero no decirlo'
        }
        genero = genero_map.get(decision, 'Otro')

        participant_number = context.user_data['participant_number']
        context.user_data[f'genero_participante_{participant_number}'] = genero
        await query.edit_message_text(f"Has seleccionado: {genero}.")

        keyboard = [
            [InlineKeyboardButton("\U0001F393 Grado", callback_data='nivel_grado')],
            [InlineKeyboardButton("\U0001F3EB Máster", callback_data='nivel_maestria')],
            [InlineKeyboardButton("\U0001F52C Doctorado", callback_data='nivel_doctorado')],
            [InlineKeyboardButton("\U0001F9D1 Otro", callback_data='nivel_otro')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=query.from_user.id, text="¿Cuál es tu nivel educativo?", reply_markup=reply_markup)
        return NIVEL_EDUCATIVO_PARTICIPANTE_1 if participant_number == 1 else NIVEL_EDUCATIVO_PARTICIPANTE_2

    except Exception as e:
        logger.error(f"Error en genero_participante: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ocurrió un error al procesar tu selección. Por favor, intenta de nuevo.")
        return ConversationHandler.END

async def otro_nivel_educativo_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    participant_number = context.user_data['participant_number']
    context.user_data[f'nivel_educativo_participante_{participant_number}'] = update.message.text
    return await pais_nacimiento_participante(update, context)

async def nivel_educativo_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        decision = query.data

        nivel_educativo_map = {
            'nivel_grado': 'Grado',
            'nivel_maestria': 'Máster',
            'nivel_doctorado': 'Doctorado',
            'nivel_otro': 'Otro'
        }
        nivel_educativo = nivel_educativo_map.get(decision, 'Otro')

        participant_number = context.user_data['participant_number']
        context.user_data[f'nivel_educativo_participante_{participant_number}'] = nivel_educativo
        await query.edit_message_text(f"Has seleccionado: {nivel_educativo}.")

        if nivel_educativo == 'Grado':
            keyboard = [
                [InlineKeyboardButton("1", callback_data='grado_1')],
                [InlineKeyboardButton("2", callback_data='grado_2')],
                [InlineKeyboardButton("3", callback_data='grado_3')],
                [InlineKeyboardButton("4", callback_data='grado_4')],
                [InlineKeyboardButton("Terminado", callback_data='grado_terminado')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=query.from_user.id, text="¿En qué año de Grado estás?", reply_markup=reply_markup)
            return GRADO_ANIO_PARTICIPANTE_1 if participant_number == 1 else GRADO_ANIO_PARTICIPANTE_2

        elif nivel_educativo in ['Máster', 'Doctorado']:
            return await universidad_participante(update, context)

        elif nivel_educativo == 'Otro':
            await context.bot.send_message(chat_id=query.from_user.id, text="Por favor, especifica tu nivel educativo:")
            return OTRO_NIVEL_EDUCATIVO_PARTICIPANTE_1 if participant_number == 1 else OTRO_NIVEL_EDUCATIVO_PARTICIPANTE_2

    except Exception as e:
        logger.error(f"Error en nivel_educativo_participante: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ocurrió un error al procesar tu selección. Por favor, intenta de nuevo.")
        return ConversationHandler.END

async def grado_anio_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        grado_anio = query.data.split('_')[1]

        participant_number = context.user_data['participant_number']
        valid_options = ['1', '2', '3', '4', 'terminado']
        if grado_anio in valid_options:
            context.user_data[f'grado_anio_participante_{participant_number}'] = grado_anio
            await query.edit_message_text(f"Has seleccionado el año: {grado_anio}.")
            return await grado_tipo_participante(update, context)
        else:
            await query.edit_message_text("Por favor, selecciona una opción válida.")
            return GRADO_ANIO_PARTICIPANTE_1 if participant_number == 1 else GRADO_ANIO_PARTICIPANTE_2

    except Exception as e:
        logger.error(f"Error en grado_anio_participante: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ocurrió un error al procesar tu selección. Por favor, intenta de nuevo.")
        return ConversationHandler.END

async def grado_tipo_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        participant_number = context.user_data['participant_number']
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🎓 ¿Qué grado estudias o estudiaste? (ej: Ingeniería Informática, Psicología, etc.)"
        )
        return GRADO_TIPO_PARTICIPANTE_1 if participant_number == 1 else GRADO_TIPO_PARTICIPANTE_2
    except Exception as e:
        logger.error(f"Error en grado_tipo_participante: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ocurrió un error. Inténtalo de nuevo.")
        return ConversationHandler.END

async def handle_grado_tipo_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        grado_tipo = update.message.text.strip()
        participant_number = context.user_data['participant_number']
        
        # Validación básica
        if len(grado_tipo) < 2:
            await update.message.reply_text("Por favor, escribe el nombre completo del grado.")
            return GRADO_TIPO_PARTICIPANTE_1 if participant_number == 1 else GRADO_TIPO_PARTICIPANTE_2
        
        context.user_data[f'grado_tipo_participante_{participant_number}'] = grado_tipo
        await update.message.reply_text(f"✅ Grado registrado: {grado_tipo}")
        
        return await universidad_participante(update, context)
        
    except Exception as e:
        logger.error(f"Error en handle_grado_tipo_participante: {e}")
        await update.message.reply_text("Ocurrió un error al registrar el grado. Inténtalo de nuevo.")
        return ConversationHandler.END

async def universidad_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Universidad de La Laguna \U0001F3DD\U0000FE0F", callback_data='ull')],
        [InlineKeyboardButton("Universidad de Las Palmas Gran Canaria \U0001F3DD\U0000FE0F", callback_data='ulpgc')],
        [InlineKeyboardButton("Otra \U0001F30D", callback_data='otra_universidad')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    participant_number = context.user_data['participant_number']

    # Using update.effective_message to handle both update.message and update.callback_query.message
    effective_message = update.effective_message
    if effective_message:
        await effective_message.reply_text("¿A qué universidad perteneces?", reply_markup=reply_markup)

    return UNIVERSIDAD_PARTICIPANTE_1_SELECTION if participant_number == 1 else UNIVERSIDAD_PARTICIPANTE_2_SELECTION

async def universidad_selection_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        universidad = query.data

        participant_number = context.user_data['participant_number']

        if universidad == 'otra_universidad':
            # Solicitar al usuario que escriba el nombre de su universidad
            await query.edit_message_text("Por favor, escribe el nombre de tu universidad:")
            return OTRO_UNIVERSIDAD_PARTICIPANTE_1 if participant_number == 1 else OTRO_UNIVERSIDAD_PARTICIPANTE_2
        else:
            universidad_map = {
                'ull': 'Universidad de La Laguna',
                'ulpgc': 'Universidad de Las Palmas Gran Canaria'
            }
            context.user_data[f'universidad_participante_{participant_number}'] = universidad_map.get(universidad, 'Otra')

            # Confirmar la universidad seleccionada
            await query.edit_message_text(f"\U00002705 Has seleccionado: {context.user_data[f'universidad_participante_{participant_number}']}.")

            # Mostrar opciones para el país de nacimiento con botones de "España" u "Otro"
            keyboard = [
                [InlineKeyboardButton("\U0001F1EA\U0001F1F8 España", callback_data='espana')],
                [InlineKeyboardButton("\U0001F310 Otro", callback_data='otro_pais')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Enviar la pregunta sobre el país de nacimiento
            chat_id = query.message.chat_id if query.message else query.from_user.id
            await context.bot.send_message(chat_id=chat_id, text="\U0001F30D ¿En qué país naciste?", reply_markup=reply_markup)

            return PAIS_NACIMIENTO_PARTICIPANTE_1_SELECTION if participant_number == 1 else PAIS_NACIMIENTO_PARTICIPANTE_2_SELECTION

    except Exception as e:
        logger.error(f"Error en universidad_selection_participante: {e}")
        chat_id = update.effective_chat.id if update.effective_chat else query.from_user.id
        await context.bot.send_message(chat_id=chat_id, text="Ocurrió un error al procesar tu selección. Por favor, intenta de nuevo.")
        return ConversationHandler.END

async def otro_universidad_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    participant_number = context.user_data['participant_number']
    context.user_data[f'universidad_participante_{participant_number}'] = update.message.text
    return await pais_nacimiento_participante(update, context)

async def pais_nacimiento_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para país de nacimiento del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_country_generic(update, context, 'nacimiento', participant_number)

async def pais_nacimiento_participante_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de país de nacimiento del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_country_selection_generic(update, context, 'nacimiento', participant_number)

async def pais_nacimiento_participante_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de país de nacimiento del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_country_input_generic(update, context, 'nacimiento', participant_number)

async def provincia_nacimiento_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para provincia de nacimiento del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_province_generic(update, context, 'nacimiento', participant_number)

async def provincia_nacimiento_participante_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de provincia de nacimiento del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_province_selection_generic(update, context, 'nacimiento', participant_number)

async def provincia_nacimiento_participante_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de provincia de nacimiento del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_province_input_generic(update, context, 'nacimiento', participant_number)

async def municipio_nacimiento_participante_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada de municipio de nacimiento del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_municipio_generic(update, context, 'nacimiento', participant_number)

async def pais_crianza_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para país de crianza del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_country_generic(update, context, 'crianza', participant_number)

async def pais_crianza_participante_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de país de crianza del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_country_selection_generic(update, context, 'crianza', participant_number)

async def pais_crianza_participante_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de país de crianza del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_country_input_generic(update, context, 'crianza', participant_number)

async def provincia_crianza_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para provincia de crianza del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_province_generic(update, context, 'crianza', participant_number)

async def provincia_crianza_participante_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de provincia de crianza del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_province_selection_generic(update, context, 'crianza', participant_number)

async def provincia_crianza_participante_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de provincia de crianza del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_province_input_generic(update, context, 'crianza', participant_number)

async def municipio_crianza_participante_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada de municipio de crianza del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_municipio_generic(update, context, 'crianza', participant_number)

async def pais_residencia_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para país de residencia del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_country_generic(update, context, 'residencia', participant_number)

async def pais_residencia_participante_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de país de residencia del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_country_selection_generic(update, context, 'residencia', participant_number)

async def pais_residencia_participante_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de país de residencia del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_country_input_generic(update, context, 'residencia', participant_number)

async def provincia_residencia_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para provincia de residencia del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_province_generic(update, context, 'residencia', participant_number)

async def provincia_residencia_participante_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de provincia de residencia del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_province_selection_generic(update, context, 'residencia', participant_number)

async def provincia_residencia_participante_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de provincia de residencia del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_province_input_generic(update, context, 'residencia', participant_number)

async def municipio_residencia_participante_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada de municipio de residencia del participante."""
    participant_number = context.user_data['participant_number']
    return await _handle_municipio_generic(update, context, 'residencia', participant_number)

async def tiempo_residencia_participante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        tiempo_residencia_map = {
            'toda_la_vida': 'Toda la vida',
            'mas_de_5': 'Más de 5 años',
            'entre_3_y_5': 'Entre 3 y 5 años',
            'entre_1_y_3': 'Entre 1 y 3 años',
            'menos_de_1': 'Menos de un año'
        }
        tiempo_residencia = tiempo_residencia_map.get(query.data, 'Otro')
        participant_number = context.user_data['participant_number']
        context.user_data[f'tiempo_residencia_participante_{participant_number}'] = tiempo_residencia

        await query.edit_message_text(f"\U00002705 Has seleccionado: {tiempo_residencia}.")

        if participant_number == 1:
            context.user_data['participant_number'] = 2
            await context.bot.send_message(chat_id=query.from_user.id, text="Gracias. Ahora, vamos a recoger los datos del segundo participante.")
            return await papel_participante(update, context)
        else:
            return await save_group_data(update, context)

    except Exception as e:
        logger.error(f"Error en tiempo_residencia_participante: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ocurrió un error al procesar tu selección. Por favor, intenta de nuevo.")
        return ConversationHandler.END

async def save_group_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_data = context.user_data
        participantes_pareja_collection.insert_one({
            "pareja_id": user_data.get('pareja_id', str(uuid.uuid4())),
            "participante_1": {
                "papel": user_data.get('papel_participante_1'),
                "email": user_data.get('email_participante_1'),
                "nombre": user_data.get('nombre_participante_1'),
                "anio_nacimiento": user_data.get('anio_nacimiento_participante_1'),
                "genero": user_data.get('genero_participante_1'),
                "nivel_educativo": user_data.get('nivel_educativo_participante_1'),
                "universidad": user_data.get('universidad_participante_1'),
                "grado_anio": user_data.get('grado_anio_participante_1'),
                "grado_tipo": user_data.get('grado_tipo_participante_1'),
                "pais_nacimiento": user_data.get('pais_nacimiento_participante_1'),
                "provincia_nacimiento": user_data.get('provincia_nacimiento_participante_1'),
                "municipio_nacimiento": user_data.get('municipio_nacimiento_participante_1'),
                "pais_crianza": user_data.get('pais_crianza_participante_1'),
                "provincia_crianza": user_data.get('provincia_crianza_participante_1'),
                "municipio_crianza": user_data.get('municipio_crianza_participante_1'),
                "pais_residencia": user_data.get('pais_residencia_participante_1'),
                "provincia_residencia": user_data.get('provincia_residencia_participante_1'),
                "municipio_residencia": user_data.get('municipio_residencia_participante_1'),
                "tiempo_residencia": user_data.get('tiempo_residencia_participante_1')
            },
            "participante_2": {
                "papel": user_data.get('papel_participante_2'),
                "email": user_data.get('email_participante_2'),
                "nombre": user_data.get('nombre_participante_2'),
                "anio_nacimiento": user_data.get('anio_nacimiento_participante_2'),
                "genero": user_data.get('genero_participante_2'),
                "nivel_educativo": user_data.get('nivel_educativo_participante_2'),
                "universidad": user_data.get('universidad_participante_2'),
                "grado_anio": user_data.get('grado_anio_participante_2'),
                "grado_tipo": user_data.get('grado_tipo_participante_2'),
                "pais_nacimiento": user_data.get('pais_nacimiento_participante_2'),
                "provincia_nacimiento": user_data.get('provincia_nacimiento_participante_2'),
                "municipio_nacimiento": user_data.get('municipio_nacimiento_participante_2'),
                "pais_crianza": user_data.get('pais_crianza_participante_2'),
                "provincia_crianza": user_data.get('provincia_crianza_participante_2'),
                "municipio_crianza": user_data.get('municipio_crianza_participante_2'),
                "pais_residencia": user_data.get('pais_residencia_participante_2'),
                "provincia_residencia": user_data.get('provincia_residencia_participante_2'),
                "municipio_residencia": user_data.get('municipio_residencia_participante_2'),
                "tiempo_residencia": user_data.get('tiempo_residencia_participante_2')
            },
            "fecha_registro": datetime.utcnow()
        })

        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id=chat_id, text="Gracias por proporcionar los datos de ambos participantes. A continuación, comenzaremos con las preguntas.")
        return await start_questions(update, context)

    except Exception as e:
        logger.error(f"Error en save_group_data: {e}")
        chat_id = update.effective_chat.id if update.effective_chat else context.bot_data['default_chat_id']
        await context.bot.send_message(chat_id=chat_id, text="Ocurrió un error al registrar los datos. Por favor, intenta de nuevo.")
        return ConversationHandler.END
