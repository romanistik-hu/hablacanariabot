# bot.py

from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from handlers import (
    task,
    consent_individual,
    consent_group,
    individual,
    group,
    questions_individual,
    questions_group,
    restart,
    exit as exit_handler 
)
from forms import *
from config import TELEGRAM_TOKEN
import logging
from logging.handlers import RotatingFileHandler 


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

rotating_error_handler = RotatingFileHandler(
    'errors.log', maxBytes=5*1024*1024, backupCount=25  
)
rotating_error_handler.setLevel(logging.ERROR)

rotating_error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rotating_error_handler.setFormatter(rotating_error_formatter)


logger.addHandler(rotating_error_handler)

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', task.start_task)],
        states={
            TIPO_TAREA: [CallbackQueryHandler(task.handle_task_selection, pattern='^tarea_individual|tarea_grupal$')],        
            CONSENTIMIENTO_INDIVIDUAL: [CallbackQueryHandler(consent_individual.handle_consent_individual, pattern='^aceptar_consentimiento|rechazar_consentimiento$')],
            CONSENTIMIENTO_GRUPAL: [CallbackQueryHandler(consent_group.handle_consent_group, pattern='^aceptar_consentimiento_grupal|rechazar_consentimiento_grupal$')],

            PAPEL_INDIVIDUAL: [CallbackQueryHandler(individual.handle_papel, pattern='^papel_estudiante|papel_profesor|papel_investigador|papel_otro$')],
            OTRO_PAPEL_INDIVIDUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.otro_papel)],
            EMAIL_INDIVIDUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.email)],
            NOMBRE_INDIVIDUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.nombre)],
            ANIO_NACIMIENTO_INDIVIDUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.anio_nacimiento)],
            GENERO_INDIVIDUAL: [CallbackQueryHandler(individual.genero, pattern='^genero_masculino|genero_femenino|genero_otro|genero_prefiero_no_decirlo$')],
            NIVEL_EDUCATIVO_INDIVIDUAL: [CallbackQueryHandler(individual.handle_nivel_educativo, pattern='^nivel_grado|nivel_maestria|nivel_doctorado|nivel_otro$')],
            OTRO_NIVEL_EDUCATIVO_INDIVIDUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.otro_nivel_educativo)],
            GRADO_ANIO_INDIVIDUAL: [CallbackQueryHandler(individual.handle_grado_anio, pattern='^grado_\\d|grado_terminado$')],
            GRADO_TIPO_INDIVIDUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.handle_grado_tipo)],
            UNIVERSIDAD_INDIVIDUAL_SELECTION: [CallbackQueryHandler(individual.universidad_selection, pattern='^ull|ulpgc|otra_universidad$')],
            OTRO_UNIVERSIDAD_INDIVIDUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.otro_universidad)],
            PAIS_NACIMIENTO_INDIVIDUAL_SELECTION: [CallbackQueryHandler(individual.pais_nacimiento_selection, pattern='^espana|otro_pais$')],
            PAIS_NACIMIENTO_INDIVIDUAL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.pais_nacimiento_input)],
            PROVINCIA_NACIMIENTO_INDIVIDUAL_SELECTION: [CallbackQueryHandler(individual.provincia_nacimiento_selection, pattern='^tenerife|las_palmas|otra_provincia$')],
            PROVINCIA_NACIMIENTO_INDIVIDUAL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.provincia_nacimiento_input)],
            MUNICIPIO_NACIMIENTO_INDIVIDUAL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.municipio_nacimiento_input)],
            PAIS_CRIANZA_INDIVIDUAL_SELECTION: [CallbackQueryHandler(individual.pais_crianza_selection, pattern='^espana|otro_pais$')],
            PAIS_CRIANZA_INDIVIDUAL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.pais_crianza_input)],
            PROVINCIA_CRIANZA_INDIVIDUAL_SELECTION: [CallbackQueryHandler(individual.provincia_crianza_selection, pattern='^tenerife|las_palmas|otra_provincia$')],
            PROVINCIA_CRIANZA_INDIVIDUAL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.provincia_crianza_input)],
            MUNICIPIO_CRIANZA_INDIVIDUAL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.municipio_crianza_input)],
            PAIS_RESIDENCIA_INDIVIDUAL_SELECTION: [CallbackQueryHandler(individual.pais_residencia_selection, pattern='^espana|otro_pais$')],
            PAIS_RESIDENCIA_INDIVIDUAL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.pais_residencia_input)],
            PROVINCIA_RESIDENCIA_INDIVIDUAL_SELECTION: [CallbackQueryHandler(individual.provincia_residencia_selection, pattern='^tenerife|las_palmas|otra_provincia$')],
            PROVINCIA_RESIDENCIA_INDIVIDUAL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.provincia_residencia_input)],
            MUNICIPIO_RESIDENCIA_INDIVIDUAL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual.municipio_residencia_input)],
            TIEMPO_RESIDENCIA_INDIVIDUAL: [CallbackQueryHandler(individual.tiempo_residencia, pattern='^toda_la_vida|mas_de_5|entre_3_y_5|entre_1_y_3|menos_de_1$')],

            PAPEL_PARTICIPANTE_1: [CallbackQueryHandler(group.handle_papel_participante, pattern='^papel_estudiante|papel_profesor|papel_investigador|papel_otro$')],
            OTRO_PAPEL_PARTICIPANTE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.otro_papel_participante)],
            EMAIL_PARTICIPANTE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.email_participante)],
            NOMBRE_PARTICIPANTE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.nombre_participante)],
            ANIO_NACIMIENTO_PARTICIPANTE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.anio_nacimiento_participante)],
            GENERO_PARTICIPANTE_1: [CallbackQueryHandler(group.genero_participante, pattern='^genero_masculino|genero_femenino|genero_otro|genero_prefiero_no_decirlo$')],
            NIVEL_EDUCATIVO_PARTICIPANTE_1: [CallbackQueryHandler(group.nivel_educativo_participante, pattern='^nivel_grado|nivel_maestria|nivel_doctorado|nivel_otro$')],
            OTRO_NIVEL_EDUCATIVO_PARTICIPANTE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.otro_nivel_educativo_participante)],
            GRADO_ANIO_PARTICIPANTE_1: [CallbackQueryHandler(group.grado_anio_participante, pattern='^grado_\\d|grado_terminado$')],
            GRADO_TIPO_PARTICIPANTE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.handle_grado_tipo_participante)],
            UNIVERSIDAD_PARTICIPANTE_1_SELECTION: [CallbackQueryHandler(group.universidad_selection_participante, pattern='^ull|ulpgc|otra_universidad$')],
            OTRO_UNIVERSIDAD_PARTICIPANTE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.otro_universidad_participante)],
            PAIS_NACIMIENTO_PARTICIPANTE_1_SELECTION: [CallbackQueryHandler(group.pais_nacimiento_participante_selection, pattern='^espana|otro_pais$')],
            PAIS_NACIMIENTO_PARTICIPANTE_1_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.pais_nacimiento_participante_input)],
            PROVINCIA_NACIMIENTO_PARTICIPANTE_1_SELECTION: [CallbackQueryHandler(group.provincia_nacimiento_participante_selection, pattern='^tenerife|las_palmas|otra_provincia$')],
            PROVINCIA_NACIMIENTO_PARTICIPANTE_1_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.provincia_nacimiento_participante_input)],
            MUNICIPIO_NACIMIENTO_PARTICIPANTE_1_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.municipio_nacimiento_participante_input)],
            PAIS_CRIANZA_PARTICIPANTE_1_SELECTION: [CallbackQueryHandler(group.pais_crianza_participante_selection, pattern='^espana|otro_pais$')],
            PAIS_CRIANZA_PARTICIPANTE_1_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.pais_crianza_participante_input)],
            PROVINCIA_CRIANZA_PARTICIPANTE_1_SELECTION: [CallbackQueryHandler(group.provincia_crianza_participante_selection, pattern='^tenerife|las_palmas|otra_provincia$')],
            PROVINCIA_CRIANZA_PARTICIPANTE_1_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.provincia_crianza_participante_input)],
            MUNICIPIO_CRIANZA_PARTICIPANTE_1_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.municipio_crianza_participante_input)],
            PAIS_RESIDENCIA_PARTICIPANTE_1_SELECTION: [CallbackQueryHandler(group.pais_residencia_participante_selection, pattern='^espana|otro_pais$')],
            PAIS_RESIDENCIA_PARTICIPANTE_1_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.pais_residencia_participante_input)],
            PROVINCIA_RESIDENCIA_PARTICIPANTE_1_SELECTION: [CallbackQueryHandler(group.provincia_residencia_participante_selection, pattern='^tenerife|las_palmas|otra_provincia$')],
            PROVINCIA_RESIDENCIA_PARTICIPANTE_1_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.provincia_residencia_participante_input)],
            MUNICIPIO_RESIDENCIA_PARTICIPANTE_1_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.municipio_residencia_participante_input)],
            TIEMPO_RESIDENCIA_PARTICIPANTE_1: [CallbackQueryHandler(group.tiempo_residencia_participante, pattern='^toda_la_vida|mas_de_5|entre_3_y_5|entre_1_y_3|menos_de_1$')],

            PAPEL_PARTICIPANTE_2: [CallbackQueryHandler(group.handle_papel_participante, pattern='^papel_estudiante|papel_profesor|papel_investigador|papel_otro$')],
            OTRO_PAPEL_PARTICIPANTE_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.otro_papel_participante)],
            EMAIL_PARTICIPANTE_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.email_participante)],
            NOMBRE_PARTICIPANTE_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.nombre_participante)],
            ANIO_NACIMIENTO_PARTICIPANTE_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.anio_nacimiento_participante)],
            GENERO_PARTICIPANTE_2: [CallbackQueryHandler(group.genero_participante, pattern='^genero_masculino|genero_femenino|genero_otro|genero_prefiero_no_decirlo$')],
            NIVEL_EDUCATIVO_PARTICIPANTE_2: [CallbackQueryHandler(group.nivel_educativo_participante, pattern='^nivel_grado|nivel_maestria|nivel_doctorado|nivel_otro$')],
            OTRO_NIVEL_EDUCATIVO_PARTICIPANTE_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.otro_nivel_educativo_participante)],
            GRADO_ANIO_PARTICIPANTE_2: [CallbackQueryHandler(group.grado_anio_participante, pattern='^grado_\\d|grado_terminado$')],
            GRADO_TIPO_PARTICIPANTE_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.handle_grado_tipo_participante)],
            UNIVERSIDAD_PARTICIPANTE_2_SELECTION: [CallbackQueryHandler(group.universidad_selection_participante, pattern='^ull|ulpgc|otra_universidad$')],
            OTRO_UNIVERSIDAD_PARTICIPANTE_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.otro_universidad_participante)],
            PAIS_NACIMIENTO_PARTICIPANTE_2_SELECTION: [CallbackQueryHandler(group.pais_nacimiento_participante_selection, pattern='^espana|otro_pais$')],
            PAIS_NACIMIENTO_PARTICIPANTE_2_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.pais_nacimiento_participante_input)],
            PROVINCIA_NACIMIENTO_PARTICIPANTE_2_SELECTION: [CallbackQueryHandler(group.provincia_nacimiento_participante_selection, pattern='^tenerife|las_palmas|otra_provincia$')],
            PROVINCIA_NACIMIENTO_PARTICIPANTE_2_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.provincia_nacimiento_participante_input)],
            MUNICIPIO_NACIMIENTO_PARTICIPANTE_2_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.municipio_nacimiento_participante_input)],
            PAIS_CRIANZA_PARTICIPANTE_2_SELECTION: [CallbackQueryHandler(group.pais_crianza_participante_selection, pattern='^espana|otro_pais$')],
            PAIS_CRIANZA_PARTICIPANTE_2_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.pais_crianza_participante_input)],
            PROVINCIA_CRIANZA_PARTICIPANTE_2_SELECTION: [CallbackQueryHandler(group.provincia_crianza_participante_selection, pattern='^tenerife|las_palmas|otra_provincia$')],
            PROVINCIA_CRIANZA_PARTICIPANTE_2_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.provincia_crianza_participante_input)],
            MUNICIPIO_CRIANZA_PARTICIPANTE_2_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.municipio_crianza_participante_input)],
            PAIS_RESIDENCIA_PARTICIPANTE_2_SELECTION: [CallbackQueryHandler(group.pais_residencia_participante_selection, pattern='^espana|otro_pais$')],
            PAIS_RESIDENCIA_PARTICIPANTE_2_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.pais_residencia_participante_input)],
            PROVINCIA_RESIDENCIA_PARTICIPANTE_2_SELECTION: [CallbackQueryHandler(group.provincia_residencia_participante_selection, pattern='^tenerife|las_palmas|otra_provincia$')],
            PROVINCIA_RESIDENCIA_PARTICIPANTE_2_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.provincia_residencia_participante_input)],
            MUNICIPIO_RESIDENCIA_PARTICIPANTE_2_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, group.municipio_residencia_participante_input)],
            TIEMPO_RESIDENCIA_PARTICIPANTE_2: [CallbackQueryHandler(group.tiempo_residencia_participante, pattern='^toda_la_vida|mas_de_5|entre_3_y_5|entre_1_y_3|menos_de_1$')],
            
            
            PREGUNTAS_INDIVIDUAL: [
            MessageHandler(filters.ALL & ~filters.COMMAND, questions_individual.handle_questions),
            CallbackQueryHandler(restart.handle_restart, pattern='^restart$'),  
            CallbackQueryHandler(exit_handler.handle_exit, pattern='^exit$'), 
            CallbackQueryHandler(questions_individual.handle_additional_audio, pattern='^(enviar_otro_audio|continuar)$'),
            CallbackQueryHandler(questions_individual.handle_questions, pattern='^opcion_.*$'),
            ],
            PREGUNTAS_GRUPAL: [
            MessageHandler(filters.ALL & ~filters.COMMAND, questions_group.handle_questions),
            CallbackQueryHandler(restart.handle_restart, pattern='^restart$'),
            CallbackQueryHandler(exit_handler.handle_exit, pattern='^exit$'),
            CallbackQueryHandler(questions_group.handle_additional_audio, pattern='^(enviar_otro_audio|continuar)$'),
            ],
        },
        fallbacks=[CommandHandler('start', task.start_task)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
