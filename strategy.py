from typing import Dict, List, Tuple, TypedDict
import logging
import random
from mensajes import (  MensajeTienesLaPelota,
                        MensajeReaccionar,
                        Coordenada,
                        Ocupante,
                        Coordenada,
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
from utils import (   Movimiento,
                      get_cancha,
                      patear_al_arco,
                      get_posicion_arco,
                      get_ubicacion_pelota,
                      distancia,
                      get_posicion_jugadores,
                      jugador_mas_cercano_adversario,
                      jugador_mas_cercano_posicion
                    )
import datetime

logger = logging.getLogger('strategy')
#random.seed(int(datetime.datetime.now()))

# Funcion principal de la estrategia ofensiva
  
def estrategia_ofensiva(token: str, mensaje: MensajeTienesLaPelota, equipo_id: str) -> MensajeCorrer | MensajePasarPelota | MensajePatear:
    """
    Estrategia ofensiva del equipo.
    
    Objetivo: Realizar un ataque con varios jugadores.
    
    Funcionamiento: Realizar una serie de pases entre jugadores de equipo hasta llegar a una zona de remate optima.
    El jugador que tiene la pelota se la pasara al jugador mas cercano. Asi hasta que lleguen a la zona optima de disparo.
    Cuando la pelota esta dentro del area de remate, el jugador que tiene la pelota, patea a una posicion aleatoria del arco.

    args:
        token: Token del equipo que ataca.
        mensaje (MensajeTienesLaPelota): Mensaje recibido del servidor.
        equipo_id (str): Identificador de tu equipo.

    returns:
        accion: Pase / Patear pelota dependiendo de la situacion.
    """
    posibles_atacantes = [7, 8, 10]     # Números de los jugadores designados para el ataque
    jugadores_del_equipo = get_posicion_jugadores(mensaje, equipo_id)
    zona_de_remate = definir_zona_de_remate(mensaje, equipo_id)
    
    cancha = get_cancha(mensaje)
    if not cancha:
        logger.error("No se pudo obtener la cancha")
        return []

    coord_pelota, jugador_con_pelota = get_ubicacion_pelota(mensaje)

    if not coord_pelota and not jugador_con_pelota:
        logger.warning("No se pudo obtener info suficiente para realizar un pase")
        return None

    equipo_es_equipo1 = cancha.equipo1.id == f"equipo:{equipo_id}"
    arco_rival = cancha.equipo2.arco if equipo_es_equipo1 else cancha.equipo1.arco
    coord_random_arco = elegir_punto_aleatorio_arco(arco_rival)

    # Si la pelota esta o supera la zona optima de remate, entonces el jugador que la tiene patea
    if coord_pelota.y >= zona_de_remate['limite_inferior'] and coord_pelota.y <= zona_de_remate['limite_superior']:
        logger.info("En zona de remate. Se ejecuta el disparo al arco")
        arco_rival = get_posicion_arco(mensaje, equipo_id, es_adversario=True)
        coord_random_arco = elegir_punto_aleatorio_arco(arco_rival)
        return patear(token, coord=coord_random_arco)
    
    # Si hay un jugador con la pelota, busca el jugador mas cercano para pasarsela
    if jugador_con_pelota:
        proximo_jugador = jugador_mas_cercano_posicion(mensaje, equipo_id, coord_pelota)
        logger.info(f'Jugador mas cercano para pasarle la pelota {proximo_jugador}')
        return pasar_pelota(token, proximo_jugador)
    
    # Si la pelota esta en movimiento, los jugadores designados para atacar se mueven
    # TODO: Ver de mover a reaccionar o sacar.
    elif coord_pelota:
        # Posicionamiento ofensivo del equipo
        posicionamiento_ataque = pasar_al_ataque(token, mensaje, posibles_atacantes)
        movimientos = posicionamiento_ataque
        jugador = jugador_mas_cercano_posicion(mensaje, equipo_id, coord_pelota)
        logger.info(f'Jugador mas cercano a la pelota {jugador}')
        movimientos.append(
            Movimiento(jugador_numero=jugador,
                       x=coord_pelota.x,
                       y=coord_pelota.y))

        if movimientos:
            return correr(token, datos={"movimientos": movimientos})

    # Si no ocurre nada de lo anterior, los jugadores vuelven a unas posiciones anteriores
    else:
        logger.error(f'Error al buscar pelota. Mensaje: {mensaje}')
        logger.info(f'Replegando equipo. Delanteros regresan...')
        return correr(token, datos={"movimientos": [
            Movimiento(jugador_numero=7,
                       x=1,
                       y=1),
            Movimiento(jugador_numero=8,
                       x=1,
                       y=3),
            Movimiento(jugador_numero=10,
                       x=1,
                       y=5)
        ]})

    # Obtenemos la distancia entre la pelota y el arco
    distancia_arco = distancia(coord_pelota, arco_rival)

    # Buscamos opciones de pase hasta llegar a la zona optima
    jugador_objetivo = None
    mejor_distancia = distancia_arco

    for jugador in jugadores_del_equipo:
        if jugador["numero"] == jugador_con_pelota or jugador["numero"] == 1:
            continue  # No me paso a mí mismo ni al arquero
        if jugador["coord"].x > coord_pelota.x and coord_pelota.x < zona_de_remate:  # Está adelante
            distancia_receptor = distancia(coord_pelota, jugador["coord"])
            if distancia_receptor < mejor_distancia:
                mejor_distancia = distancia_receptor
                jugador_objetivo = jugador["numero"]
                logger.error("ERROR")

    if jugador_objetivo:
        return pasar_pelota(token, jugador_objetivo)

def elegir_punto_aleatorio_arco(arco: Tuple[Coordenada, Coordenada, Coordenada]) -> Coordenada:
    """
    Devuelve una coordenada aleatoria de las tres que forman el arco

    args:
        arco: Lista de las coordenadas del arco.

    returns:
        coordenada: Una coordenada del arco.
    """
    return random.choice(arco)

# Funcion de movimiento de jugadores en ataque
def pasar_al_ataque(token: str, mensaje: MensajeTienesLaPelota, atacantes: List[int]) -> List[Movimiento]:
    """
    Mueve una cantidad de jugadores a posiciones ofensivas, preparando una jugada de ataque.

    args:
        token: Token del equipo que ataca.
        mensaje: Mensaje recibido del servidor.
        equipo_id (str): Identificador de tu equipo.
        atacantes (List[int]): Lista de numeros de jugadores al ataque.

    returns:
        lista: Movimientos de jugadores que atacan.
    """
    movimientos = []
    cancha = get_cancha(mensaje)
    if not cancha:
        logger.error("No se pudo obtener la cancha.")
        return None

    # Definimos posiciones ofensivas en el campo contrario
    for idx, jugador in enumerate(atacantes):
        # Ejemplo: ubicaciones ofensivas escalonadas hacia el arco rival
        pos_x = 8 + idx  # más adelante en el campo
        pos_y = 2 + idx  # evitar que estén todos en la misma línea
        movimientos.append(Movimiento(jugador_numero = jugador, x = pos_x, y = pos_y))

    return movimientos

# Funcion para definir la zona optima de remate
def definir_zona_de_remate(mensaje: MensajeTienesLaPelota, equipo_id: str) -> dict:
    posicion_arco_rival = get_posicion_arco(mensaje, equipo_id, True)
    if not posicion_arco_rival or len(posicion_arco_rival) != 3:
        logger.error("No se pudo obtener la posición del arco rival.")
        return None

    posicion_arco_rival = posicion_arco_rival[1]

    # Calcular la coordenada y central del arco
    rango_tiro = 6

    if posicion_arco_rival.y == 0:
        limite_inferior = posicion_arco_rival.y
        limite_superior = posicion_arco_rival.y + rango_tiro
    elif posicion_arco_rival.y == 19:
        limite_inferior = posicion_arco_rival.y - rango_tiro
        limite_superior = posicion_arco_rival.y

    # Defino la zona de remate
    zona_de_remate = {'limite_inferior': limite_inferior, 'limite_superior': limite_superior}

    return zona_de_remate