import json
from typing import Optional, List, Tuple, Dict, Any, Literal, Union
from pydantic import BaseModel, ValidationError, Field

class BaseServerMessage(BaseModel):
    mensaje_id: str = Field(..., alias='mensaje_id')
    destinatario: str = Field(..., alias='destinatario')

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

ServerMessage = Union[MensajeRegistro, MensajeTienesLaPelota, MensajeReaccionar, MensajeError]

message = {"mensaje_id":"TIENES_LA_PELOTA","destinatario":"TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","datos":[{"tipo":"cancha","id":"cancha","equipo1":{"id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","nombre":"PIÑEYRO","formacion":"4-4-2","rol":1,"goles":0,"arco":[{"x":5,"y":0},{"x":6,"y":0},{"x":7,"y":0}]},"equipo2":{"id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","nombre":"PIÑEYRO","formacion":"4-4-2","rol":2,"goles":0,"arco":[{"x":5,"y":19},{"x":6,"y":19},{"x":7,"y":19}]},"sectores":[{"id":6,"x":6,"y":0,"ocupantes":[{"numero":1,"nombre":"Mayer","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","sector_id":6}]},{"id":37,"x":11,"y":2,"ocupantes":[{"numero":2,"nombre":"Lagostena","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","sector_id":37}]},{"id":34,"x":8,"y":2,"ocupantes":[{"numero":3,"nombre":"Asteasuain","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","sector_id":34}]},{"id":30,"x":4,"y":2,"ocupantes":[{"numero":4,"nombre":"Diaz","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","sector_id":30}]},{"id":27,"x":1,"y":2,"ocupantes":[{"numero":5,"nombre":"Freire","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","sector_id":27}]},{"id":71,"x":6,"y":5,"ocupantes":[{"numero":6,"nombre":"Galli","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","sector_id":71}]},{"id":110,"x":6,"y":8,"ocupantes":[{"numero":7,"nombre":"Legaspi","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","sector_id":110}]},{"id":87,"x":9,"y":6,"ocupantes":[{"numero":8,"nombre":"Sabella","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","sector_id":87}]},{"id":81,"x":3,"y":6,"ocupantes":[{"numero":9,"nombre":"Tomsic","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","sector_id":81}]},{"id":121,"x":4,"y":9,"ocupantes":[{"numero":10,"nombre":"Dangiolo","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","es_el_crack":True,"sector_id":121}]},{"id":125,"x":8,"y":9,"ocupantes":[{"numero":11,"nombre":"Dubinsky","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","tiene_la_pelota":True,"sector_id":125}]},{"id":253,"x":6,"y":19,"ocupantes":[{"numero":1,"nombre":"Mayer","equipo_id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","sector_id":253,"tiene_la_pelota":False}]},{"id":222,"x":1,"y":17,"ocupantes":[{"numero":2,"nombre":"Lagostena","equipo_id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","sector_id":222,"tiene_la_pelota":False}]},{"id":225,"x":4,"y":17,"ocupantes":[{"numero":3,"nombre":"Asteasuain","equipo_id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","sector_id":225,"tiene_la_pelota":False}]},{"id":229,"x":8,"y":17,"ocupantes":[{"numero":4,"nombre":"Diaz","equipo_id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","sector_id":229,"tiene_la_pelota":False}]},{"id":232,"x":11,"y":17,"ocupantes":[{"numero":5,"nombre":"Freire","equipo_id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","sector_id":232,"tiene_la_pelota":False}]},{"id":188,"x":6,"y":14,"ocupantes":[{"numero":6,"nombre":"Galli","equipo_id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","sector_id":188,"tiene_la_pelota":False}]},{"id":149,"x":6,"y":11,"ocupantes":[{"numero":7,"nombre":"Legaspi","equipo_id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","sector_id":149,"tiene_la_pelota":False}]},{"id":172,"x":3,"y":13,"ocupantes":[{"numero":8,"nombre":"Sabella","equipo_id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","sector_id":172,"tiene_la_pelota":False}]},{"id":178,"x":9,"y":13,"ocupantes":[{"numero":9,"nombre":"Tomsic","equipo_id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","sector_id":178,"tiene_la_pelota":False}]},{"id":138,"x":8,"y":10,"ocupantes":[{"numero":10,"nombre":"Dangiolo","equipo_id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","es_el_crack":True,"sector_id":138,"tiene_la_pelota":False}]},{"id":134,"x":4,"y":10,"ocupantes":[{"numero":11,"nombre":"Dubinsky","equipo_id":"equipo:TOKEN-4bba80bf-0801-4657-9f2b-f9f4246d4098","tiene_la_pelota":False,"sector_id":134}]}],"ubicacion_pelota":{"id":125,"x":8,"y":9,"ocupantes":[{"numero":11,"nombre":"Dubinsky","equipo_id":"equipo:TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117","tiene_la_pelota":True,"sector_id":125}]},"time_stamp":"1746318406515"},{"tipo":"reloj","reloj":180000}]}
mensaje = MensajeTienesLaPelota(**message)

def get_cancha(mensaje: MensajeTienesLaPelota | MensajeReaccionar) -> CanchaData | None:
    """
    Obtiene el objeto Cancha del mensaje enviado.

    args:
        mensaje: Mensaje del servidor.
    returns:
        CanchaData: Objeto cancha del mensaje
    """
    cancha = None
    try:
        cancha: CanchaData = next(filter(lambda x: type(x) == CanchaData , mensaje.datos))
    except Exception as e:
        print(f'Error al obtener la cancha. Error: {e}')
    
    return cancha

def get_posicion_jugadores(mensaje: MensajeTienesLaPelota | MensajeReaccionar, equipo_id: str) -> List[Dict]:
    """
    Obtiene las posiciones de todos los jugadores de tu equipo.

    args:
        mensaje: Mensaje del servidor.
        equipo_id: Identificador de tu equipo.
    returns:
        List[Dict]: [{'numero': int, 'coord': Coordenada}]
    """
    cancha = get_cancha(mensaje)
    jugadores = []

    if not cancha:
        print('Error al obtener la posicion de los jugadores.')
        return jugadores

    for sector in cancha.sectores:
        jugadores_sector = [{'numero': ocupante.numero, 'coord': Coordenada(x=sector.x, y=sector.y)} for ocupante in sector.ocupantes if ocupante.equipo_id == f'equipo:{equipo_id}']
        jugadores.extend(jugadores_sector)

    return jugadores

#print(get_posicion_jugadores(mensaje=mensaje, equipo_id='TOKEN-3cdf275e-64db-46b7-8308-fa61f90d7117'))

message = {"mensaje_id":"REACCIONAR","destinatario":"TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","datos":[{"mensaje_id":"PATEAR","token":"TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","datos":{"x":7,"y":10}},{"tipo":"cancha","id":"cancha","equipo1":{"id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","nombre":"PIÑEYRO","formacion":"4-4-2","rol":1,"goles":0,"arco":[{"x":5,"y":0},{"x":6,"y":0},{"x":7,"y":0}]},"equipo2":{"id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","nombre":"PIÑEYRO","formacion":"4-4-2","rol":2,"goles":0,"arco":[{"x":5,"y":19},{"x":6,"y":19},{"x":7,"y":19}]},"sectores":[{"id":6,"x":6,"y":0,"ocupantes":[{"numero":1,"nombre":"Mayer","equipo_id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","sector_id":6,"tiene_la_pelota":False}]},{"id":37,"x":11,"y":2,"ocupantes":[{"numero":2,"nombre":"Lagostena","equipo_id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","sector_id":37,"tiene_la_pelota":False}]},{"id":34,"x":8,"y":2,"ocupantes":[{"numero":3,"nombre":"Asteasuain","equipo_id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","sector_id":34,"tiene_la_pelota":False}]},{"id":30,"x":4,"y":2,"ocupantes":[{"numero":4,"nombre":"Diaz","equipo_id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","sector_id":30,"tiene_la_pelota":False}]},{"id":27,"x":1,"y":2,"ocupantes":[{"numero":5,"nombre":"Freire","equipo_id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","sector_id":27,"tiene_la_pelota":False}]},{"id":71,"x":6,"y":5,"ocupantes":[{"numero":6,"nombre":"Galli","equipo_id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","sector_id":71,"tiene_la_pelota":False}]},{"id":137,"x":7,"y":10,"ocupantes":[{"numero":7,"nombre":"Legaspi","equipo_id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","sector_id":137,"tiene_la_pelota":False},{"numero":9,"nombre":"Tomsic","equipo_id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","sector_id":137,"tiene_la_pelota":False}]},{"id":87,"x":9,"y":6,"ocupantes":[{"numero":8,"nombre":"Sabella","equipo_id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","sector_id":87,"tiene_la_pelota":False}]},{"id":134,"x":4,"y":10,"ocupantes":[{"numero":10,"nombre":"Dangiolo","equipo_id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","es_el_crack":True,"sector_id":134,"tiene_la_pelota":False},{"numero":9,"nombre":"Tomsic","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","sector_id":134,"tiene_la_pelota":False}]},{"id":152,"x":9,"y":11,"ocupantes":[{"numero":11,"nombre":"Dubinsky","equipo_id":"equipo:TOKEN-9e576ab0-0fcf-420d-be25-cd7dc1e52b5d","tiene_la_pelota":False,"sector_id":152},{"numero":7,"nombre":"Legaspi","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","sector_id":152,"tiene_la_pelota":False}]},{"id":253,"x":6,"y":19,"ocupantes":[{"numero":1,"nombre":"Mayer","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","sector_id":253,"tiene_la_pelota":False}]},{"id":222,"x":1,"y":17,"ocupantes":[{"numero":2,"nombre":"Lagostena","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","sector_id":222,"tiene_la_pelota":False}]},{"id":225,"x":4,"y":17,"ocupantes":[{"numero":3,"nombre":"Asteasuain","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","sector_id":225,"tiene_la_pelota":False}]},{"id":229,"x":8,"y":17,"ocupantes":[{"numero":4,"nombre":"Diaz","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","sector_id":229,"tiene_la_pelota":False}]},{"id":232,"x":11,"y":17,"ocupantes":[{"numero":5,"nombre":"Freire","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","sector_id":232,"tiene_la_pelota":False}]},{"id":188,"x":6,"y":14,"ocupantes":[{"numero":6,"nombre":"Galli","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","sector_id":188,"tiene_la_pelota":False}]},{"id":172,"x":3,"y":13,"ocupantes":[{"numero":8,"nombre":"Sabella","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","sector_id":172,"tiene_la_pelota":False}]},{"id":137,"x":7,"y":10,"ocupantes":[{"numero":10,"nombre":"Dangiolo","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","es_el_crack":True,"sector_id":137,"tiene_la_pelota":True}]},{"id":134,"x":4,"y":10,"ocupantes":[{"numero":11,"nombre":"Dubinsky","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","tiene_la_pelota":False,"sector_id":134}]}],"ubicacion_pelota":{"id":137,"x":7,"y":10,"ocupantes":[{"numero":10,"nombre":"Dangiolo","equipo_id":"equipo:TOKEN-588fe2e7-f03d-4522-929f-1a483401bcfa","es_el_crack":True,"sector_id":137,"tiene_la_pelota":True}]},"time_stamp":"1746583658540"},{"tipo":"reloj","reloj":934}]}

message['datos'] = message['datos'][1:2]

MensajeReaccionar(**message)