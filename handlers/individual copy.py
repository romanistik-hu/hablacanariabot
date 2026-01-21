# individual.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from forms import *
import logging
from datetime import datetime
from handlers.questions_individual import start_questions
import re

logger = logging.getLogger(__name__)

# ============================================================================
# FUNCIONES GENÉRICAS DE UBICACIÓN GEOGRÁFICA
# ============================================================================

async def handle_country_generic(update, context: ContextTypes.DEFAULT_TYPE, context_type: str):
    """
    Función genérica para manejar la selección de país.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        chat_id = update.callback_query.from_user.id if update.callback_query else update.message.chat_id
        config = LOCATION_CONTEXTS[context_type]
        
        keyboard = [
            [InlineKeyboardButton("\U0001F1EA\U0001F1F8 España", callback_data='espana')],
            [InlineKeyboardButton("\U0001F310 Otro", callback_data='otro_pais')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat_id, 
            text=config['messages']['country_question'], 
            reply_markup=reply_markup
        )
        return config['states']['country_selection']
        
    except Exception as e:
        logger.error(f"Error en handle_country_generic para {context_type}: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Ocurrió un error al procesar tu selección.")
        return ConversationHandler.END

async def handle_country_selection_generic(update: Update, context: ContextTypes.DEFAULT_TYPE, context_type: str):
    """
    Función genérica para manejar la selección de país.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        query = update.callback_query
        await query.answer()
        pais = query.data
        config = LOCATION_CONTEXTS[context_type]
        
        if pais == 'otro_pais':
            await query.edit_message_text("\U00002753 Por favor, escribe el nombre de tu país:")
            return config['states']['country_input']
        else:
            context.user_data[config['data_keys']['country']] = 'España'
            await query.edit_message_text("\U00002705 Has seleccionado: España.")
            return await handle_province_generic(update, context, context_type)
            
    except Exception as e:
        logger.error(f"Error en handle_country_selection_generic para {context_type}: {e}")
        await context.bot.send_message(chat_id=query.from_user.id, text="Ocurrió un error al procesar tu selección.")
        return ConversationHandler.END

async def handle_country_input_generic(update: Update, context: ContextTypes.DEFAULT_TYPE, context_type: str):
    """
    Función genérica para manejar la entrada manual de país.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        config = LOCATION_CONTEXTS[context_type]
        context.user_data[config['data_keys']['country']] = update.message.text
        return await handle_province_generic(update, context, context_type)
        
    except Exception as e:
        logger.error(f"Error en handle_country_input_generic para {context_type}: {e}")
        await update.message.reply_text("Ocurrió un error al registrar tu país. Inténtalo de nuevo.")
        return ConversationHandler.END

async def handle_province_generic(update, context: ContextTypes.DEFAULT_TYPE, context_type: str):
    """
    Función genérica para manejar la selección de provincia.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        chat_id = update.callback_query.from_user.id if update.callback_query else update.message.chat_id
        config = LOCATION_CONTEXTS[context_type]
        
        if context.user_data.get(config['data_keys']['country']) == 'España':
            keyboard = [
                [InlineKeyboardButton("Santa Cruz de Tenerife", callback_data='tenerife')],
                [InlineKeyboardButton("Las Palmas", callback_data='las_palmas')],
                [InlineKeyboardButton("Otra", callback_data='otra_provincia')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=chat_id, 
                text=config['messages']['province_question'], 
                reply_markup=reply_markup
            )
            return config['states']['province_selection']
        else:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"\U00002753 Por favor, escribe el nombre de tu provincia:",
                reply_markup=ReplyKeyboardRemove()
            )
            return config['states']['province_input']
            
    except Exception as e:
        logger.error(f"Error en handle_province_generic para {context_type}: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Ocurrió un error al procesar tu selección.")
        return ConversationHandler.END

async def handle_province_selection_generic(update: Update, context: ContextTypes.DEFAULT_TYPE, context_type: str):
    """
    Función genérica para manejar la selección de provincia.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        query = update.callback_query
        await query.answer()
        provincia = query.data
        config = LOCATION_CONTEXTS[context_type]
        
        provincias_display = {
            'tenerife': 'Santa Cruz de Tenerife',
            'las_palmas': 'Las Palmas',
            'otra_provincia': 'Otra'
        }
        
        if provincia == 'otra_provincia':
            await query.edit_message_text(
                f"\U00002753 Por favor, escribe el nombre de tu provincia:", 
                reply_markup=None
            )
            return config['states']['province_input']
        else:
            provincia_display = provincias_display.get(provincia, provincia)
            context.user_data[config['data_keys']['province']] = provincia
            await query.edit_message_text(f"\U00002705 Has seleccionado: {provincia_display}.", reply_markup=None)
            await context.bot.send_message(
                chat_id=query.from_user.id, 
                text=config['messages']['municipio_question']
            )
            return config['states']['municipio_input']
            
    except Exception as e:
        logger.error(f"Error en handle_province_selection_generic para {context_type}: {e}")
        await context.bot.send_message(chat_id=query.from_user.id, text="Ocurrió un error al procesar tu selección.")
        return ConversationHandler.END

async def handle_province_input_generic(update: Update, context: ContextTypes.DEFAULT_TYPE, context_type: str):
    """
    Función genérica para manejar la entrada manual de provincia.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        config = LOCATION_CONTEXTS[context_type]
        context.user_data[config['data_keys']['province']] = update.message.text
        await update.message.reply_text(config['messages']['municipio_question'])
        return config['states']['municipio_input']
        
    except Exception as e:
        logger.error(f"Error en handle_province_input_generic para {context_type}: {e}")
        await update.message.reply_text("Ocurrió un error al registrar tu provincia. Inténtalo de nuevo.")
        return ConversationHandler.END

async def handle_municipio_generic(update: Update, context: ContextTypes.DEFAULT_TYPE, context_type: str):
    """
    Función genérica para manejar la entrada de municipio.
    
    Args:
        update: Objeto Update de Telegram
        context: Contexto de Telegram
        context_type: Tipo de contexto ('nacimiento', 'crianza', 'residencia')
    
    Returns:
        Estado al que debe transicionar
    """
    try:
        config = LOCATION_CONTEXTS[context_type]
        context.user_data[config['data_keys']['municipio']] = update.message.text
        
        # Determinar el siguiente flujo basado en el contexto
        if context_type == 'nacimiento':
            return await handle_country_generic(update, context, 'crianza')
        elif context_type == 'crianza':
            return await handle_country_generic(update, context, 'residencia')
        elif context_type == 'residencia':
            # Para residencia, mostrar el menú de tiempo de residencia
            chat_id = update.message.chat_id
            keyboard = [
                [InlineKeyboardButton("\U0001F4A1 Toda la vida", callback_data='toda_la_vida')],
                [InlineKeyboardButton("\U0001F553 Más de 5 años", callback_data='mas_de_5')],
                [InlineKeyboardButton("\U0001F551 Entre 3 y 5 años", callback_data='entre_3_y_5')],
                [InlineKeyboardButton("\U0001F550 Entre 1 y 3 años", callback_data='entre_1_y_3')],
                [InlineKeyboardButton("\U0001F55C Menos de un año", callback_data='menos_de_1')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=chat_id, 
                text="\U0001F4C5 ¿Cuánto tiempo llevas viviendo en tu lugar de residencia actual?", 
                reply_markup=reply_markup
            )
            return TIEMPO_RESIDENCIA_INDIVIDUAL
        else:
            logger.error(f"Contexto de ubicación desconocido: {context_type}")
            return ConversationHandler.END
            
    except Exception as e:
        logger.error(f"Error en handle_municipio_generic para {context_type}: {e}")
        await update.message.reply_text("Ocurrió un error al registrar tu municipio. Inténtalo de nuevo.")
        return ConversationHandler.END

# ============================================================================
# FUNCIONES WRAPPER PARA MANTENER COMPATIBILIDAD
# ============================================================================

async def pais_nacimiento(update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para país de nacimiento."""
    return await handle_country_generic(update, context, 'nacimiento')

async def pais_nacimiento_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de país de nacimiento."""
    return await handle_country_selection_generic(update, context, 'nacimiento')

async def pais_nacimiento_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de país de nacimiento."""
    return await handle_country_input_generic(update, context, 'nacimiento')

async def provincia_nacimiento(update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para provincia de nacimiento."""
    return await handle_province_generic(update, context, 'nacimiento')

async def provincia_nacimiento_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de provincia de nacimiento."""
    return await handle_province_selection_generic(update, context, 'nacimiento')

async def provincia_nacimiento_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de provincia de nacimiento."""
    return await handle_province_input_generic(update, context, 'nacimiento')

async def municipio_nacimiento_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada de municipio de nacimiento."""
    return await handle_municipio_generic(update, context, 'nacimiento')

async def pais_crianza(update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para país de crianza."""
    return await handle_country_generic(update, context, 'crianza')

async def pais_crianza_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de país de crianza."""
    return await handle_country_selection_generic(update, context, 'crianza')

async def pais_crianza_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de país de crianza."""
    return await handle_country_input_generic(update, context, 'crianza')

async def provincia_crianza(update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para provincia de crianza."""
    return await handle_province_generic(update, context, 'crianza')

async def provincia_crianza_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de provincia de crianza."""
    return await handle_province_selection_generic(update, context, 'crianza')

async def provincia_crianza_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de provincia de crianza."""
    return await handle_province_input_generic(update, context, 'crianza')

async def municipio_crianza_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada de municipio de crianza."""
    return await handle_municipio_generic(update, context, 'crianza')

async def pais_residencia(update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para país de residencia."""
    return await handle_country_generic(update, context, 'residencia')

async def pais_residencia_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de país de residencia."""
    return await handle_country_selection_generic(update, context, 'residencia')

async def pais_residencia_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de país de residencia."""
    return await handle_country_input_generic(update, context, 'residencia')

async def provincia_residencia(update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para provincia de residencia."""
    return await handle_province_generic(update, context, 'residencia')

async def provincia_residencia_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para selección de provincia de residencia."""
    return await handle_province_selection_generic(update, context, 'residencia')

async def provincia_residencia_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada manual de provincia de residencia."""
    return await handle_province_input_generic(update, context, 'residencia')

async def municipio_residencia_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper para entrada de municipio de residencia."""
    return await handle_municipio_generic(update, context, 'residencia')

# ============================================================================
# FUNCIONES EXISTENTES NO RELACIONADAS CON UBICACIÓN
# ============================================================================

async def start_individual_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        keyboard = [
            [InlineKeyboardButton("\U0001F393 Estudiante", callback_data='papel_estudiante')],
            [InlineKeyboardButton("\U0001F3EB Profesor", callback_data='papel_profesor')],
            [InlineKeyboardButton("\U0001F52C Investigador", callback_data='papel_investigador')],
            [InlineKeyboardButton("\U0001F464 Otro", callback_data='papel_otro')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            await update.message.reply_text("\U0001F4D1 Por favor, selecciona cuál es tu papel en esta investigación:", reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.message.reply_text("\U0001F4D1 Por favor, selecciona cuál es tu papel en esta investigación:", reply_markup=reply_markup)

        return PAPEL_INDIVIDUAL

    except Exception as e:
        logger.error(f"Error en start_individual_registration: {e}")
        if update.message:
            await update.message.reply_text("Ocurrió un error al iniciar el registro individual.")
        elif update.callback_query:
            await update.callback_query.message.reply_text("Ocurrió un error al iniciar el registro individual.")
        return ConversationHandler.END

async def handle_papel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        decision = query.data

        if decision == 'papel_otro':
            await query.edit_message_text("\U00002753 Por favor, especifica tu papel:")
            return OTRO_PAPEL_INDIVIDUAL
        else:
            papel = {
                'papel_estudiante': 'Estudiante',
                'papel_profesor': 'Docente',
                'papel_investigador': 'Investigador(a)'
            }.get(decision, 'Otro')

            context.user_data['papel'] = papel
            await query.edit_message_text(f"\U00002705 Has seleccionado: {papel}.")
            await context.bot.send_message(chat_id=query.from_user.id, text="\U0001F4E7 Por favor, proporciona tu correo electrónico:")
            return EMAIL_INDIVIDUAL

    except Exception as e:
        logger.error(f"Error en handle_papel: {e}")
        await context.bot.send_message(chat_id=query.from_user.id, text="Ocurrió un error al manejar tu selección.")
        return ConversationHandler.END

async def otro_papel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['papel'] = update.message.text
        await update.message.reply_text("\U0001F4E7 Por favor, proporciona tu correo electrónico:", reply_markup=ReplyKeyboardRemove())
        return EMAIL_INDIVIDUAL
    except Exception as e:
        logger.error(f"Error en otro_papel: {e}")
        await update.message.reply_text("Ocurrió un error al registrar tu papel. Inténtalo de nuevo.")
        return ConversationHandler.END

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        email_text = update.message.text

        if EMAIL_REGEX.match(email_text):
            context.user_data['email'] = email_text
            await update.message.reply_text(
                "\U0001F464 ¿Cuál es tu nombre?",
                reply_markup=ReplyKeyboardRemove()
            )
            return NOMBRE_INDIVIDUAL
        else:
            await update.message.reply_text(
                "El correo electrónico proporcionado no es válido. Por favor, ingresa un correo electrónico válido:"
            )
            return EMAIL_INDIVIDUAL

    except Exception as e:
        logger.error(f"Error en email: {e}")
        await update.message.reply_text(
            "Ocurrió un error al registrar tu correo electrónico. Por favor, intenta de nuevo:"
        )
        return EMAIL_INDIVIDUAL
    
async def nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['nombre'] = update.message.text
        await update.message.reply_text("\U0001F4C5 ¿En qué año naciste?", reply_markup=ReplyKeyboardRemove())
        return ANIO_NACIMIENTO_INDIVIDUAL
    except Exception as e:
        logger.error(f"Error en nombre: {e}")
        await update.message.reply_text("Ocurrió un error al registrar tu nombre. Inténtalo de nuevo.")
        return ConversationHandler.END

async def anio_nacimiento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        anio_nacimiento = int(update.message.text)
        current_year = datetime.now().year
        age = current_year - anio_nacimiento
        if age < 18:
            await update.message.reply_text("\U000026A0 La edad debe estar entre 18 y 120 años. Por favor, introduce un año válido.")
            return ANIO_NACIMIENTO_INDIVIDUAL
        if age > 120:
            await update.message.reply_text("\U000026A0 La edad debe estar entre 18 y 120 años. Por favor, introduce un año válido.")
            return ANIO_NACIMIENTO_INDIVIDUAL

        context.user_data['anio_nacimiento'] = anio_nacimiento

        keyboard = [
            [InlineKeyboardButton("\U0001F468\u200D\U0001F393 Masculino", callback_data='genero_masculino')],
            [InlineKeyboardButton("\U0001F469\u200D\U0001F393 Femenino", callback_data='genero_femenino')],
            [InlineKeyboardButton("\U0001F9D1 Otro", callback_data='genero_otro')],
            [InlineKeyboardButton("\U0001F636 Prefiero no decirlo", callback_data='genero_prefiero_no_decirlo')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("\U0001F3C3 ¿Cuál es tu género?", reply_markup=reply_markup)
        return GENERO_INDIVIDUAL

    except ValueError:
        await update.message.reply_text("\U0001F4A1 Por favor, introduce un año válido (solo números).")
        return ANIO_NACIMIENTO_INDIVIDUAL
    except Exception as e:
        logger.error(f"Error en anio_nacimiento: {e}")
        await update.message.reply_text("Ocurrió un error al registrar tu año de nacimiento. Inténtalo de nuevo.")
        return ConversationHandler.END

async def genero(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

        context.user_data['genero'] = genero
        await query.edit_message_text(f"\U00002705 Has seleccionado: {genero}.")

        keyboard = [
            [InlineKeyboardButton("\U0001F393 Grado", callback_data='nivel_grado')],
            [InlineKeyboardButton("\U0001F3EB Máster", callback_data='nivel_maestria')],
            [InlineKeyboardButton("\U0001F52C Doctorado", callback_data='nivel_doctorado')],
            [InlineKeyboardButton("\U0001F9D1 Otro", callback_data='nivel_otro')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=query.from_user.id, text="\U0001F4DA ¿Cuál es tu nivel educativo?", reply_markup=reply_markup)
        return NIVEL_EDUCATIVO_INDIVIDUAL

    except Exception as e:
        logger.error(f"Error en genero: {e}")
        await context.bot.send_message(chat_id=query.from_user.id, text="Ocurrió un error al registrar tu género. Inténtalo de nuevo.")
        return ConversationHandler.END

async def handle_nivel_educativo(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

        context.user_data['nivel_educativo'] = nivel_educativo
        await query.edit_message_text(f"\U00002705 Has seleccionado: {nivel_educativo}.")

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
            return GRADO_ANIO_INDIVIDUAL

        elif nivel_educativo in ['Máster', 'Doctorado']:
            return await universidad(update, context)

        elif nivel_educativo == 'Otro':
            await context.bot.send_message(chat_id=query.from_user.id, text="Por favor, especifica tu nivel educativo:")
            return OTRO_NIVEL_EDUCATIVO_INDIVIDUAL

    except Exception as e:
        logger.error(f"Error en handle_nivel_educativo: {e}")
        await context.bot.send_message(chat_id=query.from_user.id, text="Ocurrió un error al registrar tu nivel educativo. Inténtalo de nuevo.")
        return ConversationHandler.END
        
async def otro_nivel_educativo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['nivel_educativo'] = update.message.text
        return await pais_nacimiento(update, context)

    except Exception as e:
        logger.error(f"Error en otro_nivel_educativo: {e}")
        await update.message.reply_text("Ocurrió un error al registrar tu nivel educativo. Inténtalo de nuevo.")
        return ConversationHandler.END

async def handle_grado_anio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        grado_anio = query.data.split('_')[1]

        valid_options = ['1', '2', '3', '4', 'terminado']
        if grado_anio in valid_options:
            context.user_data['grado_anio'] = grado_anio
            await query.edit_message_text(f"\U00002705 Has seleccionado el año: {grado_anio}.")
            return await universidad(update, context)
        else:
            await query.edit_message_text("Por favor, selecciona una opción válida.")
            return GRADO_ANIO_INDIVIDUAL

    except Exception as e:
        logger.error(f"Error en handle_grado_anio: {e}")
        await context.bot.send_message(chat_id=query.from_user.id, text="Ocurrió un error al registrar el año de Grado. Inténtalo de nuevo.")
        return ConversationHandler.END

async def universidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Universidad de La Laguna \U0001F3DD\U0000FE0F", callback_data='ull')],
        [InlineKeyboardButton("Universidad de Las Palmas Gran Canaria \U0001F3DD\U0000FE0F", callback_data='ulpgc')],
        [InlineKeyboardButton("Otra \U0001F30D", callback_data='otra_universidad')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("\U0001F3EB ¿A qué universidad perteneces?", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("\U0001F3EB ¿A qué universidad perteneces?", reply_markup=reply_markup)

    return UNIVERSIDAD_INDIVIDUAL_SELECTION

async def universidad_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        universidad = query.data

        if universidad == 'otra_universidad':
            await query.edit_message_text("\U00002753 Por favor, escribe el nombre de tu universidad:")
            return OTRO_UNIVERSIDAD_INDIVIDUAL
        else:
            universidad_map = {
                'ull': 'Universidad de La Laguna',
                'ulpgc': 'Universidad de Las Palmas Gran Canaria'
            }
            context.user_data['universidad'] = universidad_map.get(universidad, 'Otra')
            await query.edit_message_text(f"\U00002705 Has seleccionado: {context.user_data['universidad']}.")

            # Obtener el chat_id desde el objeto query
            chat_id = query.message.chat_id

            # Llamar a pais_nacimiento pasando el chat_id correctamente
            return await pais_nacimiento(update=update, context=context)

    except Exception as e:
        logger.error(f"Error en universidad_selection: {e}")
        await context.bot.send_message(chat_id=query.from_user.id, text="Ocurrió un error al manejar la selección de la universidad. Inténtalo de nuevo.")
        return ConversationHandler.END

async def otro_universidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['universidad'] = update.message.text
    return await pais_nacimiento(update, context)

async def tiempo_residencia(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        context.user_data['tiempo_residencia'] = tiempo_residencia

        await query.edit_message_text(f"\U00002705 Has seleccionado: {tiempo_residencia}.")

        # Insertar datos en la base de datos con manejo de errores
        try:
            participantes_collection.insert_one({
                'usuario_id': str(query.from_user.id),
                'papel': context.user_data.get('papel'),
                'email': context.user_data.get('email'),
                'nombre': context.user_data.get('nombre'),
                'anio_nacimiento': int(context.user_data.get('anio_nacimiento')),
                'genero': context.user_data.get('genero'),
                'nivel_educativo': context.user_data.get('nivel_educativo'),
                'universidad': context.user_data.get('universidad'),
                'grado_anio': context.user_data.get('grado_anio'),
                'pais_nacimiento': context.user_data.get('pais_nacimiento'),
                'provincia_nacimiento': context.user_data.get('provincia_nacimiento'),
                'municipio_nacimiento': context.user_data.get('municipio_nacimiento'),
                'pais_crianza': context.user_data.get('pais_crianza'),
                'provincia_crianza': context.user_data.get('provincia_crianza'),
                'municipio_crianza': context.user_data.get('municipio_crianza'),
                'pais_residencia': context.user_data.get('pais_residencia'),
                'provincia_residencia': context.user_data.get('provincia_residencia'),
                'municipio_residencia': context.user_data.get('municipio_residencia'),
                'tiempo_residencia': context.user_data.get('tiempo_residencia'),
                'fecha_registro': datetime.utcnow()
            })
        except Exception as db_error:
            logger.error(f"Error al insertar en la base de datos: {db_error}")
            await context.bot.send_message(chat_id=query.from_user.id, text="Ocurrió un error al registrar tus datos. Por favor, intenta de nuevo.")

        await context.bot.send_message(chat_id=query.from_user.id, text="\U0001F64C ¡Gracias por proporcionar todos tus datos! A continuación, comenzaremos con las preguntas.")
        return await start_questions(update, context)

    except Exception as e:
        logger.error(f"Error en tiempo_residencia: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ocurrió un error al procesar tu selección. Por favor, intenta de nuevo.")


