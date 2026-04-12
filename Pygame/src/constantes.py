#MAPA

#multiplo de la velocidad para que el personaje pueda alinearse perfectamente con las paredes al girar, sino se quedaría atascado al intentar girar justo antes de un muro.
#Además, es el mismo tamaño que el personaje para que encaje perfectamente en las celdas del mapa.
tamano_celda = 20

ancho_ventana = 28 * tamano_celda # 700
alto_ventana = 35 * tamano_celda # 900

# Bajamos el mapa 3 celdas (60 píxeles) para dejar espacio al marcador superior
offset_y_mapa = 3 * tamano_celda

#el personaje medirá lo mismo que el tamaño de la celda 
alto_personaje = tamano_celda
ancho_personaje = tamano_celda

#tambien podria definir colores aqui
color_fondo = (0, 0, 0)

#la velocidad debe ser divisor de tamano_celda para que el personaje pueda alinearse 
# perfectamente con las paredes al girar, sino se quedaría atascado al intentar girar justo antes de un muro.
velocidad = 2 
velocidad_asustados = 1 # los fantasmas asustados van a la mitad de velocidad
FPS = 50

duraciones_oleada = [7, 20] # Duración de cada oleada en segundos (Dispersión, Persecución)

#escalamos el spritr de 15/16px al tamaño de la celda

escala_personaje = tamano_celda / 15.0 

factor_proyectar = tamano_celda // velocidad
DEBUG = False  # Cambia a True cuando hagamos el debug

# puerta spawn fantasmas
# La puerta está bajo la fila 11 (fila 10 en índice 0), columnas 13 y 14.
x_puerta = 13 * tamano_celda
y_puerta = 11 * tamano_celda + 3 # Lo bajamos 3 píxeles para que se vea
ancho_puerta = 2 * tamano_celda
alto_puerta = 6


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

FANTASMA_ESTADOS_ESPECIALES = {
    'asustado_azul': [
        (137, 68, 15, 15), # Azul frame 1
        (154, 68, 15, 15)  # Azul frame 2
    ],
    'asustado_blanco': [
        (171, 68, 15, 15), # Blanco frame 1 (parpadeo de aviso)
        (188, 68, 15, 15)  # Blanco frame 2
    ],
    'ojos': {
        'derecha':   (137, 85, 15, 15),
        'izquierda': (154, 85, 15, 15),
        'arriba':    (171, 85, 15, 15),
        'abajo':     (188, 85, 15, 15)
    }
}