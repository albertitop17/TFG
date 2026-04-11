import pygame
from src import constantes
import random
from src.fisica import camino_esta_libre
class Humano:
    def __init__(self):
        #empieza quieto
        self.dx = 0
        self.dy = 0

    def obtener_movimiento(self, _ ,__,___, _____):
        
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
    def obtener_movimiento(self,  rect_actual, muros, objetivo=None):
        #aqui va la logica de movimiento de la IA
        dx = 0  
        dy = 0
        return dx, dy
    

class ControladorFantasmaPadre:
    def __init__(self):
        self.dx = constantes.velocidad
        self.dy = 0
        self.modo_debug = 0 # Todos nacen con el debug apagado
        #variables del modo debug que heredan todos los fantasmas
        self.objetivo_debug = None
        self.opciones_debug = [] # almacena (posicion, distancia) consideradas para el modo debug
        self.ruta_debug = [] # lista para las 4 posiciones futuras

    def obtener_movimiento(self, rect_actual, muros, objetivo=None, lista_fantasmas=None):
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

        if direcciones_validas: #la decision dependera del fantasma 
            self.dx, self.dy = self.tomar_decision(direcciones_validas, rect_actual, objetivo,muros, lista_fantasmas)
        else:
            # Si se mete en un callejón sin salida (no debería pasar en un mapa de Pac-Man normal)
            self.dx *= -1
            self.dy *= -1

        return self.dx, self.dy

    def tomar_decision(self, direcciones_validas, rect_actual, objetivo, muros, lista_fantasmas = None):
        # Este método está pensado para ser sobrescrito. 
        # Por defecto hace un movimiento aleatorio.
        return random.choice(direcciones_validas)
    
    # funciones del modo debug que heredan todos los fantasmas -----------------------

    def _calcular_mejor_dir(self, direcciones, rect, meta_x, meta_y, guardar_debug = False):
        """Función auxiliar para encontrar la mejor dirección basándose en distancia"""
        mejor_direccion  = direcciones[0]
        menor_dist = float('inf')

        # Calculamos cuántas veces entra la velocidad en una celda (ej: 50 // 5 = 10)
        # Esto sirve para proyectar la visión exactamente 1 casilla entera hacia adelante
        factor = constantes.tamano_celda // constantes.velocidad

        for dx, dy in direcciones:
            # Calculamos nuestra futura posición si tomamos este camino (desde el centro de la siguiente celda)
            futuro_x = rect.x + (dx*factor)
            futuro_y = rect.y + (dy*factor)
            # Distancia cuadrada hasta PacMan (usamos el centro del rectángulo para que la heurística sea más precisa)
            dist_cuadrada = (meta_x - futuro_x)**2 + (meta_y - futuro_y)**2

            # solo guardamos si es el paso real (no una simulación)
            if guardar_debug:
                valor_mostrar = int(dist_cuadrada**0.25) #usamos la raíz quinta para que el número no sea gigante en pantalla
                self.opciones_debug.append(((futuro_x, futuro_y), valor_mostrar))

            if dist_cuadrada < menor_dist:
                menor_dist = dist_cuadrada
                mejor_direccion = (dx, dy)

        return mejor_direccion


    def _simular_ruta_futura(self, dir_inicial, rect_actual, meta_x, meta_y, muros):
        """Calcula los próximos 4 movimientos solo para dibujarlos en pantalla"""
        sim_rect = rect_actual.copy()
        sim_dx, sim_dy = dir_inicial
        
        for _ in range(4):
            # Simulamos el movimiento hasta la siguiente celda/intersección
            sim_rect.x += sim_dx * (constantes.tamano_celda // constantes.velocidad)
            sim_rect.y += sim_dy * (constantes.tamano_celda // constantes.velocidad)
            
            # Guardamos el centro de esa celda para dibujarlo luego
            self.ruta_debug.append(sim_rect.center)
            
            # Buscamos la siguiente mejor dirección desde esa posición simulada
            posibles = self._obtener_validas_sim(sim_rect, sim_dx, sim_dy, muros)
            if posibles:
                #limpiamos opciones_debug para no guardar los cálculos falsos de la simulación
                #se actualizan sim_dx y sim_dy para el siguiente ciclo del bucle
                sim_dx, sim_dy = self._calcular_mejor_dir(posibles, sim_rect, meta_x, meta_y, guardar_debug=False)
            else:
                break

    def _obtener_validas_sim(self, rect, current_dx, current_dy, muros):
        # Función auxiliar para la simulación que evita volver atrás
        dirs = [(0, -constantes.velocidad), (-constantes.velocidad, 0), (0, constantes.velocidad), (constantes.velocidad, 0)]
        validas = []
        for dx, dy in dirs:
            if dx == -current_dx and dy == -current_dy: 
                continue
            if camino_esta_libre(rect, dx, dy, muros):
                validas.append((dx, dy))
        return validas
    
class ControladorFantasmaAleatorio(ControladorFantasmaPadre):
    pass

class CerebroBlinky(ControladorFantasmaPadre):

    #usará el init del padre
        
    def tomar_decision(self, direcciones_validas, rect_actual, objetivo, muros, lista_fantasmas = None):

        self.objetivo_debug = objetivo.forma.center # Guardamos el objetivo para usarlo en el modo debug de src/fantasma.py
        # IA DE BLINKY
        mejor_direccion = direcciones_validas[0]
        menor_distancia = float('inf') #inicializamos con infinito para asegurarnos de que cualquier distancia real será menor

        for dir_x, dir_y in direcciones_validas:
            # Calculamos nuestra futura posición si tomamos este camino
            futuro_x = rect_actual.x + dir_x
            futuro_y = rect_actual.y + dir_y
            
            # matemáticas: Distancia Euclidiana al Cuadrado hacia Pac-Man
            dist_cuadrada = (objetivo.forma.centerx - futuro_x)**2 + (objetivo.forma.centery - futuro_y)**2

            # Debug: Guardamos la info para el dibujo: posición central de la futura celda y su valor
            # Usamos la raíz para que el número no sea gigante en pantalla
            valor_mostrar = int(dist_cuadrada**0.5) 
            self.opciones_debug.append(((futuro_x, futuro_y), valor_mostrar))
            
            if dist_cuadrada < menor_distancia:
                menor_distancia = dist_cuadrada
                mejor_direccion = (dir_x, dir_y)

        return mejor_direccion
    

class CerebroBlinky2(ControladorFantasmaPadre):

    #usará el init del padre

    def tomar_decision(self, direcciones_validas, rect_actual, jugador, muros, lista_fantasmas = None):
        self.objetivo_debug = jugador.forma.center # Guardamos el objetivo para usarlo en el modo debug de src/fantasma.py
        self.opciones_debug = [] # Limpiamos los cálculos del frame anterior
        self.ruta_debug = []

        # IA DE BLINKY
        #Siguiente decisión (real)
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self._calcular_mejor_dir(direcciones_validas, rect_actual, jugador.forma.centerx, jugador.forma.centery, guardar_debug=debug_valores)

        # SIMULACIÓN: Predecir los siguientes 4 nodos (debug)
        # Si el modo es 0 o 1, nos saltamos toda esta carga de CPU.
        if self.modo_debug == 2:
            self._simular_ruta_futura(mejor_direccion, rect_actual,  jugador.forma.centerx, jugador.forma.centery, muros)

        return mejor_direccion


class CerebroPinky(ControladorFantasmaPadre):
    
    #usará el init del padre

    def tomar_decision(self, direcciones_validas, rect_actual, jugador, muros, lista_fantasmas=None):
        #META DE PINKY (4 casillas por delante)
        meta_x = jugador.forma.centerx
        meta_y = jugador.forma.centery
        
        distancia_emboscada = 4 * constantes.tamano_celda

        # Miramos hacia dónde va Pac-Man
        if jugador.dx > 0:   # Derecha
            meta_x += distancia_emboscada
        elif jugador.dx < 0: # Izquierda
            meta_x -= distancia_emboscada
        elif jugador.dy > 0: # Abajo
            meta_y += distancia_emboscada
        elif jugador.dy < 0: # Arriba
            meta_y -= distancia_emboscada
            # ¿bug clásico de Pinky? En el juego original

        # Guardamos la meta calculada para que el modo debug dibuje la línea rosa hasta allí
        self.objetivo_debug = (meta_x, meta_y)

        #limpiamos los debugs de la iteración anterior
        self.opciones_debug = []
        self.ruta_debug = []

        # calculo de la mejor direccion basandose en la distancia euclidiana a su meta 
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self._calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)

        # simulacion de ruta futura (Modo Debug 2)
        if self.modo_debug == 2:
            self._simular_ruta_futura(mejor_direccion, rect_actual, meta_x, meta_y, muros)

        return mejor_direccion

    
    

class CerebroInky(ControladorFantasmaPadre):
    def __init__(self):
        super().__init__()
        self.pivote_debug = None 
        self.blinky_debug = None # guardamos dónde está Blinky para el dibujo

    def tomar_decision(self, direcciones_validas, rect_actual, jugador, muros, lista_fantasmas=None):
        self.opciones_debug = []
        self.ruta_debug = []

        #blinky es el indice 0 en la lista de fantasmas
        blinky_forma = lista_fantasmas[0].forma #va a ser siempre la lista no vacia? if lista_fantasmas and len(lista_fantasmas) > 0 else None

        if not blinky_forma:
            meta_x, meta_y = jugador.forma.centerx, jugador.forma.centery
            self.blinky_debug = None
        else:
            self.blinky_debug = blinky_forma.center # para el debug
            # pivote (2 casillas por delante de Pac-Man)
            pivot_x = jugador.forma.centerx
            pivot_y = jugador.forma.centery
            distancia_pivote = 2 * constantes.tamano_celda #dos casillas por delante

            if jugador.dx > 0:   # Derecha
                pivot_x += distancia_pivote
            elif jugador.dx < 0: # Izquierda
                pivot_x -= distancia_pivote
            elif jugador.dy > 0: # Abajo
                pivot_y += distancia_pivote
            elif jugador.dy < 0: # Arriba
                pivot_y -= distancia_pivote
                pivot_x -= distancia_pivote # ¡El Bug!

            self.pivote_debug = (pivot_x, pivot_y)

            # vector desde Blinky hasta el pivote
            vector_x = pivot_x - blinky_forma.centerx
            vector_y = pivot_y - blinky_forma.centery

            # la meta de inky (Blinky + el doble del vector)
            meta_x = blinky_forma.centerx + (2 * vector_x)
            meta_y = blinky_forma.centery + (2 * vector_y)

        self.objetivo_debug = (meta_x, meta_y)

        # --- Lógica de persecución ---
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self._calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)

        if self.modo_debug == 2:
            self._simular_ruta_futura(mejor_direccion, rect_actual, meta_x, meta_y, muros)

        return mejor_direccion

    