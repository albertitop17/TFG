ancho_ventana = 1200
alto_ventana = 600

alto_personaje = 50
ancho_personaje = 50
#tambien podria definir colores aqui

color_fondo = (0, 0, 0)

velocidad = 5 
FPS = 60

escala_personaje = 10/3

# DICCIONARIO DE ANIMACIONES
# Formato: 'clave': [(x, y, ancho, alto), (x, y, ancho, alto)...]
# NOTA: Pon aquí los números reales que sacaste con el script buscador.
PACMAN_COORDENADAS = {
    'quieto': [(0, 0, 16, 16)], 
    'derecha': [ 
        (18, 0, 15, 15), #medio abierta dr
        (1, 0, 15, 15), #muy abierta dr
        (18, 0, 15, 15), #medio abierta dr
        (35, 0, 15, 15) #cerrada 
    ]
}

"""
    ,
    'izquierda': [
        (17, 17, 16, 16), # medio abierta iz
        (0, 17, 16, 16), # muy abierta iz
        (17, 17, 16, 16), # medio abierta iz
        (34, 0, 16, 16) # cerrada
    ],
    'arriba': [
        (17, 34, 16, 16), # medio abierta ar
        (0, 34, 16, 16), # muy abierta ar
        (17, 34, 16, 16), # medio abierta ar
        (34, 0, 16, 16) # cerrada
    ],
    'abajo': [
        (17, 51, 16, 16), # medio abierta ab
        (0, 51, 16, 16), # muy abierta ab
        (17, 51, 16, 16), # medio abierta ab
        (34, 0, 16, 16) # cerrada
    ]
    """

FANTASMA_ROJO_COORDENADAS = {
    'rojo': {
        'derecha': [(1, 68, 15, 15), (18, 68, 15, 15)],
        'izquierda': [(35, 68, 15, 15), (52, 68, 15, 15)],
        'arriba': [(69, 68, 15, 15), (86, 68, 15, 15)],
        'abajo': [(103, 68, 15, 15), (120, 68, 15, 15)]
    },
    'rosa': {
        'derecha': [(1, 85, 15, 15), (18, 85, 15, 15)],
        'izquierda': [(35, 85, 15, 15), (52, 85, 15, 15)],
        'arriba': [(69, 85, 15, 15), (86, 85, 15, 15)],
        'abajo': [(103, 85, 15, 15), (120, 85, 15, 15)]
    },
    'azul': {
        'derecha': [(1, 102, 15, 15), (18, 102, 15, 15)],
        'izquierda': [(35, 102, 15, 15), (52, 102, 15, 15)],
        'arriba': [(69, 102, 15, 15), (86, 102, 15, 15)],
        'abajo': [(103, 102, 15, 15), (120, 102, 15, 15)]
    },
    'naranja': {
        'derecha': [(1, 119, 15, 15), (18, 119, 15, 15)],
        'izquierda': [(35, 119, 15, 15), (52, 119, 15, 15)],
        'arriba': [(69, 119, 15, 15), (86, 119, 15, 15)],
        'abajo': [(103, 119, 15, 15), (120, 119, 15, 15)]
    }
}



#MAPA

#multiplo de la velocidad para que el personaje pueda alinearse perfectamente con las paredes al girar, sino se quedaría atascado al intentar girar justo antes de un muro.
#Además, es el mismo tamaño que el personaje para que encaje perfectamente en las celdas del mapa.
tamano_celda = 50 