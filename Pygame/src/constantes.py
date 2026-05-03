'''
Configuración y constantes del juego Pacman.
Agrupamos variables estátricas como dimensiones, velocidades, coordenadas de sprites, etc. 
En caso de querer modificar una variable, solo se tendrá que cambiar aquí.
'''

# DIMENSIONES Y CUADRÍCULA ------------

#  El tamaño de la celda es vital que encaje tanto con el mapa como con los personajes
tamano_celda = 20

# Dimensiones del mapa original (28 columnas x 35 filas)
ancho_ventana = 28 * tamano_celda  # 560 pixeles
alto_ventana = 35 * tamano_celda   # 700 pixeles

# Espacio reservado en la parte superior para el HUD (marcador y vidas)
offset_y_mapa = 3 * tamano_celda  # 60 pixeles

# Los personajes medirán exactamente lo mismo que la celda, haciendo posible que accedan de forma precisa
alto_personaje = tamano_celda
ancho_personaje = tamano_celda

# Guardamos las coordenadas y dimensiones de la puerta del refugio de los fantasmas (las guardamos discretizadas)
x_puerta = 13 * tamano_celda #columnas 13 y 14
y_puerta = 11 * tamano_celda + 3 # fila 11 (lo bajamos 3 píxeles)
ancho_puerta = 2 * tamano_celda 
alto_puerta = 6

# Fila en la que se encuentra el túnel del mapa (usado para la lógica de teletransporte)
tunel = 13 # fila del túnel ajustada al offset

# FÍSICAS Y RENDERIZADO ------------------

# Regla fundamental: la velocidad debe ser divisor de 'tamano_celda' para que el personaje pueda alinearse perfectamente con las paredes al girar
velocidad = 2 # (20 % 2 == 0)
velocidad_asustados = 1 # los fantasmas asustados van a la mitad de velocidad
FPS = 60 

# Escalamos los sprites a nuestro tamaño de celda
escala_personaje = tamano_celda / 15.0


# Multiplicador para calcular cuántos pasos forman una celda entera en función de nuestra velocidad (usado en calcular_mejor_dir en controladores)
factor_proyectar = tamano_celda // velocidad

# Temporizador de la máquina de estados de los fantasmas (Dispersión <-> Persecución) 
duraciones_oleada = [7, 20]

# Activador del modo Debug: dibujado de rutas y objetivos 
DEBUG = False

# GRAFICADO (DICCIONARIO DE ANIMACIONES)

colores_debug = {
        'rojo': (255, 0, 0),
        'rosa': (255, 184, 255),
        'azul': (0, 255, 255),
        'naranja': (255, 184, 82)
    }

# Cooldown de las animaciones (en ms)
cooldown_animaciones = 120

# Formato: 'clave': [(x, y, ancho, alto),...] del Sprite Sheet
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
        (137, 68, 15, 15), 
        (154, 68, 15, 15)  
    ],
    'asustado_blanco': [
        (171, 68, 15, 15), 
        (188, 68, 15, 15)  
    ],
    'ojos': {
        'derecha':   (137, 85, 15, 15),
        'izquierda': (154, 85, 15, 15),
        'arriba':    (171, 85, 15, 15),
        'abajo':     (188, 85, 15, 15)
    }
}

# Matrices de mapas: 0 = Bolita, 1 = Muro, 2 = Super-Bolita, " " = Túnel

MAPA = [                        
    "1111111111111111111111111111",
    "1000000000000110000000000001",
    "1011110111110110111110111101",
    "1211110111110110111110111121",
    "1011110111110110111110111101",
    "1000000000000000000000000001",
    "1011110110111111110110111101",
    "1011110110111111110110111101",
    "1000000110000110000110000001",
    "111111011111 11 111110111111",
    "     1011          1101     ",
    "     1011 111  111 1101     ",
    "111111011 1      1 110111111",
    " 0    0   1      1   0    0 ",
    "111111011 1      1 110111111",
    "     1011 11111111 1101     ",
    "     1011          1101     ",
    "111111011 11111111 110111111",
    "1000000000000110000000000001",
    "1011110111110110111110111101",
    "1011110111110110111110111101",
    "1200110000000  0000000110021",
    "1110110110111111110110110111",
    "1110110110111111110110110111",
    "1000000110000110000110000001",
    "1011111111110110111111111101",
    "1011111111110110111111111101",
    "1000000000000000000000000001",
    "1111111111111111111111111111"
]

MAPA2 = [ 
    "1111111111111111111111111111",
    "1            11            1",
    "1 1111 11111 11 11111 1111 1",
    "1 1111 11111 11 11111 1111 1",
    "1 1111 11111 11 11111 1111 1",
    "1                          1",
    "101111 11 11111111 11 1111 1",
    "1 1111 11 11111111 11 1111 1",
    "1      11    11    11      1",
    "111111 11111 11 11111 111111",
    "     1 11          11 1     ",
    "     1 11 111  111 11 1     ",
    "111111 11 1      1 11 111111",
    "  0       1      1       0  ",  # <--- Fila 13
    "111111 11 1      1 11 111111",
    "     1 11 11111111 11 1     ",
    "     1 11          11 1     ",
    "111111 11 11111111 11 111111",
    "1            11       0    1",
    "1 1111 11111 11 11111 1111 1",
    "1 1111 11111 11 11111 1111 1",
    "1   11                11   1",
    "111 11 11 11111111 11 11 111",
    "111 11 11 11111111 11 11 111",
    "1      110   11    11      1",
    "1 1111111111 11 1111111111 1",
    "1 1111111111 11 1111111111 1",
    "1                          1",
    "1111111111111111111111111111"
]

columnas_mapa = len(MAPA[0])
filas_mapa = len(MAPA)
ancho_px = columnas_mapa * tamano_celda
y_tunel_px = (tunel * tamano_celda) + offset_y_mapa