import pygame
from src import constantes

# Matriz de 24 columnas x 12 filas
MAPA = [
    "111111111111111111111111",
    "100000000001100000000001",
    "101111011101101110111101",
    "101111011101101110111101",
    "100000000000000000000001",
    "101111010111111010111101",
    "100000010001100010000001",
    "111111011101101110111111",
    "000001010000000010100000",
    "111111010111111010111111",
    "100000000001100000000001",
    "111111111111111111111111"
]

class Mapa:
    def __init__(self):
        self.matriz = MAPA
        self.tamano_celda = constantes.celda # 50 píxeles por celda (igual que el personaje)
        self.muros = [] # Aquí guardaremos los rectángulos de las paredes
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
        # Dibujamos cada muro de color azul
        color_muro = (33, 33, 255) 
        for muro in self.muros:
            pygame.draw.rect(pantalla, color_muro, muro)
            # Dibujamos un borde para que se vea estilo retro
            pygame.draw.rect(pantalla, (0, 0, 0), muro, 2)