import pygame
from src import constantes

class Humano:
    def __init__(self):
        #empieza quieto
        self.dx = 0
        self.dy = 0

    def obtener_movimiento(self):
        
        teclas = pygame.key.get_pressed() #obtener el estado de todas las teclas
        if teclas[pygame.K_LEFT]: #si la tecla de flecha izquierda está presionada
            self.dx = -constantes.velocidad
            self.dy = 0
        elif teclas[pygame.K_RIGHT]: #si la tecla de flecha derecha está presionada
            self.dx = constantes.velocidad   
            self.dy = 0
        elif teclas[pygame.K_UP]: #si la tecla de flecha arriba está presionada
            self.dx = 0
            self.dy = -constantes.velocidad
        elif teclas[pygame.K_DOWN]: #si la tecla de flecha abajo está presionada
            self.dx = 0
            self.dy = constantes.velocidad

        return self.dx, self.dy
    
class IA:
    def obtener_movimiento(self):
        #aqui va la logica de movimiento de la IA
        dx = 0
        dy = 0
        return dx, dy