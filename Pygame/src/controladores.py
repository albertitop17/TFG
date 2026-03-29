import pygame
from src import constantes
import random
from src.fisica import camino_esta_libre
class Humano:
    def __init__(self):
        #empieza quieto
        self.dx = 0
        self.dy = 0

    def obtener_movimiento(self, _ ,__,___):
        
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
    def obtener_movimiento(self, _ ,__,___):
        #aqui va la logica de movimiento de la IA
        dx = 0  
        dy = 0
        return dx, dy
    

class ControladorFantasmaPadre:
    def __init__(self):
        self.dx = constantes.velocidad
        self.dy = 0

    def obtener_movimiento(self, rect_actual, muros, objetivo=None):
        # Miramos primero si estamos en un cruce (nodo) para tomar decisiones. Si no, seguimos rectos.
        if rect_actual.x % constantes.tamano_celda != 0 or rect_actual.y % constantes.tamano_celda != 0:
            return self.dx, self.dy

        # Si por algún motivo no hay objetivo (Pac-Man ha muerto, etc.), seguimos rectos
        if not objetivo:
            return self.dx, self.dy

        # Tenemos 4 direcciones posibles
        direcciones_posibles = [
            (0, -constantes.velocidad),   # Arriba
            (-constantes.velocidad, 0),   # Izquierda
            (0, constantes.velocidad),    # Abajo
            (constantes.velocidad, 0)     # Derecha
        ]

        direcciones_validas = []

        # Comprobamos qué caminos no tienen pared
        for dir_x, dir_y in direcciones_posibles:
            # REGLA PAC-MAN: Los fantasmas no pueden dar la vuelta 180º
            if dir_x == -self.dx and dir_y == -self.dy and (self.dx != 0 or self.dy != 0):
                continue
            if camino_esta_libre(rect_actual, dir_x, dir_y, muros):
                direcciones_validas.append((dir_x, dir_y))

        if direcciones_validas:
            self.dx, self.dy = self.tomar_decision(direcciones_validas, rect_actual, objetivo)
        else:
            # Si se mete en un callejón sin salida (no debería pasar en un mapa de Pac-Man normal)
            self.dx *= -1
            self.dy *= -1

        return self.dx, self.dy

    def tomar_decision(self, direcciones_validas, rect_actual, objetivo):
        # Este método está pensado para ser sobrescrito. 
        # Por defecto (si un hijo no lo cambia), hace un movimiento aleatorio.
        return random.choice(direcciones_validas)
    
class ControladorFantasmaAleatorio(ControladorFantasmaPadre):
    pass

class CerebroBlinky(ControladorFantasmaPadre):

    def __init__(self):
        super().__init__()
        #Para dibujar la heuristica de Blinky en modo debug
        self.objetivo_debug = None

        
    def tomar_decision(self, direcciones_validas, rect_actual, objetivo):

        self.objetivo_debug = objetivo.center # Guardamos el objetivo para usarlo en el modo debug de src/fantasma.py
        # IA DE BLINKY
        mejor_direccion = direcciones_validas[0]
        menor_distancia = float('inf')

        for dir_x, dir_y in direcciones_validas:
            # Calculamos nuestra futura posición si tomamos este camino
            futuro_x = rect_actual.x + dir_x
            futuro_y = rect_actual.y + dir_y
            
            # MATEMÁTICAS: Distancia Euclidiana al Cuadrado hacia Pac-Man
            dist_cuadrada = (objetivo.centerx - futuro_x)**2 + (objetivo.centery - futuro_y)**2
            
            if dist_cuadrada < menor_distancia:
                menor_distancia = dist_cuadrada
                mejor_direccion = (dir_x, dir_y)

        return mejor_direccion

class CerebroBlinky2(ControladorFantasmaPadre):
    def __init__(self):
        super().__init__()
        #Para dibujar la heuristica de Blinky en modo debug
        self.objetivo_debug = None 

    def tomar_decision(self, direcciones_validas, rect_actual, objetivo):

        self.objetivo_debug = objetivo.center # Guardamos el objetivo para usarlo en el modo debug de src/fantasma.py
        # IA DE BLINKY
        mejor_direccion = direcciones_validas[0]
        menor_distancia = float('inf')

        for dir_x, dir_y in direcciones_validas:
            # Calculamos nuestra futura posición si tomamos este camino
            futuro_x = rect_actual.x + dir_x
            futuro_y = rect_actual.y + dir_y
            
            # Distancia Manhattan al Cuadrado hacia Pac-Man
            dist_manhattan = abs(objetivo.centerx - futuro_x) + abs(objetivo.centery - futuro_y)
                
            if dist_manhattan < menor_distancia:
                menor_distancia = dist_manhattan
                mejor_direccion = (dir_x, dir_y)
        return mejor_direccion
    

