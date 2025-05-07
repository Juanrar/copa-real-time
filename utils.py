from math import sqrt
from typing import Dict, List, Tuple, TypedDict
import logging
from mensajes import (
                      MensajeTienesLaPelota,
                      MensajeReaccionar,
                      Coordenada,
                      Ocupante,
                      CanchaData,
                      MensajeCorrer,
                      MensajePatear,
                      MensajePasarPelota,
                      MensajeMarcarAdversario,
                      ClientMessage,
                      correr,
                      pasar_pelota,
                      patear,
                      marcar_adversario
                      )

logger = logging.getLogger(__name__)

class Movimiento(TypedDict):
    jugador_numero: int
    x: int
    y: int

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
        logger.error(f'Error al obtener la cancha. Error: {e}')
    
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
        logger.error('Error al obtener la posicion de los jugadores.')
        return jugadores

    for sector in cancha.sectores:
        jugadores_sector = [{'numero': ocupante.numero, 'coord': Coordenada(x=sector.x, y=sector.y)} for ocupante in sector.ocupantes if ocupante.equipo_id == f'equipo:{equipo_id}']
        jugadores.extend(jugadores_sector)

    return jugadores

def get_posicion_adversarios(mensaje: MensajeTienesLaPelota | MensajeReaccionar, equipo_id: str) -> List[Dict]:
    """
    Obtiene las posiciones de todos los jugadores del equipo rival.

    args:
        mensaje: Mensaje del servidor.
        equipo_id: Identificador de tu equipo.
    returns:
        List[Dict]: [{'numero': int, 'coord': Coordenada}]
    """
    cancha = get_cancha(mensaje)
    adversarios = []

    if not cancha:
        logger.error('Error al obtener la posicion de los adversarios.')
        return adversarios

    for sector in cancha.sectores:
        adversarios_sector = [{'numero': ocupante.numero, 'coord': Coordenada(x=sector.x, y=sector.y)} for ocupante in sector.ocupantes if ocupante.equipo_id != f'equipo:{equipo_id}']
        adversarios.extend(adversarios_sector)

    return adversarios

def get_posicion(mensaje: MensajeTienesLaPelota | MensajeReaccionar, equipo_id: str, n_jugador: int, es_adversario: bool) -> Coordenada | None:
    """
    Obtiene la posicion de un jugador/adversario particular. En caso de no encontrarlo devuelve None

    args:
        args:
        mensaje: Mensaje del servidor.
        equipo_id (str): Identificador de tu equipo.
        n_jugador (int): Identificador del jugador.
        es_adversario (bool): Flag para indicar de que equipo es el jugador.
    returns:
        Coordenada: Posicion del jugador/adversario.
    """
    if es_adversario:
        posiciones = get_posicion_adversarios(mensaje, equipo_id=equipo_id)
    else:
        posiciones = get_posicion_jugadores(mensaje, equipo_id=equipo_id)

    for jugador in posiciones:
        if jugador['numero'] == n_jugador:
            return jugador['coord']
    
    return None

def get_posicion_arco(mensaje: MensajeTienesLaPelota | MensajeReaccionar, equipo_id: str, es_adversario: bool) -> Coordenada | None:
    """
    Devuelve la posicion central del arco.

    args:
        mensaje: Mensaje del servidor.
        equipo_id (str): Identificador de tu equipo.
        es_adversario (bool): Flag para indicar de que equipo se busca el arco.
    returns:
        Coordenada: Posicion central del arco.
    """

    cancha = get_cancha(mensaje)

    if not cancha:
        logger.error(f'Error al obtener el arco. Mensaje: {mensaje}')
        return None
    
    if es_adversario and cancha.equipo1.id != f'equipo:{equipo_id}':
        return cancha.equipo1.arco[1]
    else:
        return cancha.equipo2.arco[1]

def get_ubicacion_pelota(mensaje: MensajeReaccionar) -> Tuple[Coordenada, int] | None:
    """
    Obtiene la ubicacion de la pelota a partir de un mensaje.
    Tambien devuelve el jugador que la posee en caso de corresponder.
    En caso que no la tenga ningun jugador ni este en la posicion UbicacionPelota se asume que esta en el aire.

    args:
        mensaje (MensajeReaccionar): Mensaje del servidor.
    returns:
        Tuple[Coordenada, int]: Coordenada y numero del jugador que tiene la pelota.
        None: En caso de que se produzca algun error o no se encuentre la pelota se devuelve None.
    """
    cancha = get_cancha(mensaje)
        
    if not cancha:
        logger.error(f'Error al obtener la posicion de la pelota. Mensaje: {mensaje}')
        return (None, None)
    
    if cancha.ubicacion_pelota.esta_la_pelota == True:
        return (Coordenada(x=cancha.ubicacion_pelota.x, y=cancha.ubicacion_pelota.y), None)

   # Si la pelota no esta en el suelo la debe tener algun jugador 
    for sector in cancha.sectores:
        for ocupante in sector.ocupantes:
            if ocupante.tiene_la_pelota == True:
                return (Coordenada(x=sector.x, y=sector.y), ocupante.numero)
                
    # Valor por default en caso de no encontrar la pelota
    logger.info(f'Pelota en el aire.')
    return (Coordenada(x=cancha.ubicacion_pelota.x, y=cancha.ubicacion_pelota.y), None)

def distancia(coord1: Coordenada, coord2: Coordenada):
    return sqrt((coord1.x - coord2.x)**2 + (coord1.y - coord2.y)**2)

def jugador_mas_cercano_posicion(mensaje: MensajeReaccionar | MensajeTienesLaPelota, equipo_id: str, coord: Coordenada) -> int | None:
    """
    Obtiene al jugador mas cercano a una posicion utilizando la distancia euclidiana.

    args:
        mensaje: Mensaje del servidor.
        equipo_id (str): Identificador de tu equipo.
        coord (Coordenada): Posicion.

    returns:
        int: Numero del jugador mas cercano.
    """
    posiciones = get_posicion_jugadores(mensaje, equipo_id=equipo_id)

    if len(posiciones) == 0:
        logger.error('Error al obtener el jugador mas cercano.')
        return None
    
    distancias = {jugador['numero']: distancia(coord1=jugador['coord'], coord2=coord) for jugador in posiciones}

    # Esto obtiene el primer jugador que encuentre con la menor distancia
    jugador = min(distancias, key=distancias.get)

    return jugador
    
def jugador_mas_cercano_adversario(mensaje: MensajeReaccionar | MensajeTienesLaPelota, equipo_id: str, adversario: int) -> int:
    """
    Obtiene al jugador mas cercano a un adversario utilizando la distancia euclidiana.

    args:
        mensaje: Mensaje del servidor.
        equipo_id (str): Identificador de tu equipo.
        adversario (int): Numero del adversario.

    returns:
        int: Numero del jugador mas cercano.
    """
    posicion_rival = get_posicion(mensaje, equipo_id=equipo_id, n_jugador=adversario, es_adversario=True)

    if posicion_rival is None:
        return None
    
    return jugador_mas_cercano_posicion(mensaje=mensaje, equipo_id=equipo_id, coord=posicion_rival)

def buscar_pelota(token: str, mensaje: MensajeReaccionar, equipo_id: str) -> MensajeCorrer | MensajeMarcarAdversario:

    coord, adversario = get_ubicacion_pelota(mensaje)

    if adversario:
        jugador = jugador_mas_cercano_adversario(mensaje, equipo_id=equipo_id, adversario=adversario)
        logger.info(f'Jugador mas cercano {jugador}')
        return marcar_adversario(token, jugador=jugador, adversario=adversario)  
    
    elif coord:
        jugador = jugador_mas_cercano_posicion(mensaje, equipo_id=equipo_id, coord=coord)
        logger.info(f'Jugador mas cercano {jugador}')
        return correr(token, datos={"movimientos": [
            Movimiento(jugador_numero=jugador,
                       x=coord.x,
                       y=coord.y)
        ]})
    
    else:
        logger.error(f'Error al buscar pelota. Mensaje: {mensaje}')
        return correr(token, datos={"movimientos": [
            Movimiento(jugador_numero=3,
                       x=1,
                       y=1)
        ]})
    
def patear_al_arco(token: str, mensaje: MensajeTienesLaPelota, equipo_id: str):

    coordenada_arco = get_posicion_arco(mensaje, equipo_id=equipo_id, es_adversario=True)

    if coordenada_arco:
        return patear(token, coord=coordenada_arco)
    else:
        logger.error(f'Error al encontrar la coordenada del arco. Mensaje: {mensaje}')
        return patear(token, coord=Coordenada(x=10, y=10))




