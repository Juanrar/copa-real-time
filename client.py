# Importacion de librerias
import websockets
import asyncio
import ssl
import json
import logging
import datetime
import sys
from mensajes import (parse_server_message,
                      MensajeRegistro,
                      MensajeTienesLaPelota,
                      MensajeReaccionar,
                      MensajeError,
                      ClientMessage,
                      correr,
                      pasar_pelota,
                      patear,
                      marcar_adversario)
from utils import (get_ubicacion_pelota, 
                   buscar_pelota,
                   patear_al_arco)

# Datos del servidor
HOST = 'wss://machuca.com.ar'
PORT = 4000

now = datetime.datetime.now()
now_formatted = now.strftime("%Y%m%d_%H%M%S")

logging.basicConfig(
    filename=f'./logs/client_{now_formatted}.log',        # Nombre del archivo de log
    filemode='w',              # 'a' para añadir (append), 'w' para sobrescribir (write)
    level=logging.INFO,        # Nivel mínimo para registrar
    format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger_raiz = logging.getLogger()
consola_handler = logging.StreamHandler(sys.stdout)
consola_handler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# Equipos para hacer el registro (Mensaje REGISTRAR)
team_register = {
    "mensaje_id":"REGISTRAR",
    "datos":{
        "equipo":{
            "id":"1",
            "nombre":"PIÑEYRO",
            "jugadores":[
                {"numero": 1, "nombre": "Mayer", "equipo_id": "1"},
                {"numero": 2, "nombre": "Lagostena", "equipo_id": "1"},
                {"numero": 3, "nombre": "Asteasuain","equipo_id": "1"},
                {"numero": 4, "nombre": "Diaz", "equipo_id": "1"},
                {"numero": 5, "nombre": "Freire", "equipo_id": "1"},
                {"numero": 6, "nombre": "Galli", "equipo_id": "1"},
                {"numero": 7, "nombre": "Legaspi", "equipo_id": "1"},
                {"numero": 8, "nombre": "Sabella", "equipo_id": "1"},
                {"numero": 9, "nombre": "Tomsic", "equipo_id": "1"},
                {"numero": 10, "nombre": "Dangiolo", "equipo_id": "1", "es_el_crack": True},
                {"numero": 11, "nombre": "Dubinsky", "equipo_id": "1", "tiene_la_pelota": True}
            ],
            "formacion":"4-4-2"
        }
      }
    }

# Funcion para registrar el equipo
async def register(websocket) -> MensajeRegistro:
    await websocket.send(json.dumps(team_register))                           # Convertimos el diccionario a JSON con .dumps()
    logger.info("Registro enviado. Esperando respuesta...")

    while True:
        try:
            # Esperamos la respuesta del servidor
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            mensaje = parse_server_message(response)

            if type(mensaje) == MensajeRegistro:
                return mensaje
            elif type(mensaje) == MensajeError:
                logger.error(f'Error: {mensaje.datos}')
                return None
            else:
                return None

        except asyncio.TimeoutError:
            logger.error("No se recibió respuesta del servidor en 5 segundos.")
        except websockets.exceptions.ConnectionClosed:
            logger.error("Conexión cerrada antes de recibir respuesta.")
        except websockets.exceptions.ConnectionClosedOK:
            logger.error("Server closed the connection normally.")
        except websockets.exceptions.ConnectionClosedError as e:
            logger.error(f"Server closed the connection with error: {e}")
        return None

async def send_message(websocket, mensaje: ClientMessage):

    await websocket.send(json.dumps(mensaje.model_dump()))
    logger.info(f'Accion enviada. Mensaje: {mensaje}')
    return


# Funcion para evaluar los mensajes y procesarlos de acuerdo al tipo
async def process_messages(websocket, token: str, equipo_id: str):
    async for response in websocket:
        mensaje = parse_server_message(response)
        pos = 10
        if type(mensaje) == MensajeTienesLaPelota:
            logger.info("Tienes la pelota!")
            logger.debug(mensaje)
            #await send_message(websocket=websocket, mensaje=pasar_pelota(token, pos))
            mensaje_a_enviar = patear_al_arco(token, mensaje, equipo_id)
            await send_message(websocket, mensaje=mensaje_a_enviar)
            if pos == 10:
                pos = 9
            else:
                pos = 10
        elif type(mensaje) == MensajeReaccionar:
            logger.info("Reaccionar")
            logger.debug(mensaje)
            mensaje_a_enviar = buscar_pelota(token, mensaje, equipo_id)
            await send_message(websocket, mensaje=mensaje_a_enviar)
        elif type(mensaje) == MensajeError:
            logger.error(f"Mensaje de error del servidor. Mensaje enviado: {mensaje_a_enviar}, Mensaje recibido: {mensaje}")
        else:
            logger.warning(f"Otro mensaje recibido. Mensaje enviado: \nMensaje Enviado: {mensaje_a_enviar}\n\nMensaje recibido: {mensaje}")

async def main():
    url = f"{HOST}:{PORT}"
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)                     # Creamos un contexto SSL para establecer una conexión segura (TLS)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE                                   # Desactivamos la verificación del certificado SSL
    token = None
    
    async with websockets.connect(url, ssl=ssl_context) as websocket:
        logger.info("Conectado al servidor!. Registrando equipo...")
        mensaje_registro = await register(websocket)
        token = mensaje_registro.token
        equipo_id = mensaje_registro.destinatario
        if token is None:
            logger.error('No se registro ningun token. Saliendo')
            return
        logger.info(f'El token del equipo es: {token}')
        await process_messages(websocket, token=token, equipo_id=equipo_id)

# Ejecutamos la funcion
asyncio.run(main())