import pygame
from src import constantes

# El auténtico mapa de Pac-Man de 1980 (28x31)

class Mapa:
    def __init__(self):
        self.matriz = constantes.MAPA
        self.tamano_celda = constantes.tamano_celda # 50 píxeles por celda (igual que el personaje)
        self.offset_y = constantes.offset_y_mapa # bajar el mapa y dejar espacio al marcador
        self.muros = [] # Aquí guardaremos los rectángulos de las paredes
        # Creamos un rectángulo muy fino justo por debajo de la fila 11.
        self.puerta_rect = pygame.Rect(constantes.x_puerta, constantes.y_puerta + self.offset_y, 
                                       constantes.ancho_puerta, constantes.alto_puerta)
        self.bolitas = []
        self.super_bolitas = []

        self.construir_mapa()



    def construir_mapa(self):
        #transformar una lista de texto en un plano cartesiano de coordenadas (X, Y)
        for fila_idx, fila in enumerate(self.matriz):
            for col_idx, celda in enumerate(fila):
                x = col_idx * self.tamano_celda
                y = fila_idx * self.tamano_celda + self.offset_y 
                
                # Calculamos el centro exacto de la celda para centrar las bolitas
                centro_x = x + self.tamano_celda // 2
                centro_y = y + self.tamano_celda // 2

                if celda == "1":
                    rect_muro = pygame.Rect(x, y, self.tamano_celda, self.tamano_celda)
                    self.muros.append(rect_muro)
                
                elif celda == "0":
                    # rectángulo pequeño para la bolita normal (6x6 píxeles)
                    rect_bolita = pygame.Rect(0, 0, 6, 6)
                    rect_bolita.center = (centro_x, centro_y)
                    self.bolitas.append(rect_bolita)
                    
                elif celda == "2":
                    # rectángulo grande para la super-bolita (14x14 píxeles)
                    rect_super = pygame.Rect(0, 0, 14, 14)
                    rect_super.center = (centro_x, centro_y)
                    self.super_bolitas.append(rect_super)
                    self.muros.append(rect_muro)

    def dibujar(self, pantalla):
        # Dibujamos cada muro de color azul (luego pondré directamente el sprite)
        color_muro = (33, 33, 255) 
        for muro in self.muros:
            pygame.draw.rect(pantalla, color_muro, muro)
            # Dibujamos un borde para que se vea estilo retro
            pygame.draw.rect(pantalla, (0, 0, 0), muro, 2)
        #Dibujamos la puerta del spawn de los fantasmas
        pygame.draw.rect(pantalla, (190, 179, 67), self.puerta_rect)
        # Color clásico de las bolitas de Pac-Man (un tono melocotón/crema)
        color_comida = (255, 184, 174) 
        for bolita in self.bolitas:
            pygame.draw.circle(pantalla, color_comida, bolita.center, 3)
        for super_bolita in self.super_bolitas:
            pygame.draw.circle(pantalla, color_comida, super_bolita.center, 7)