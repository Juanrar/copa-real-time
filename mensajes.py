import json
import logging
from typing import Optional, List, Tuple, Dict, Any, Literal, Union
from pydantic import BaseModel, ValidationError, Field

logger = logging.getLogger('mensajes')

class BaseServerMessage(BaseModel):
    mensaje_id: str = Field(..., alias='mensaje_id')
    destinatario: str = Field(..., alias='destinatario')

class BaseClientMessage(BaseModel):
    mensaje_id: str = Field(..., alias='mensaje_id')
    token: str = Field(..., alias='token')
    datos: dict = Field(..., alias='datos')
# --- Modelos para Estructuras Internas ---

class Coordenada(BaseModel):
    """Representa una coordenada X, Y."""
    x: int
    y: int

class Ocupante(BaseModel):
    """Representa un jugador (u ocupante) en un sector."""
    numero: int
    nombre: str
    equipo_id: str = Field(..., alias='equipo_id') # Usar alias si prefieres equipo_id
    sector_id: int = Field(..., alias='sector_id')   # Usar alias si prefieres sector_id
    tiene_la_pelota: Optional[bool] = Field(None, alias='tiene_la_pelota')
    es_el_crack: Optional[bool] = Field(None, alias='es_el_crack')

class Sector(BaseModel):
    """Representa un sector de la cancha."""
    id: int
    x: int
    y: int
    # Un sector puede tener uno o más ocupantes
    ocupantes: List[Ocupante]

class Equipo(BaseModel):
    """Representa la información de un equipo."""
    id: str
    nombre: str
    formacion: str
    rol: int
    goles: int
    # El arco está definido por una lista de coordenadas
    arco: Tuple[Coordenada, Coordenada, Coordenada]

class UbicacionPelota(BaseModel):
    """Representa la ubicación de la pelota."""
    id: int # Parece ser el ID del sector donde está la pelota
    x: int
    y: int
    esta_la_pelota: Optional[bool] = Field(None, alias='esta_la_pelota')

# --- Modelos para los Items dentro de la lista "datos" ---

class CanchaData(BaseModel):
    """Representa el objeto 'cancha' dentro de la lista 'datos'."""
    tipo: Literal['cancha'] # Fija el valor esperado para 'tipo'
    id: str # Parece ser siempre 'cancha' en este caso
    equipo1: Equipo
    equipo2: Equipo
    sectores: List[Sector]
    ubicacion_pelota: UbicacionPelota = Field(..., alias='ubicacion_pelota')
    time_stamp: str = Field(..., alias='time_stamp')

class RelojData(BaseModel):
    """Representa el objeto 'reloj' dentro de la lista 'datos'."""
    tipo: Literal['reloj']
    reloj: int # O float, dependiendo de la precisión necesaria

# --- Unión de los posibles tipos dentro de la lista "datos" ---
# Pydantic usará el campo 'tipo' para decidir si es CanchaData o RelojData
DatoItem = Union[CanchaData, RelojData]

# --- Modelo Principal ---
class MensajeTienesLaPelota(BaseServerMessage):
    """Representa el mensaje completo cuando mensaje_id es 'TIENES_LA_PELOTA'."""
    mensaje_id: Literal['TIENES_LA_PELOTA']
    # La lista 'datos' puede contener objetos CanchaData o RelojData
    datos: List[DatoItem]

class MensajeReaccionar(BaseServerMessage):
    """Representa el mensaje completo cuando mensaje_id es 'TIENES_LA_PELOTA'."""
    mensaje_id: Literal['REACCIONAR']
    # La lista 'datos' puede contener objetos CanchaData o RelojData
    datos: List[DatoItem]

class MensajeRegistro(BaseServerMessage):
    mensaje_id: Literal['OK']
    token: str

class MensajeError(BaseModel):
    mensaje_id: Literal['ERROR']
    datos: dict

class MensajeCorrer(BaseClientMessage):
    mensaje_id: Literal['CORRER']

class MensajePatear(BaseClientMessage):
    mensaje_id: Literal['PATEAR']

class MensajePasarPelota(BaseClientMessage):
    mensaje_id: Literal['PASAR_PELOTA']

class MensajeMarcarAdversario(BaseClientMessage):
    mensaje_id: Literal['MARCAR_ADVERSARIO']

ServerMessage = Union[MensajeRegistro, MensajeTienesLaPelota, MensajeReaccionar, MensajeError]
ClientMessage = Union[MensajeCorrer, MensajePasarPelota, MensajePatear]

def parse_server_message(raw_data: str) -> Optional[ServerMessage]:
    """
    Parsea un string JSON recibido del servidor y lo convierte
    en el objeto Pydantic correspondiente.
    """
    try:
        data = json.loads(raw_data)
        msg_id = data.get('mensaje_id')
        
        if msg_id == 'OK':
            message = MensajeRegistro(**data)
        elif msg_id == 'TIENES_LA_PELOTA':
            message = MensajeTienesLaPelota(**data)
        elif msg_id == 'REACCIONAR':
            message = MensajeReaccionar(**data)
        elif msg_id == 'ERROR':
            message = MensajeError(**data)
        else:
            logger.error(f'msg_id no interpretado. Data: {data}')
            message = None
        return message

    except json.JSONDecodeError:
        logger.error(f"Mensaje recibido no es JSON válido: {raw_data}")
        return None
    except ValidationError as e:
        try:
            # Correccion de error dado formato raro con el mensaje Reaccionar
            data['datos'] = data['datos'][1:2]
            message = MensajeReaccionar(**data)
            return message
        except Exception:    
            logger.critical(f'Error al parsear: {raw_data}')
            logger.critical(f"\n\nError: Datos de mensaje inválidos: {e.errors()}")
            return None
    except Exception as e:
        logger.critical(f"Error inesperado al parsear mensaje: {e}")
        logger.critical(f"  Mensaje: {raw_data}")
        return None
    
def pasar_pelota(token: str, jugador: int) -> MensajePasarPelota:

    mensaje = MensajePasarPelota(   mensaje_id='PASAR_PELOTA',
                                    token=token,
                                    datos={"jugador_numero": jugador})
    
    return mensaje

def correr(token: str, datos: dict) -> MensajeCorrer:

    mensaje = MensajeCorrer(mensaje_id='CORRER',
                            token=token,
                            datos=datos)
    
    return mensaje

def patear(token: str, coord = Coordenada) -> MensajePatear:

    mensaje = MensajePatear(mensaje_id='PATEAR',
                            token=token,
                            datos={"x": coord.x, "y": coord.y})
    
    return mensaje

def marcar_adversario(token: str, jugador: int, adversario: int) -> MensajeMarcarAdversario:

    mensaje = MensajeMarcarAdversario(mensaje_id='MARCAR_ADVERSARIO',
                                      token=token,
                                      datos={"jugador_numero": jugador,
                                             "adversario_numero": adversario})
    
    return mensaje