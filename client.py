import asyncio
import websockets
import sys
import json
import ssl

# --- Configuración ---
# Dirección del servidor WebSocket seguro (wss) y puerto
HOST = "wss://machuca.com.ar:4000"

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

token = None

async def register(websocket):                     
    print("-> Enviando mensaje REGISTRAR...")                                   
    await websocket.send(json.dumps(team_register))
    print("Registro enviado.")

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


async def handle_message(websocket, message_data):
    """Procesa los mensajes recibidos del servidor."""
    global token

    message_id = message_data.get("mensaje_id")
    datos = message_data.get("datos")
    token_in_message = message_data.get("token")

    print(f"<- Mensaje recibido con mensaje_id: {message_id}")

    if message_id == "OK":
        token = token_in_message
        print(f"   ¡Registro exitoso! Token recibido: {token}")
        print("   Esperando que comience el partido...")
    
    
    elif message_id == "TIENES_LA_PELOTA":
            print("Tienes la pelota!")
            await pass_the_ball(websocket)
            await run_on_the_pitch(websocket)

    elif message_id == "ERROR":
        error_desc = datos.get("descripcion", "Error desconocido")
        print(f"   ERROR del servidor: {error_desc}")
        print("   El cliente terminará debido a un error de registro.")
        await websocket.close()
        sys.exit(1)
    
async def run_client():
    print(f"Intentando conectar a {HOST}")
    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with websockets.connect(HOST, ssl=ssl_context) as websocket:
            print("¡Conexion establecida con exito!")
            
            await register(websocket)
            
            while True:
                try:
                    message = await websocket.recv()
                    
                    try:
                        message_data = json.loads(message)
                        await handle_message(websocket, message_data)
                        
                    except json.JSONDecodeError:
                        print(f"Error: No se pudo decodificar el mensaje como JSON: {message}")
                    except Exception as e:
                        print(f"Error al procesar el mensaje: {e}\nMensaje: {message}")
                    
                except websockets.exceptions.ConnectionClosedOK:
                    print("Conexión cerrada por el servidor de forma limpia.")
                    break
                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"Conexión cerrada con error: {e}")
                    break
                except Exception as e:
                    print(f"Ocurrió un error durante la comunicación: {e}")
                    break
    except ConnectionRefusedError:
        print(f"Error: Conexión rechazada. Asegúrate de que el servidor en {HOST} está activo y accesible.")
        sys.exit(1)
    except Exception as e:
        print(f"Error general al conectar o ejecutar: {e}")
        sys.exit(1)
    

if __name__ == "__main__":
    asyncio.run(run_client())