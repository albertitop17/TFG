import pygame
from src import constantes

# El auténtico mapa de Pac-Man de 1980 (28x31)
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
    "       0  1      1  0       ",
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
class Mapa:
    def __init__(self):
        self.matriz = MAPA
        self.tamano_celda = constantes.tamano_celda # 50 píxeles por celda (igual que el personaje)
        self.muros = [] # Aquí guardaremos los rectángulos de las paredes
        # Creamos un rectángulo muy fino justo por debajo de la fila 11.
        self.puerta_rect = pygame.Rect(constantes.x_puerta, constantes.y_puerta, 
                                       constantes.ancho_puerta, constantes.alto_puerta)
        self.construir_mapa()



    def construir_mapa(self):
        # Recorremos la lista para convertir los "1" en muros
        #transformar una lista de texto en un plano cartesiano de coordenadas (X, Y)
        for fila_idx, fila in enumerate(self.matriz):
            for col_idx, celda in enumerate(fila):
                if celda == "1":
                    # Calculamos la posición X e Y multiplicando por 50
                    x = col_idx * self.tamano_celda
                    y = fila_idx * self.tamano_celda
                    # Creamos el rectángulo y lo guardamos
                    rect_muro = pygame.Rect(x, y, self.tamano_celda, self.tamano_celda)
                    self.muros.append(rect_muro)

    def dibujar(self, pantalla):
        # Dibujamos cada muro de color azul (luego pondré directamente el sprite)
        color_muro = (33, 33, 255) 
        for muro in self.muros:
            pygame.draw.rect(pantalla, color_muro, muro)
            # Dibujamos un borde para que se vea estilo retro
            pygame.draw.rect(pantalla, (0, 0, 0), muro, 2)
        pygame.draw.rect(pantalla, (190, 179, 67), self.puerta_rect)