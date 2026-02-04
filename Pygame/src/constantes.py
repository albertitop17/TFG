ancho_ventana = 100
alto_ventana = 100

alto_personaje = 50
ancho_personaje = 50
#tambien podria definir colores aqui

color_fondo = (0, 0, 100)

velocidad = 15
FPS = 60

escala_personaje = 0.9

# DICCIONARIO DE ANIMACIONES
# Formato: 'clave': [(x, y, ancho, alto), (x, y, ancho, alto)...]
# NOTA: Pon aquí los números reales que sacaste con el script buscador.
PACMAN_COORDENADAS = {
    'quieto': [(0, 0, 16, 16)], 
    'derecha': [ 
        (17, 0, 16, 16), #medio abierta dr
        (0, 0, 16, 16), #muy abierta dr
        (17, 0, 16, 16), #medio abierta dr
        (34, 0, 16, 16) #cerrada 
    ],
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
}