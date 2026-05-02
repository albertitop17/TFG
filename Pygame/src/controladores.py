import pygame
from src import constantes
import random
from src.fisica import camino_esta_libre
import heapq
class Humano:
    def __init__(self):
        #empieza quieto
        self.dx = 0
        self.dy = 0

    def obtener_movimiento(self, **kwargs):
        
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
    def __init__(self):
        self.dx = 0
        self.dy = 0
    def buscar_bolita_segura(self, nodo_origen, mapa_logico, mapa_peligro, bolitas_dis):
        # Búsqueda de Costo Uniforme (Dijkstra Multi-meta)
        frontera = []
        # Guardamos: (coste_acumulado, nodo_actual, camino_hasta_aqui)
        heapq.heappush(frontera, (0, nodo_origen, [nodo_origen])) 
        visitados = {nodo_origen: 0}
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        while frontera:
            coste_g, actual, camino = heapq.heappop(frontera)
            
            # ¡LA MAGIA! Si el nodo que estamos pisando es una bolita, hemos terminado.
            # Al usar Dijkstra, matemáticamente está garantizado que es la bolita más cercana y segura.
            if actual in bolitas_dis:
                return camino
                
            for dx, dy in direcciones:
                next_x = actual[0] + dx
                next_y = actual[1] + dy
                ancho_mapa = len(mapa_logico[0])
                
                # --- INTEGRACIÓN DE PORTALES ---
                if actual[1] == constantes.tunel:
                    if actual[0] == 0 and dx == -1: next_x = ancho_mapa - 1
                    elif actual[0] == ancho_mapa - 1 and dx == 1: next_x = 0
                        
                siguiente = (next_x, next_y)
                
                if 0 <= siguiente[1] < len(mapa_logico) and 0 <= siguiente[0] < ancho_mapa:
                    if mapa_logico[siguiente[1]][siguiente[0]] != "1": # No es muro
                        
                        # El coste de dar el paso incluye el "aura radiactiva" de los fantasmas
                        coste_paso = 1 + mapa_peligro.get(siguiente, 0)
                        nuevo_coste = coste_g + coste_paso
                        
                        if siguiente not in visitados or nuevo_coste < visitados[siguiente]:
                            visitados[siguiente] = nuevo_coste
                            heapq.heappush(frontera, (nuevo_coste, siguiente, camino + [siguiente]))
                            
        return [] # No hay camino seguro posible (Pac-Man está 100% atrapado)
    
    def obtener_movimiento(self, rect_actual = None, muros = None, objetivo=None, lista_fantasmas=None, mapa_logico=None, bolitas=None, **kwargs):
        
        # Si no me pasan bolitas o mapa, no puedo hacer A*, me quedo quieto
        if not bolitas or not mapa_logico:
            return 0, 0
        # 1 - solo calculamos un nuevo camino si estamos alineados en la cuadrícula (podríamos hacerlo mas veces? mejora en eficiencia/winrate?)
        if rect_actual.x % constantes.tamano_celda != 0 or rect_actual.y % constantes.tamano_celda != 0:
            return self.dx, self.dy

        # 2 - Discretizamos las coordenadas (de Píxeles a Coordenadas de Cuadrícula)
        x_discretizada = rect_actual.centerx // constantes.tamano_celda
        y_discretizada = (rect_actual.centery - constantes.offset_y_mapa) // constantes.tamano_celda
        nodo_origen = (x_discretizada, y_discretizada)


        
        mapa_peligro = {}
        # precalculamos las posiciones discretas de los fantasmas (con un set para que 'in' sea de tiempo 0(1)) 
        posiciones_fantasmas = set()
        if lista_fantasmas:
            for f in lista_fantasmas:
                # Discretizamos sus posiciones igual que con Pac-Man
                fantasma_dis_x = f.forma.centerx // constantes.tamano_celda
                fantasma_dis_y = (f.forma.centery - constantes.offset_y_mapa) // constantes.tamano_celda
                #generamos un rombo de peligro al rededor 
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        distancia = abs(dx) + abs(dy)
                        if distancia <= 3: # Si está dentro del radio de peligro
                            nx, ny = fantasma_dis_x + dx, fantasma_dis_y + dy
                            penalizacion = 0
                            if distancia == 0: penalizacion = 5000
                            elif distancia == 1: penalizacion = 2000
                            elif distancia == 2: penalizacion = 1000
                            elif distancia == 3: penalizacion = 5000
                            
                            # Si se solapan auras de varios fantasmas, nos quedamos con el peligro más alto
                            mapa_peligro[(nx, ny)] = max(mapa_peligro.get((nx, ny), 0), penalizacion)

    
        # 3 - Encontramos la bolita más cercana (Distancia Manhattan en píxeles)
        #meta_bolita = min(bolitas, key=lambda bolita: abs(rect_actual.centerx - bolita.centerx) + abs(rect_actual.centery - bolita.centery)) # NO VALE 
        #pero no debería haber demasiadas en pantalla a la vez. Si fuera un problema, podríamos optimizarlo con una estructura espacial.
        # 3 - Encontramos la bolita más cercana (Distancia con Portales en píxeles)
        ancho_px = constantes.columnas_mapa * constantes.tamano_celda
        y_tunel_px = (constantes.tunel * constantes.tamano_celda) + constantes.offset_y_mapa #fila del tunel
        
    
        meta_bolita = min( #busqueda greedy con la distancia de portales O(nº bolitas restantes)
            bolitas, 
            key=lambda b: self.distancia_con_portales(
                rect_actual.centerx, rect_actual.centery, 
                b.centerx, b.centery, 
                ancho_px, y_tunel_px
            )
        )
        
        
        def coste_utilidad_bolita(bolita):
            dist_pacman = self.distancia_con_portales(
                rect_actual.centerx, rect_actual.centery, 
                bolita.centerx, bolita.centery, 
                ancho_px, y_tunel_px
            )
            
            # Consultamos el peligro EXACTO de la casilla donde está la bolita
            bx = bolita.x // constantes.tamano_celda
            by = (bolita.y - constantes.offset_y_mapa) // constantes.tamano_celda
            
            # Multiplicamos la penalización para que sea repulsiva frente a la distancia
            peligro_casilla = mapa_peligro.get((bx, by), 0) * 100 
            
            return dist_pacman + peligro_casilla

        meta_bolita = min(bolitas, key=coste_utilidad_bolita)
        # 4 - Meta matemática (IMPORTANTE EL OFFSET EN Y PARA QUE APUNTE AL LUGAR REAL DEL MAPA)
        # Usamos .x y .y de la bolita que son las esquinas superiores izquierdas (mejor centrex?)
        bolita_dis_x = meta_bolita.x // constantes.tamano_celda  #necesitamos hacer la división entera para obtener la coordenada de la cuadrícula
        bolita_dis_y = (meta_bolita.y - constantes.offset_y_mapa) // constantes.tamano_celda
        bolita_dis = (bolita_dis_x, bolita_dis_y)

        # 5 - Aplicamos el Algoritmo A* weighted (con peso de los fantasmas)
        camino = self.a_star_search(nodo_origen, bolita_dis, mapa_logico, lista_fantasmas, mapa_peligro)

        # 6 - Traducir el siguiente nodo del camino en velocidades físicas (dx, dy)
        if camino and len(camino) > 1:
            next_node = camino[1] # El índice 0 es el nodo actual, el 1 es el siguiente paso
            
            # Calculamos la diferencia matemática entre la casilla a la que vamos y en la que estamos
            dx_grid = next_node[0] - x_discretizada
            dy_grid = next_node[1] - y_discretizada
            
            # --- MOVIMIENTO CON ARITMÉTICA MODULAR (Portales integrados) ---
            
            # Si el salto es 1 a la derecha (ej: de x=14 a x=15 -> 15-14 = 1)
            # O si cruzamos el portal hacia la derecha (ej: de x=27 a x=0 -> 0-27 = -27)
            if dx_grid == 1 or dx_grid < -1:
                self.dx, self.dy = constantes.velocidad, 0
                
            # Si el salto es 1 a la izquierda (ej: de x=15 a x=14 -> 14-15 = -1)
            # O si cruzamos el portal hacia la izquierda (ej: de x=0 a x=27 -> 27-0 = 27)
            elif dx_grid == -1 or dx_grid > 1:
                self.dx, self.dy = -constantes.velocidad, 0
                
            # Movimientos verticales (sin túnel)
            elif dy_grid == 1:
                self.dx, self.dy = 0, constantes.velocidad
            elif dy_grid == -1:
                self.dx, self.dy = 0, -constantes.velocidad
        else:
            self.dx, self.dy = 0, 0 # hemos llegado o no hay camino
        return self.dx, self.dy






    def a_star_search(self, nodo_origen, meta, mapa_logico, lista_fantasmas, mapa_peligro):
        #Implementació de A* Graph Search 
        #Devuelve una lista de nodos (tuplas) desde 'start' hasta 'goal'.
        
        frontera = []
        # La cola de prioridad guarda tuplas de: (f(n), g(n), nodo_actual, camino_acumulado)
        heapq.heappush(frontera, (0, 0, nodo_origen, [nodo_origen]))
        # 'visitados' mapea un nodo con el coste real 'g(n)' más bajo encontrado hacia él 0(1)
        visitados = {nodo_origen: 0}
        # Direcciones posibles: (dx, dy) en la cuadrícula (discretizada)
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]

       
        #hasta que no tengamos nodos para explorar
        while frontera:
            # popeamos el nodo con menor f(n) de la frontera
            f_n, g_n, actual, camino = heapq.heappop(frontera)
            # Miramos is hemos alcanzado el objetivo
            if actual == meta:
                return camino
            # Añadimos los nodos vecinos al actual
            for dx, dy in direcciones:
                #siguiente = (actual[0] + dx, actual[1] + dy)
                # Usamos variables sueltas (para poder modificarlas)
                next_x = actual[0] + dx
                next_y = actual[1] + dy

                # hacemos que el portal identifique el otro lado del tunel como vecino 
                if actual[1] == constantes.tunel: # Si estamos en la fila del túnel, el nodo vecino del otro lado del mapa también es accesible
                    if actual[0] == 0 and dx == -1: #si la coord x es 0 y estamos mirando a la izq (en el tunel)
                        next_x = constantes.columnas_mapa - 1 # Salto a la derecha ((actual-(-1,0))%ancho_mapa )
                    elif actual[0] == constantes.columnas_mapa - 1 and dx == 1: #por el lado derecho
                        next_x = 0 # Salto a la izquierda

                siguiente = (next_x, next_y)


                # Comprobamos los límites del mapa y si es muro (MAPA es matriz de strings)
                if 0 <= siguiente[1] < len(mapa_logico) and 0 <= siguiente[0] < len(mapa_logico[0]): #cambiarlo por ctes
                    celda = mapa_logico[siguiente[1]][siguiente[0]]
                    
                    if celda != "1":  # no es un muro
                        coste_paso = 1
                        # Si en el nodo destino hay un fantasma, el coste se dispara.
                        #if siguiente in posiciones_fantasmas:
                        coste_paso = 1 + mapa_peligro.get(siguiente, 0)
                        
                        #    coste_paso += 1000
                        nuevo_coste_g = g_n + coste_paso  # c(s, a, s') = 1 si no hay fantasma, 1001 si hay fantasma
                        # Graph Search: Comprobar si el nodo ya se ha visitado y si el nuevo camino es más barato
                        if siguiente not in visitados or nuevo_coste_g < visitados[siguiente]:
                            visitados[siguiente] = nuevo_coste_g
                            # f(n) = g(n) + h(n)
                            # Variables del mapa y el túnel
                            ancho_mapa = constantes.columnas_mapa
                            y_tunel = constantes.tunel # fila del túnel (ajustada al offset???)

                            #Para la heuristica, calculamos las 3 distancias posibles y nos quedamos con la menor (la mejor)
                            # 1. Distancia Manhattan directa
                            h_directo = abs(siguiente[0] - meta[0]) + abs(siguiente[1] - meta[1])
                            # 2. Distancia cruzando por la izquierda (siguiente -> Izq -> Der -> Meta)
                            h_izq = (siguiente[0] + abs(siguiente[1] - y_tunel)) + 1 + ((ancho_mapa - 1 - meta[0]) + abs(y_tunel - meta[1]))
                            # 3. Distancia cruzando por la derecha (siguiente -> Der -> Izq -> Meta)
                            h_der = ((ancho_mapa - 1 - siguiente[0]) + abs(siguiente[1] - y_tunel)) + 1 + (meta[0] + abs(y_tunel - meta[1]))

                            # Tu heurística final
                            h_n = min(h_directo, h_izq, h_der)
                            prioridad = nuevo_coste_g + h_n

                            heapq.heappush(frontera, (prioridad, nuevo_coste_g, siguiente, camino + [siguiente]))
        return [] # Devuelve vacío si no se encuentra solución

    def distancia_con_portales(self, px1, py1, px2, py2, ancho_px, y_tunel_px):
        #calcula la distancia teniendo en cuenta el tunel ¿deberia hacerlo con la euclidea?
        # Distancia Manhattan normal
        dist_directa = abs(px1 - px2) + abs(py1 - py2)

        #Distancia cruzando por el túnel (entrando por la izquierda)
        # Vamos a x=0, cruzamos (+ 1 celda), y vamos desde x=ancho_px hasta la meta
        dist_izq = (px1 + abs(py1 - y_tunel_px)) + constantes.tamano_celda + ((ancho_px - px2) + abs(y_tunel_px - py2))

        #Distancia cruzando por el túnel (entrando por la derecha)
        dist_der = ((ancho_px - px1) + abs(py1 - y_tunel_px)) + constantes.tamano_celda + (px2 + abs(y_tunel_px - py2))

        return min(dist_directa, dist_izq, dist_der)

class ControladorFantasmaPadre:
    def __init__(self):
        self.dx = constantes.velocidad
        self.dy = 0

        self.estado = "dispersion" # Máquina de estados: perseguir, asustado u ojos (o dispersion)
        
        self.liberado = True
        self.offset_filas = constantes.offset_y_mapa // constantes.tamano_celda # para ajustarnos a la posición real del mapa

        self.modo_debug = 0 # Todos nacen con el debug apagado
        #variables del modo debug que heredan todos los fantasmas
        self.objetivo_debug = None
        self.opciones_debug = [] # almacena (posicion, distancia) consideradas para el modo debug
        self.ruta_debug = [] # lista para las 4 posiciones futuras
        
    def obtener_movimiento(self, rect_actual, muros, objetivo=None, lista_fantasmas=None, **kwargs):

        if not self.liberado: return 0, 0
        # Miramos primero si estamos en un cruce (nodo) para tomar decisiones. Si no, seguimos rectos.
        if rect_actual.x % constantes.tamano_celda != 0 or rect_actual.y % constantes.tamano_celda != 0:
            return self.dx, self.dy

        # Si por algún motivo no hay objetivo (Pac-Man ha muerto, etc.), seguimos rectos
        if not objetivo:
            return self.dx, self.dy

        # irán más lentos si están en modo asustados
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

        # Comprobamos qué caminos no tienen pared
        for dir_x, dir_y in direcciones_posibles:
            # Regla PAC-MAN: Los fantasmas no pueden dar la vuelta 180º
            if dir_x == -self.dx and dir_y == -self.dy and (self.dx != 0 or self.dy != 0):
                continue

            # Regla PAC-MAN: No volver a entrar al spawn
            # La puerta está bajo la fila 10, columnas 13 y 14.  Si estoy en la fila 10 NO puedo ir abajo
            if dir_y > 0 and fila_actual == (10 + self.offset_filas) and col_actual in (13, 14):
                # Si el fantasma es solo ojos, puede entrar a la casa
                if self.estado != "ojos":
                    continue

            if camino_esta_libre(rect_actual, dir_x, dir_y, muros):
                direcciones_validas.append((dir_x, dir_y))

        if direcciones_validas: #la decision dependera del fantasma 
            if self.estado == "asustado":
                # Movimiento completamente aleatorio
                self.dx, self.dy = random.choice(direcciones_validas)
            elif self.estado == "ojos":
                # la logica de movimiento es ir al spawn
                self.dx, self.dy = self._logica_ojos(direcciones_validas, rect_actual, muros)
            elif self.estado == "dispersion":
                #cada uno se dirige a su esquina correspondiente
                self.dx, self.dy = self._logica_dispersion(direcciones_validas, rect_actual, muros)
            else:
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

        # salir de la casa si estoy en ella
        fila_actual = rect.y // constantes.tamano_celda
        col_actual = rect.x // constantes.tamano_celda
        
        # Casa fantasma original: filas 12 a 15. Con offset (+3): filas 15 a 18
        # Puerta de salida original: fila 10. Con offset (+3): fila 13
        fila_puerta = 10 + self.offset_filas
        if self.estado != "ojos" and (fila_puerta < fila_actual < fila_puerta + 6) and (9 < col_actual < 18):
            # Mi única meta es la salida (Fila 10, Columna 13)
            meta_x = 13 * constantes.tamano_celda
            meta_y = fila_puerta * constantes.tamano_celda


        mejor_direccion  = direcciones[0]
        menor_dist = float('inf')

        # Calculamos cuántas veces entra la velocidad en una celda (ej: 50 // 5 = 10)
        # Esto sirve para proyectar la visión exactamente 1 casilla entera hacia adelante
        factor = constantes.factor_proyectar

        for dx, dy in direcciones:
            # Calculamos nuestra futura posición si tomamos este camino (desde el centro de la siguiente celda)
            futuro_x = rect.x + (dx*factor)
            futuro_y = rect.y + (dy*factor)
            # Distancia cuadrada hasta PacMan (usamos el centro del rectángulo para que la heurística sea más precisa)
            dist_cuadrada = (meta_x - futuro_x)*(meta_x - futuro_x) + (meta_y - futuro_y)*(meta_y - futuro_y) #mejor que hacer **2

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
        dirs = [(0, -constantes.velocidad), (-constantes.velocidad, 0), (0, constantes.velocidad), 
                (constantes.velocidad, 0)]
        
        fila_actual = rect.y // constantes.tamano_celda
        col_actual = rect.x // constantes.tamano_celda
        fila_puerta = 10 + (constantes.offset_y_mapa // constantes.tamano_celda)
        
        # Devolvemos la lista filtrando:
        # 1. Que no sea un giro de 180º
        # 2. Que no intente entrar a la casa hacia abajo por la puerta (Fila 10, Col 13 o 14)
        # 3. Que el camino esté libre de muros
        return [(dx, dy) for dx, dy in dirs 
            if not (dx == -current_dx and dy == -current_dy) 
            and not (dy > 0 and fila_actual == fila_puerta and col_actual in (13, 14))
            and camino_esta_libre(rect, dx, dy, muros)
        ]
    
    def _logica_ojos(self, direcciones_validas, rect_actual, muros):
        self.opciones_debug = []
        self.ruta_debug = []

        fila_actual = rect_actual.y // constantes.tamano_celda
        col_actual = rect_actual.x // constantes.tamano_celda
        
        fila_puerta = 10 + self.offset_filas
        fila_dentro_casa = fila_puerta + 3 # dentro del spawn

        # meta para el debug
        meta_x = 13 * constantes.tamano_celda
        meta_y = fila_puerta * constantes.tamano_celda #primer checkpoint es la puerta

        # si ya estoy justo encima de la puerta o bajando hacia adentro, 
        # actualizo mi meta para que apunte al FONDO de la casa.
        if col_actual in (13, 14) and fila_puerta <= fila_actual <= fila_dentro_casa:
            meta_y = fila_dentro_casa * constantes.tamano_celda

        self.objetivo_debug = (meta_x, meta_y) 

        # Solo resucita si está en el centro de la casa
        if fila_actual == fila_dentro_casa and col_actual in (13, 14):
            self.estado = "perseguir"
            # No cambiamos la dirección. En el siguiente fotograma ya estará vivo,
            # y la logica de ecape que hemos hecho en _calcular_mejor_dir lo forzará a subir y salir.

        # calculamos el camino vorazmente
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self._calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)

        if self.modo_debug == 2:
            self._simular_ruta_futura(mejor_direccion, rect_actual, meta_x, meta_y, muros)

        return mejor_direccion
    

    def _logica_dispersion(self, direcciones_validas, rect_actual, muros):
        self.opciones_debug = []
        self.ruta_debug = []
        # meta del hijo
        meta_x, meta_y = self.meta_dispersion
        self.objetivo_debug = (meta_x, meta_y)
        # Calculamos el camino hacia esa esquina
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self._calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)
        if self.modo_debug == 2:
            self._simular_ruta_futura(mejor_direccion, rect_actual, meta_x, meta_y, muros)
        return mejor_direccion

class ControladorFantasmaAleatorio(ControladorFantasmaPadre):
    pass

class CerebroBlinky(ControladorFantasmaPadre):

    def __init__(self):
        super().__init__()
        self.meta_dispersion = (26 * constantes.tamano_celda, self.offset_filas * constantes.tamano_celda)

    def tomar_decision(self, direcciones_validas, rect_actual, jugador, muros, lista_fantasmas = None):
        self.objetivo_debug = jugador.forma.center # Guardamos el objetivo para usarlo en el modo debug de src/fantasma.py
        self.opciones_debug = [] # Limpiamos los cálculos del frame anterior
        self.ruta_debug = []
        #meta pacman
        meta_x = jugador.forma.centerx
        meta_y = jugador.forma.centery
        self.objetivo_debug = (meta_x, meta_y) # Guardamos la meta para el modo debug
        # IA DE BLINKY
        #Siguiente decisión (real)
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self._calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)

        # SIMULACIÓN: Predecir los siguientes 4 pasos (debug)
        # Si el modo es 0 o 1, nos saltamos toda esta carga de CPU.
        if self.modo_debug == 2:
            self._simular_ruta_futura(mejor_direccion, rect_actual,  meta_x, meta_y, muros)

        return mejor_direccion


class CerebroPinky(ControladorFantasmaPadre):
    
    def __init__(self):
        super().__init__()
        self.meta_dispersion = (1 * constantes.tamano_celda, self.offset_filas * constantes.tamano_celda)

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
        self.meta_dispersion = (26 * constantes.tamano_celda, 30 * constantes.tamano_celda)
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
                pivot_x -= distancia_pivote 

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


class CerebroClyde(ControladorFantasmaPadre):

    def __init__(self):
        super().__init__()
        self.meta_dispersion = (1 * constantes.tamano_celda, 30 * constantes.tamano_celda)
        #Calculamos el radio de miedo al cuadrado una sola vez al nacer
        # 8 casillas * tamaño de celda, y todo al cuadrado
        radio = 8 * constantes.tamano_celda
        self.radio_miedo_cuadrado = radio * radio

    def tomar_decision(self, direcciones_validas, rect_actual, jugador, muros, lista_fantasmas=None):
        self.opciones_debug = []
        self.ruta_debug = []

        # calculmos la distancia en línea recta hacia Pac-Man
        dist_x = jugador.forma.centerx - rect_actual.centerx
        dist_y = jugador.forma.centery - rect_actual.centery
        distancia_a_pacman_cuadrada = (dist_x*dist_x + dist_y*dist_y) #al cuadrado, para evitar la raíz cuadrada
        
        # 2. Decidir la meta
        if distancia_a_pacman_cuadrada > self.radio_miedo_cuadrado:
            # Si estoy lejos, persigo
            meta_x = jugador.forma.centerx
            meta_y = jugador.forma.centery
        else:
            # Si estoy cerca, huye a su esquina (Inferior Izquierda)
            # es X=0, Y=alto de la ventana
            meta_x = 0
            meta_y = constantes.alto_ventana

        self.objetivo_debug = (meta_x, meta_y)

        # 3. Calcular dirección (PUEDO USAR EL DE BLINKY??????)
        debug_valores = (self.modo_debug == 1)
        mejor_direccion = self._calcular_mejor_dir(direcciones_validas, rect_actual, meta_x, meta_y, guardar_debug=debug_valores)

        if self.modo_debug == 2:
            self._simular_ruta_futura(mejor_direccion, rect_actual, meta_x, meta_y, muros)

        return mejor_direccion