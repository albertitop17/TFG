import pygame
import random
import heapq
from collections import deque
from src import constantes
from src.fisica import camino_esta_libre
class Humano:
    '''
    Controlador de E/S para el jugador. 
    Mapea los eventos del teclado convirtiendolos en vectores de velocidad
    '''
    def __init__(self):
        #empieza quieto
        self.dx = 0
        self.dy = 0
        self.estado = "dispersion" # No hace nada, solamente está por compatibilidad 
        self.liberado = True

    def obtener_movimiento(self, **kwargs):
        '''
        Obtiene el estado de todas las teclas y distingue casos en función de que flecha esté presionada
        '''
        teclas = pygame.key.get_pressed() 

        if teclas[pygame.K_LEFT]: 
            self.dx = -constantes.velocidad
            self.dy = 0
        elif teclas[pygame.K_RIGHT]: 
            self.dx = constantes.velocidad   
            self.dy = 0
        elif teclas[pygame.K_UP]: 
            self.dx = 0
            self.dy = -constantes.velocidad
        elif teclas[pygame.K_DOWN]:
            self.dx = 0
            self.dy = constantes.velocidad

        return self.dx, self.dy
    

class IA:
    '''
    Agente autónomo que controla a Pacman.
    Utiliza Búsqueda en Grafos (A*) junto con zonas de peligro.
    '''
    def __init__(self):
        self.dx = 0
        self.dy = 0

        # Variables para el modo Debug
        self.mapa_peligro_debug = {}
        self.meta_bolita_debug = None
        self.camino_debug = []
    
    def obtener_movimiento(self, rect_actual = None, muros = None, objetivo=None, lista_fantasmas=None, mapa_logico=None, bolitas=None, **kwargs):
        
        # Tendremos q poner que cuando acabe las bolitas acabe el nivel (por ahora se queda quieto)
        if not bolitas or not mapa_logico:
            return 0, 0
        
        # Solo calculamos un nuevo camino si estamos alineados en la cuadrícula (podríamos hacerlo mas veces? mejora en eficiencia/winrate?)
        if rect_actual.x % constantes.tamano_celda != 0 or rect_actual.y % constantes.tamano_celda != 0:
            return self.dx, self.dy

        # Discretizamos las coordenadas de Pacman. Pasamos de un esoacion continuo (píxeles) al grafo (matriz)
        x_discretizada = rect_actual.centerx // constantes.tamano_celda
        y_discretizada = (rect_actual.centery - constantes.offset_y_mapa) // constantes.tamano_celda
        nodo_origen = (x_discretizada, y_discretizada)

        # Generamos un 'aura' de peligro alrededor de cada fantasma (primera versión, por ahora atraviesan las paredes)
        mapa_peligro = {}
        self.mapa_peligro_debug = mapa_peligro
        if lista_fantasmas:
            for f in lista_fantasmas:
                if f.controlador.estado not in ["ojos", "asustado"]: 
                    # Discretizamos las posiciones de los fantasmas que puedan atacar a Pacman
                    nodo_fantasma = (f.forma.centerx // constantes.tamano_celda, (f.forma.centery - constantes.offset_y_mapa) // constantes.tamano_celda)

                    # Penalizaciones en función de la distancia [0,1,2,3]
                    penalizaciones = [5000, 2000, 1000, 500]
                    direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]

                    # Usamos una cola para generar el aura de peligro
                    cola_aura_peligro = deque([(nodo_fantasma, 0)]) 
                    visitados_aura_peligro = {nodo_fantasma}

                    while cola_aura_peligro:

                        (cx,cy), distancia = cola_aura_peligro.popleft() 
                        
                        # Asignación directa desde la lista (acceso instantáneo)
                        penalizacion = penalizaciones[distancia]
                                
                        # Si se solapan auras de varios fantasmas, nos quedamos con el peligro más alto
                        mapa_peligro[(cx, cy)] = max(mapa_peligro.get((cx, cy), 0), penalizacion)

                        # Solo hacemos que 'fluya' el aura de peligro 3 casillas
                        if distancia < 3:
                            for dx, dy in direcciones:
                                nx, ny = cx + dx, cy + dy
                                
                                # Comprobamos límites de mapa y que no sea un muro 
                                if 0 <= ny < constantes.filas_mapa and 0 <= nx < constantes.columnas_mapa:
                                    if mapa_logico[ny][nx] != "1" and (nx, ny) not in visitados_aura_peligro:
                                        visitados_aura_peligro.add((nx, ny))
                                        cola_aura_peligro.append(((nx, ny), distancia + 1))
        # Seleccionamos la meta
        def coste_utilidad_bolita(bolita):
            dist_pacman = self.distancia_con_portales(rect_actual.centerx, rect_actual.centery, 
                bolita.centerx, bolita.centery, constantes.ancho_px, constantes.y_tunel_px)
            
            # Consultamos el peligro de la casilla donde está la bolita
            bx = bolita.x // constantes.tamano_celda
            by = (bolita.y - constantes.offset_y_mapa) // constantes.tamano_celda
            
            peligro_casilla = mapa_peligro.get((bx, by), 0)

            return dist_pacman + peligro_casilla

        meta_bolita = min(bolitas, key=coste_utilidad_bolita)
        self.meta_bolita_debug = meta_bolita
        # Hacemos la división entera de 'meta_bolita' para obtener la coordenada de la cuadrícula
        bolita_dis = ( meta_bolita.x // constantes.tamano_celda, (meta_bolita.y - constantes.offset_y_mapa) // constantes.tamano_celda)

        # Aplicamos el Algoritmo A* weighted (con peso de los fantasmas)
        camino = self.a_star_search(nodo_origen, bolita_dis, mapa_logico, mapa_peligro)
        self.camino_debug = camino

        # Traducimos en cinemática (vector de movimiento) el camino calculado
        if camino and len(camino) > 1:
            next_node = camino[1] # El índice 0 es el nodo actual, el 1 es el siguiente nodo 
            # Calculamos la diferencia entre la casilla a la que vamos y en la que estamos
            dx_grid = next_node[0] - x_discretizada
            dy_grid = next_node[1] - y_discretizada
            
            # Añadimos la mecánica del portal 
            # Si el salto es 1 a la derecha (ej: de x=14 a x=15 -> 15-14 = 1)
            # Si cruzamos el portal hacia la derecha (ej: de x=27 a x=0 -> 0-27 = -27)
            if dx_grid == 1 or dx_grid < -1:
                self.dx, self.dy = constantes.velocidad, 0
            # Si el salto es 1 a la izquierda (ej: de x=15 a x=14 -> 14-15 = -1)
            # Si cruzamos el portal hacia la izquierda (ej: de x=0 a x=27 -> 27-0 = 27)
            elif dx_grid == -1 or dx_grid > 1:
                self.dx, self.dy = -constantes.velocidad, 0
            # En el eje Y no hay portal
            elif dy_grid == 1:
                self.dx, self.dy = 0, constantes.velocidad
            elif dy_grid == -1:
                self.dx, self.dy = 0, -constantes.velocidad
        else:
            self.dx, self.dy = 0, 0 # hemos llegado o no hay camino
        return self.dx, self.dy

    def a_star_search(self, nodo_origen, meta, mapa_logico, mapa_peligro):
        '''
        Implementación del algoritmo A*.
        Minimiza una heurística admisible que contempla el teletransporte por el portal.
        Devuelve una lista de nodos (tuplas) desde el origen hasta la meta (en cada iteración)
        para asegurarnos de que 'veamos' correctamente a los fantasmas al calcular el camino.
        '''
        frontera = []
        # La cola de prioridad guarda tuplas de: (f(n), g(n), nodo_actual)
        heapq.heappush(frontera, (0, 0, nodo_origen))
        # Usaremos 'visitados' para mapea el nodo con el coste f(n) más bajo encontrado 
        visitados = {nodo_origen: 0}
        # Diccionario para rastrear el camino de forma súper eficiente
        padres = {nodo_origen: None}
        # Direcciones posibles: (dx, dy) en la cuadrícula (discretizada)
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        y_tunel = constantes.tunel # fila del túnel 
        
        while frontera: # Hasta que no tengamos nodos para explorar
            # Tomamos el nodo con menor f(n) de la frontera
            _, g_n, actual = heapq.heappop(frontera)

            # Miramos is hemos alcanzado el objetivo. En caso afirmativo, reconstruimos la meta
            if actual == meta:
                camino_reconstruido = []
                nodo_actual = actual
                while nodo_actual is not None:
                    camino_reconstruido.append(nodo_actual)
                    nodo_actual = padres[nodo_actual] 
                # Invertimos la lista porque la hemos construido desde la meta hasta el origen
                return camino_reconstruido[::-1]
            
            # Añadimos los nodos vecinos al actual
            for dx, dy in direcciones:
                # Usamos variables sueltas (para poder modificarlas)
                next_x = actual[0] + dx
                next_y = actual[1] + dy

                # hacemos que el portal identifique el otro lado del tunel como vecino 
                if actual[1] == constantes.tunel: # Si estamos en la fila del túnel, el nodo vecino del otro lado del mapa también es accesible
                    if actual[0] == 0 and dx == -1: # Si la coord x es 0 y estamos mirando a la izq (en el tunel)
                        next_x = constantes.columnas_mapa - 1 # Salto a la derecha ((actual-(-1,0))%ancho_mapa )
                    elif actual[0] == constantes.columnas_mapa - 1 and dx == 1: # Análogo por la derecha
                        next_x = 0 # Salto a la izquierda
                siguiente = (next_x, next_y)

                # Comprobamos los límites del mapa (por si acaso, aunque no debería de ser necesario) 
                if 0 <= siguiente[1] < constantes.filas_mapa and 0 <= siguiente[0] < constantes.columnas_mapa: 
                    
                    if mapa_logico[siguiente[1]][siguiente[0]] != "1":  # Seguiremos con el camino si el siguiente nodo no es un muro

                        # g(n): Coste acumulado  
                        coste_paso = 1 + mapa_peligro.get(siguiente, 0)
                        nuevo_coste_g = g_n + coste_paso  

                        # Comprobamos si el nodo ya se ha visitado y si el nuevo camino es más barato
                        if siguiente not in visitados or nuevo_coste_g < visitados[siguiente]:
                            visitados[siguiente] = nuevo_coste_g
                            # Guardamos de qué nodo venimos
                            padres[siguiente] = actual

                            # f(n) = g(n) + h(n)

                            # h(n): Heurística admisible (El mínimo de las 3 distancias posibles)
                            # 1. Distancia Manhattan directa
                            h_directo = abs(siguiente[0] - meta[0]) + abs(siguiente[1] - meta[1])
                            # 2. Distancia cruzando por la izquierda (siguiente -> Izq -> Der -> Meta)
                            h_izq = (siguiente[0] + abs(siguiente[1] - y_tunel)) + 1 + ((constantes.columnas_mapa - 1 - meta[0]) + abs(y_tunel - meta[1]))
                            # 3. Distancia cruzando por la derecha (siguiente -> Der -> Izq -> Meta)
                            h_der = ((constantes.columnas_mapa - 1 - siguiente[0]) + abs(siguiente[1] - y_tunel)) + 1 + (meta[0] + abs(y_tunel - meta[1]))

                            h_n = min(h_directo, h_izq, h_der)
                            prioridad = nuevo_coste_g + h_n

                            heapq.heappush(frontera, (prioridad, nuevo_coste_g, siguiente))
        return [] # Devuelve vacío si no se encuentra solución

    def distancia_con_portales(self, px1, py1, px2, py2, ancho_px, y_tunel_px):
        '''
        Calcula la distancia usando la distancia Manhattan y contemplando que podemos teletrasportarnos por los portales
        '''
        # Distancia Manhattan normal
        dist_directa = abs(px1 - px2) + abs(py1 - py2)
        #Distancia cruzando por el túnel (entrando por la izquierda)
        dist_izq = (px1 + abs(py1 - y_tunel_px)) + constantes.tamano_celda + ((ancho_px - px2) + abs(y_tunel_px - py2))
        #Distancia cruzando por el túnel (entrando por la derecha)
        dist_der = ((ancho_px - px1) + abs(py1 - y_tunel_px)) + constantes.tamano_celda + (px2 + abs(y_tunel_px - py2))

        return min(dist_directa, dist_izq, dist_der)

class ControladorFantasmaPadre:
    '''
    Clase padre de todos los fantasmas.
    Aplica las reglas originales de movimiento globales de todos los fantasmas.
    Contiene funciones para el modo debug.
    '''
    def __init__(self):
        self.dx = 0
        self.dy = 0

        self.estado = "dispersion" # Estados posibles: "perseguir", "asustado", "ojos", "dispersion"
        self.liberado = False # Variable para gestionar la salida de los fantasmas progresivamente 

        self.offset_filas = constantes.offset_y_mapa // constantes.tamano_celda # Para ajustarnos a la posición real del mapa

        # Precalculamos la zona de aparición de los fantasmas
        self.puerta_y = 10 + self.offset_filas
        self.fondo_y  = self.puerta_y + 3
        
        self.puerta_px_x = 13 * constantes.tamano_celda
        self.puerta_px_y = self.puerta_y * constantes.tamano_celda
        self.fondo_px_y  = self.fondo_y * constantes.tamano_celda

        # Variables para el modo Debug
        self.modo_debug = 0 # Todos nacen con el debug apagado
        self.objetivo_debug = None
        self.opciones_debug = [] # Almacena (posicion, distancia) consideradas para el modo debug
        self.ruta_debug = [] # Lista para las 4 posiciones futuras
        
    def obtener_movimiento(self, rect_actual, muros, objetivo=None, lista_fantasmas=None, **kwargs):

        if not self.liberado: return 0, 0

        # Solo calculamos un nuevo camino si estamos alineados en la cuadrícula
        if rect_actual.x % constantes.tamano_celda != 0 or rect_actual.y % constantes.tamano_celda != 0:
            return self.dx, self.dy

        # Si por algún motivo no hay objetivo (Pac-Man ha muerto, etc.), seguimos rectos (no debería de darse)
        if not objetivo:
            return self.dx, self.dy

        direcciones_validas = self.obtener_direcciones_validas(rect_actual, self.dx, self.dy, muros)

        # Elegimos qué hacer según el estado del cada fantasma
        if direcciones_validas: 
            if self.estado == "asustado":
                # Huyen tomando direcciones totalmente aleatorias en los cruces
                self.dx, self.dy = random.choice(direcciones_validas)
            elif self.estado == "ojos":
                # Vuelven directamente al punto de aparición
                self.dx, self.dy = self.logica_ojos(direcciones_validas, rect_actual, muros)
            elif self.estado == "dispersion":
                # Cada fantasma se dirige a su esquina del mapa asignada
                self.dx, self.dy = self.logica_dispersion(direcciones_validas, rect_actual, muros)
            else:
                # Cuando self.estado == "perseguir" dejamos que tome la decisión el cerebro de cada fantasma 
                self.dx, self.dy = self.tomar_decision(direcciones_validas, rect_actual, objetivo,muros, lista_fantasmas)
        else:
            # Si se mete en un callejón sin salida (no debería pasar)
            self.dx *= -1
            self.dy *= -1

        return self.dx, self.dy
    
    def obtener_direcciones_validas(self, rect_actual, dx_actual, dy_actual, muros):
        '''
        Devolvemos las direcciones filtrando:
        - Que no sea un giro de 180º
        - Que no intente entrar a la zona de aparición de los fantasmas
        - Que no sea un muro
        '''
        # Ajustamos la velocidad si están en modo asustados (van más despacio)
        vel_actual = constantes.velocidad_asustados if self.estado == "asustado" else constantes.velocidad 

        # Tenemos 4 direcciones posibles
        direcciones_posibles = [
            (0, -vel_actual),   # Arriba
            (-vel_actual, 0),   # Izquierda
            (0, vel_actual),    # Abajo
            (vel_actual, 0)     # Derecha
        ]

        direcciones_validas = []
        
        # Obtenemos la fila y columna actual para la lógica de la puerta
        fila_actual = rect_actual.y // constantes.tamano_celda
        col_actual = rect_actual.x // constantes.tamano_celda

        # Comprobamos 3 reglas para cada posible dirección
        for dir_x, dir_y in direcciones_posibles:
            # Regla Pac-Man: Los fantasmas no pueden dar la vuelta 180º
            if dir_x == -dx_actual and dir_y == -dy_actual and (dx_actual != 0 or dy_actual != 0):
                continue

            # Regla Pac-Man: No volver a entrar a la zona de aparición
            # La puerta está en la fila 10 (más el offset de la cabecera), columnas 13 y 14
            if dir_y > 0 and fila_actual == (10 + self.offset_filas) and col_actual in (13, 14):
                # Solo pueden atravesar esa puerta si han muerto (son solo ojos)
                if self.estado != "ojos":
                    continue
            
            # Si no chocamos contra un muro, es una dirección válida
            if camino_esta_libre(rect_actual, dir_x, dir_y, muros):
                direcciones_validas.append((dir_x, dir_y))
        return direcciones_validas

    def tomar_decision(self, direcciones_validas, rect_actual, objetivo, muros, lista_fantasmas = None):
        '''
        Este método se sobrescribe en las clases hijas (CerebroBlinky, CerebroPinky, CerebroInky, CerebroClyde).
        Por defecto, si un fantasma no tiene IA propia, se mueve al azar.
        '''
        return random.choice(direcciones_validas)
    
    # funciones del modo debug que heredan todos los fantasmas -----------------------

    def calcular_mejor_dir(self, direcciones, rect, meta_x, meta_y, guardar_debug = False):
        '''
        Función auxiliar que mediante el uso de la distancia euclídea, devuelve la dirección a la que debe ir 
        el fantasma, minimizando la distancia desde el fantasma al objetivo.
        '''

        # Discretizamos la posción del fantasma
        fila_actual = rect.y // constantes.tamano_celda
        col_actual = rect.x // constantes.tamano_celda

        # Si el fantasma no está en el estado ojos, su único objetivo será salir de la zona de aparición (Fila 10, Columna 13)
        if self.estado != "ojos" and (self.puerta_y < fila_actual < self.puerta_y + 6) and (9 < col_actual < 18):
            meta_x = 13 * constantes.tamano_celda
            meta_y = self.puerta_y * constantes.tamano_celda

        mejor_direccion  = direcciones[0] # La dirección por defecto es hacia arriba
        menor_dist = float('inf')

        # Factor que sirve para proyectar la visión exactamente 1 casilla entera hacia adelante
        factor = constantes.factor_proyectar

        for dx, dy in direcciones:
            # Calculamos nuestra futura posición si tomamos este camino (desde el centro de la siguiente celda) ((seguro podemos optimizarlo))
            futuro_x = rect.x + (dx*factor) # una casilla delante
            futuro_y = rect.y + (dy*factor) 

            # Distancia euclidea al cuadrado hasta el objetivo (mejor que calcular la raíz)
            dist_cuadrada = (meta_x - futuro_x)*(meta_x - futuro_x) + (meta_y - futuro_y)*(meta_y - futuro_y) #mejor que hacer **2

            # Guardamos los números para dibujarlos en pantalla si el debug está activo (así en caso de no usarlo no trabajamos innecesariamente)
            if guardar_debug:
                valor_mostrar = int(dist_cuadrada**0.25) # Usamos la raíz quinta para que el número no sea gigante en pantalla
                self.opciones_debug.append(((futuro_x, futuro_y), valor_mostrar))

            if dist_cuadrada < menor_dist:
                menor_dist = dist_cuadrada
                mejor_direccion = (dx, dy)

        return mejor_direccion


    def simular_ruta_futura(self, dir_inicial, rect_actual, meta_x, meta_y, muros):
        '''
        Calcula los próximos 4 cruces solo para dibujarlos en pantalla como una línea de predicción del modo Debug.
        Utilizaremos una copia del fantasma para la simulación.
        '''
        sim_rect = rect_actual.copy()
        sim_dx, sim_dy = dir_inicial
        
        for _ in range(4):
            # Simulamos el movimiento hasta la siguiente celda
            sim_rect.x += sim_dx * (constantes.tamano_celda // constantes.velocidad)
            sim_rect.y += sim_dy * (constantes.tamano_celda // constantes.velocidad)
            
            # Guardamos el centro de esa celda para dibujarlo luego
            self.ruta_debug.append(sim_rect.center)
            
            # Buscamos la siguiente mejor dirección desde esa posición simulada
            posibles = self.obtener_direcciones_validas(sim_rect, sim_dx, sim_dy, muros)        
            if posibles:
                 # Simulamos volver a pensar cuál sería el mejor giro
                sim_dx, sim_dy = self.calcular_mejor_dir(posibles, sim_rect, meta_x, meta_y, guardar_debug=False)
            else:
                break

    
    def logica_ojos(self, direcciones_validas, rect_actual, muros):
        '''
        Para un recorrido más óptimo de los ojos de regreso a la zona de aparición dividimos el camino en 2 partes:
        - Primero se dirige a la puerta de la zona de aparición
        - Una vez llega a la puerta hacemos que entre dentro de la zona de aparición
        '''
        self.opciones_debug = []
        self.ruta_debug = []

        fila_actual = rect_actual.y // constantes.tamano_celda
        col_actual = rect_actual.x // constantes.tamano_celda
    
        # Primera meta, la puerta.
        meta_x = self.puerta_px_x
        meta_y = self.puerta_px_y 

        # Si ya estoy justo encima de la puerta o bajando hacia adentro, 
        # actualizo mi meta para que apunte al fondo de la zona de aparición.
        if col_actual in (13, 14) and self.puerta_y <= fila_actual <= self.fondo_y:
            meta_y = self.fondo_px_y

        # Solo resucita si está en el centro de la casa
        if fila_actual == self.fondo_y and col_actual in (13, 14):
            self.estado = "perseguir"
        # Una vez resucitado volverá a actuar la lógica de salida de la zona de aparición

        self.objetivo_debug = (meta_x, meta_y) 

        # Calculamos el movimiento con el algoritmo voraz
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self.calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)

        # Solo realizamos los cálculos de simulación en caso de que se quiera visualizar
        if self.modo_debug == 2:
            self.simular_ruta_futura(mejor_direccion, rect_actual, meta_x, meta_y, muros)

        return mejor_direccion
    

    def logica_dispersion(self, direcciones_validas, rect_actual, muros):
        '''
        Para cada fantasma, calcula la ruta hacia su esquina de dispersión correspondiente mediante el algoritmo voraz 
        '''
        self.opciones_debug = []
        self.ruta_debug = []
        
        # Tomamos como meta la esquina asignada al fantasma
        meta_x, meta_y = self.meta_dispersion
        self.objetivo_debug = (meta_x, meta_y)

        # Calculamos el camino hacia esa esquina (la siguiente celda)
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self.calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)

        # Solo realizamos los cálculos de simulación en caso de que se quiera visualizar
        if self.modo_debug == 2:
            self.simular_ruta_futura(mejor_direccion, rect_actual, meta_x, meta_y, muros)

        return mejor_direccion

class ControladorFantasmaAleatorio(ControladorFantasmaPadre):
    '''
    El movimiento que seguirá será el predefinido por la clase padre: movimiento aleatorio
    '''
    pass

class CerebroBlinky(ControladorFantasmaPadre):
    '''
    Controlador de la IA de Blinky (Fantasma Rojo).
    Comportamiento: Persigue de forma agresiva a Pacman minimizando la distancia euclidea hasta la posición exacta de este mismo.
    '''

    def __init__(self):
        super().__init__()
        self.liberado = True
        self.meta_dispersion = (26 * constantes.tamano_celda, self.offset_filas * constantes.tamano_celda)

    def tomar_decision(self, direcciones_validas, rect_actual, jugador, muros, lista_fantasmas = None):
        '''
        Fija la meta en la posición exacta de Pacman y calcula mediante el algoritmo voraz la casilla que se encuentra a menor distancia
        '''
        
        meta_x = jugador.forma.centerx
        meta_y = jugador.forma.centery

        # Inicializamos unas variables visuales para el modo Debug
        self.opciones_debug = [] 
        self.ruta_debug = []
        self.objetivo_debug = (meta_x, meta_y) 
        
        # Caluclamos la mejor dirección vorazmente usando la distancia euclídea al cuadrado
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self.calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)

        if self.modo_debug == 2:
            self.simular_ruta_futura(mejor_direccion, rect_actual,  meta_x, meta_y, muros)

        return mejor_direccion


class CerebroPinky(ControladorFantasmaPadre):
    '''
    Controlador de la IA de Pinky (Fantasma Rosa).
    Comportamiento:  Minimiza la distancia euclidea hasta 4 casillas por delante de la trayectoria actual de Pacman.
    '''
    def __init__(self):
        super().__init__()
        self.meta_dispersion = (1 * constantes.tamano_celda, self.offset_filas * constantes.tamano_celda)

    def tomar_decision(self, direcciones_validas, rect_actual, jugador, muros, lista_fantasmas=None):
        '''
        Analiza la dirección actual de Pacman para establecer su meta a 4 posiciones delante y mediante el algoritmo 
        voraz calcula la casilla que se encuentra a menor distancia
        '''
            
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

        # Inicializamos unas variables visuales para el modo Debug
        self.opciones_debug = [] 
        self.ruta_debug = []
        self.objetivo_debug = (meta_x, meta_y) 

        # Caluclamos la mejor dirección vorazmente usando la distancia euclídea al cuadrado
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self.calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)

        if self.modo_debug == 2:
            self.simular_ruta_futura(mejor_direccion, rect_actual, meta_x, meta_y, muros)

        return mejor_direccion
    
class CerebroInky(ControladorFantasmaPadre):
    '''
    Controlador de la IA de Inky (Fantasma Azul).
    Comportamiento: Mediante vectores minimiza la distancia a un punto calculado vectorialmente de la siguiente forma:
    - Obtiene la posición actual de Blinky
    - Proyecta un punto 2 casillas por delante de la trayectoria de Pacman (pivote)
    - Traza un vector desde Blinky hasta el pivote y duplica su longitud
    Al final de este último vector Inky coloca su casilla objetivo
    '''
    def __init__(self):
        super().__init__()
        self.meta_dispersion = (26 * constantes.tamano_celda, 30 * constantes.tamano_celda)
        self.pivote_debug = None 
        self.blinky_debug = None 

    def tomar_decision(self, direcciones_validas, rect_actual, jugador, muros, lista_fantasmas=None):
        '''
        Analiza la dirección actual de Blinky y la posición actual de Pacman para establecer su meta como se menciona en la descripción de la clase
        y mediante el algoritmo voraz calcula la casilla que se encuentra a menor distancia
        '''
        # Blinky es el indice 0 en la lista de fantasmas
        blinky_forma = lista_fantasmas[0].forma 

        if not blinky_forma: # En caso de que no esté Blinky (ha muerto), actúa como si fuese Blinky (apunta directamente a Pacman)
            meta_x, meta_y = jugador.forma.centerx, jugador.forma.centery
            self.blinky_debug = None
        else:
            # Pivote (2 casillas por delante de Pacman)
            pivot_x = jugador.forma.centerx
            pivot_y = jugador.forma.centery
            distancia_pivote = 2 * constantes.tamano_celda 

            if jugador.dx > 0:   # Derecha
                pivot_x += distancia_pivote
            elif jugador.dx < 0: # Izquierda
                pivot_x -= distancia_pivote
            elif jugador.dy > 0: # Abajo
                pivot_y += distancia_pivote
            elif jugador.dy < 0: # Arriba
                pivot_y -= distancia_pivote

            # Vector desde Blinky hasta el pivote
            vector_x = pivot_x - blinky_forma.centerx
            vector_y = pivot_y - blinky_forma.centery

            # La meta de Inky (Blinky + el doble del vector)
            meta_x = blinky_forma.centerx + (2 * vector_x)
            meta_y = blinky_forma.centery + (2 * vector_y)

        self.objetivo_debug = (meta_x, meta_y)

        # Inicializamos unas variables visuales para el modo Debug
        self.opciones_debug = [] 
        self.ruta_debug = []
        self.objetivo_debug = (meta_x, meta_y) 
        self.blinky_debug = blinky_forma.center
        self.pivote_debug = (pivot_x, pivot_y)

        # Caluclamos la mejor dirección vorazmente usando la distancia euclídea al cuadrado
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self.calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)

        if self.modo_debug == 2:
            self.simular_ruta_futura(mejor_direccion, rect_actual, meta_x, meta_y, muros)

        return mejor_direccion

class CerebroClyde(ControladorFantasmaPadre):
    '''
    Controlador de la IA de Clyde (Fantasma Naranja).
    Comportamiento:  Actúa igual que Blinky hasta que entra dentro de una circunferencia móvil ubicada en la posición actual de Pacman. 
        Cuando se encuentra dentro de esta circunferencia huye a su esquina (abajo izquierda) 
        Cuando sale de dicha circunferencia vuelve a actuar como Blinky (repitiéndose este ciclo)
    '''

    def __init__(self):
        super().__init__()
        self.meta_dispersion = (1 * constantes.tamano_celda, 30 * constantes.tamano_celda)
        radio = 8 * constantes.tamano_celda # Radio de la circunferencia centrada en Pacman (radio del miedo)
        self.radio_miedo_cuadrado = radio * radio

    def tomar_decision(self, direcciones_validas, rect_actual, jugador, muros, lista_fantasmas=None):
        '''
        Fija la meta en la posición exacta de Pacman y calcula mediante el algoritmo voraz la casilla que se encuentra a menor distancia.
        Si se encuentra dentro de la circunferencia de radio 8 casillas, fija la meta a la esquina inferior izquierda y calcula mediante 
        el algoritmo voraz la casilla que se encuentra a menor distancia.
        '''

        # Calculamos la distancia euclídea hasta Pacman
        dist_x = jugador.forma.centerx - rect_actual.centerx
        dist_y = jugador.forma.centery - rect_actual.centery
        distancia_a_pacman_cuadrada = (dist_x*dist_x + dist_y*dist_y) #al cuadrado para evitar la raíz cuadrada
        
        # En función de si estoy dentro o fuera de la circunferencia del miedo fijaré la meta como se ha explicado
        if distancia_a_pacman_cuadrada > self.radio_miedo_cuadrado:
            meta_x = jugador.forma.centerx
            meta_y = jugador.forma.centery
        else:
            meta_x = 0
            meta_y = constantes.alto_ventana

        # Inicializamos unas variables visuales para el modo Debug
        self.opciones_debug = [] 
        self.ruta_debug = []
        self.objetivo_debug = (meta_x, meta_y) 

        # Caluclamos la mejor dirección vorazmente usando la distancia euclídea al cuadrado
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self.calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)

        if self.modo_debug == 2:
            self.simular_ruta_futura(mejor_direccion, rect_actual, meta_x, meta_y, muros)

        return mejor_direccion