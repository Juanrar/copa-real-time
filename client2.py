import websockets
import asyncio
import ssl
import json
import logging
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
from teams import TEAM_PIN, TEAM_LANUS
from log import setup_logging

# Datos del servidor
HOST = 'wss://machuca.com.ar'
PORT = 4000

logger = logging.getLogger('client')

team_register = TEAM_LANUS
ID_CLIENT = 2

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

        if type(mensaje) == MensajeTienesLaPelota:
            logger.info("Tienes la pelota!")
            logger.debug(mensaje)
            mensaje_a_enviar = patear_al_arco(token, mensaje, equipo_id)
            await send_message(websocket, mensaje=mensaje_a_enviar)

        elif type(mensaje) == MensajeReaccionar:
            logger.info("Reaccionar")
            logger.debug(mensaje)
            mensaje_a_enviar = buscar_pelota(token, mensaje, equipo_id)
            await send_message(websocket, mensaje=mensaje_a_enviar)

        elif type(mensaje) == MensajeError:
            logger.error(f"Mensaje de error del servidor. Mensaje enviado: {mensaje_a_enviar}, Mensaje recibido: {mensaje}")

        else:
            logger.warning(f"Otro mensaje recibido.\nMensaje Enviado: {mensaje_a_enviar}\n\nMensaje recibido: {mensaje}")

async def main():
    url = f"{HOST}:{PORT}"
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)                     # Creamos un contexto SSL para establecer una conexión segura (TLS)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE                                   # Desactivamos la verificación del certificado SSL
    token = None
    setup_logging(ID_CLIENT)
    
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