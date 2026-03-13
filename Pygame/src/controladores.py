import pygame
from src import constantes
import random

class Humano:
    def __init__(self):
        #empieza quieto
        self.dx = 0
        self.dy = 0

    def obtener_movimiento(self, _ ,__):
        
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
    
class ControladorFantasmaAleatorio:
    def __init__(self):
        # El fantasma arranca moviéndose hacia la derecha por defecto
        self.dx = constantes.velocidad
        self.dy = 0

    def obtener_movimiento(self, rect_actual, muros):
        # 1. MAGIA MATEMÁTICA: ¿Estamos en un "Nodo" (intersección)?
        # Si nuestra posición no es múltiplo del tamaño de celda, estamos a mitad de un pasillo.
        # Por tanto, no tomamos decisiones, seguimos rectos.
        if rect_actual.x % constantes.tamano_celda != 0 or rect_actual.y % constantes.tamano_celda != 0:
            return self.dx, self.dy

        # 2. Si estamos alineados (resto = 0), evaluamos las aristas (caminos) válidas
        direcciones_posibles = [
            (constantes.velocidad, 0),   # Derecha
            (-constantes.velocidad, 0),  # Izquierda
            (0, constantes.velocidad),   # Abajo
            (0, -constantes.velocidad)   # Arriba
        ]

        direcciones_validas = []

        for dir_x, dir_y in direcciones_posibles:
            # REGLA DE ORO: Un fantasma jamás da un giro de 180 grados
            if dir_x == -self.dx and dir_y == -self.dy and (self.dx != 0 or self.dy != 0):
                continue # Descartamos este camino

            # Comprobamos colisión simulando un paso (Evaluamos si existe la arista)
            rect_prueba = rect_actual.copy()
            rect_prueba.x += dir_x
            rect_prueba.y += dir_y

            colisiona = False
            for muro in muros:
                if rect_prueba.colliderect(muro):
                    colisiona = True
                    break

            # Si no chocamos, es un camino válido
            if not colisiona:
                direcciones_validas.append((dir_x, dir_y))

        # 3. Tomamos una decisión basada en los caminos disponibles
        if direcciones_validas:
            # Elegimos un camino al azar (Comportamiento Errático)
            self.dx, self.dy = random.choice(direcciones_validas)
        else:
            # Seguridad: Si el fantasma entra en un callejón sin salida, le dejamos dar la vuelta
            self.dx *= -1
            self.dy *= -1

        return self.dx, self.dy