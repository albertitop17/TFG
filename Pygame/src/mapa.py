import pygame
from src import constantes

class Mapa:
    '''
    Transoforma la matriz lógica de strings de constantes.py en objetos físicos de Pygame (pygame.Rect)
    '''
    def __init__(self):
        self.matriz = constantes.MAPA
        self.tamano_celda = constantes.tamano_celda 
        self.offset_y = constantes.offset_y_mapa # Desplazamos el mapa en el eje Y para dejar espacio al HUD arriba

        self.muros = [] # Lista de pygame.Rect que formarán los muros.
        self.bolitas = [] 
        self.super_bolitas = [] 

        # Barrera del spawn (se podrá atravesar en momentos precisos)
        self.puerta_rect = pygame.Rect(constantes.x_puerta, constantes.y_puerta + self.offset_y, 
                                       constantes.ancho_puerta, constantes.alto_puerta)
        self.construir_mapa()

    def construir_mapa(self):
        '''
        Itera sobre la matriz lógica generando las hitboxes del juego
        '''
        for fila_idx, fila in enumerate(self.matriz):
            for col_idx, celda in enumerate(fila):

                # Transformamos los índices de la matriz en píxeles de la pantalla
                x = col_idx * self.tamano_celda
                y = fila_idx * self.tamano_celda + self.offset_y 
                
                # Calculamos el centro exacto de la celda para centrar las bolitas
                centro_x = x + self.tamano_celda // 2
                centro_y = y + self.tamano_celda // 2

                if celda == "1": # creamos el muro que ocupará toda la celda
                    rect_muro = pygame.Rect(x, y, self.tamano_celda, self.tamano_celda)
                    self.muros.append(rect_muro)
                
                elif celda == "0": # creamos una pequeña bolita en el centro de ña celda
                    rect_bolita = pygame.Rect(0, 0, 6, 6)
                    rect_bolita.center = (centro_x, centro_y)
                    self.bolitas.append(rect_bolita)
                    
                elif celda == "2": # creamos una super-bolita en el centro de la celda
                    rect_super = pygame.Rect(0, 0, 14, 14)
                    rect_super.center = (centro_x, centro_y)
                    self.super_bolitas.append(rect_super)

    def dibujar(self, pantalla):
        '''
        Se ocupa del renderizado del mapa (con intención de sustituir por sprites a futuro)
        '''
        # Dibujamos cada muro de color azul
        color_muro = (33, 33, 255) 
        for muro in self.muros:
            pygame.draw.rect(pantalla, color_muro, muro) 
            pygame.draw.rect(pantalla, (0, 0, 0), muro, 2) # Dibujamos un borde para que se vea estilo retro
        pygame.draw.rect(pantalla, (190, 179, 67), self.puerta_rect) # Dibujamos la puerta del spawn de los fantasmas
        
        # Dibujamos las bolitas y super-bolitas
        color_comida = (255, 184, 174) 
        for bolita in self.bolitas:
            pygame.draw.circle(pantalla, color_comida, bolita.center, 3)
        for super_bolita in self.super_bolitas:
            pygame.draw.circle(pantalla, color_comida, super_bolita.center, 7)