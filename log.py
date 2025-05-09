import logging
import logging.config
import datetime
import sys # Para salida a consola

now = datetime.datetime.now()
now_formatted = now.strftime("%Y%m%d_%H%M%S")

def setup_logging(id: int):
    """Configura el logging para la aplicación."""
    # Asegúrate de que el directorio de logs exista
    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')

    LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d (%(funcName)s) - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO', # Nivel mínimo para este handler
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout,
        },
        'file_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'filename': f'logs/client_{id}_{now_formatted}.log',
            'encoding': 'utf-8',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'detailed', # Más detalle para errores
            'filename': f'logs/client_{id}_error_{now_formatted}.log',
            'encoding': 'utf-8',
        }
    },
    'loggers': {
        '': { # Logger raíz (root logger)
            'handlers': ['console', 'file_info', 'file_error'],
            'level': 'INFO', # Nivel global por defecto si no se especifica en un logger específico
            'propagate': True # Si los mensajes también deben ir al handler del logger padre
        }
    }
    }
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info("Logging configurado exitosamente.")