# Importacion de librerias
import websockets
import asyncio
import ssl
import json

# Datos del servidor
HOST = 'wss://machuca.com.ar'
PORT = 4000

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

# Token del equipo
token = None

# Funcion para registrar el equipo
async def register(websocket):
    global token                                                              # Se accede a la variable global del token del equipo 1 para que podamos usarla luego

    await websocket.send(json.dumps(team_register))                           # Convertimos el diccionario a JSON con .dumps()
    print("Registro enviado. Esperando respuesta...")

    while True:
        try:
              # Esperamos la respuesta del servidor
              response = await asyncio.wait_for(websocket.recv(), timeout=5)
              data = json.loads(response)                                     # Convertimos el JSON en diccionario con .loads()

              if data["mensaje_id"] == "OK":
                  token = data["token"]
                  print(f"Registro exitoso. Token recibido: {token}")
                  return token

              elif data["mensaje_id"] == "ERROR":
                  error_desc = data["datos"]["descripcion"]
                  print(f"Error al registrar equipo: {error_desc}")
                  return None

              else:
                  print(f"Respuesta inesperada del servidor: {data}")

        except asyncio.TimeoutError:
            print("No se recibió respuesta del servidor en 5 segundos.")
        except websockets.exceptions.ConnectionClosed:
            print("Conexión cerrada antes de recibir respuesta.")
        except websockets.exceptions.ConnectionClosedOK:
            print("Server closed the connection normally.")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Server closed the connection with error: {e}")

# Funcion para patear la pelota
async def kick_the_ball(websocket):
    global token

    kick_action = {
        "mensaje_id": "PATEAR",
        "token": token,
        "datos": {"x": 10, "y": 10}
    }
    
    await websocket.send(json.dumps(kick_action))
    print(f'Accion enviada!. El jugador patea la pelota')

# Funcion para pasar la pelota
async def pass_the_ball(websocket):
    global token

    pass_action = {
        "mensaje_id": "PASAR_PELOTA",
        "token": token,
        "datos": {"jugador_numero": 10}
    }

    await websocket.send(json.dumps(pass_action))
    print(f'Accion enviada!. Pasar pelota al jugador 10')

# Funcion para que un jugador o un grupo de jugadores corra
async def run_on_the_pitch(websocket):
    global token

    run_action = {
        "mensaje_id": "CORRER",
        "token": token,
        "datos": {
           "movimientos":[
              {"jugador_numero": 10, "x": 10, "y": 10},
              {"jugador_numero": 11, "x": 5, "y": 10},
              {"jugador_numero": 9, "x": 8, "y": 10}
           ]
        }
    }     
    await websocket.send(json.dumps(run_action))
    print(f'Accion enviada!. Movimiento de jugador/es')

# Funcion para evaluar los mensajes y procesarlos de acuerdo al tipo
async def process_messages(websocket):
    async for message in websocket:
        data = json.loads(message)
        message_id = data.get("mensaje_id")

        if message_id == "TIENES_LA_PELOTA":
            print("Tienes la pelota!")
            await pass_the_ball(websocket)
            await run_on_the_pitch(websocket)
            

async def main():
    url = f"{HOST}:{PORT}"
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)                     # Creamos un contexto SSL para establecer una conexión segura (TLS)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE                                   # Desactivamos la verificación del certificado SSL
    
    async with websockets.connect(url, ssl=ssl_context) as websocket:
        print("Conectado al servidor!. Registrando equipo...")
        await register(websocket)
        print(f'El token del equipo es: {token}')
        await process_messages(websocket)

# Ejecutamos la funcion
asyncio.run(main())