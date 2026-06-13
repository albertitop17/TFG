import pygame
from src import constantes
from src import controladores
from src.pacman import Pacman
from src.fantasma import Fantasma
from src.mapa import Mapa 

DEBUG = constantes.DEBUG
class Game:
    '''
    Clase Principal (Motor del juego)
    Controla el bucle del juego, instanciando las entidades, gestionando colisiones y actuando como máquina de estados (dispersion <-> perseguir)
    '''
    def __init__(self):
        
        # Inicializamos el motor de Pygame
        pygame.init()
        self.pantalla = pygame.display.set_mode((constantes.ancho_ventana , constantes.alto_ventana )) # Creamos la ventana del juego
        pygame.display.set_caption("TFG Pacman") # Título de la ventana
        self.reloj = pygame.time.Clock() # Para controlar los FPS
        self.run = True

        # Creamos el Mapa y las Entidades
        sprite = pygame.image.load("assets//graficos//sheet_pacman_personajes.png").convert_alpha()

        # Mapa
        self.mapa = Mapa() 

        # Pacman
        self.spawn_pacman = (13 * constantes.tamano_celda, 24 * constantes.tamano_celda) # Guardamos la variable para luego poder reaparecer
        self.jugador = Pacman(x = self.spawn_pacman[0], y = self.spawn_pacman[1], imagen_entera = sprite, controlador = controladores.Humano()) 

        # Fantasmas: Lista de fantasmas: (x, y, color, cerebro)
        tam_celda = constantes.tamano_celda
        centro_x = 13 * tam_celda
        self.fantasmas = [
            Fantasma(x=centro_x              , y=13 * tam_celda, imagen_entera=sprite, controlador=controladores.CerebroBlinky(), color='rojo'),
            Fantasma(x=centro_x              , y=15 * tam_celda, imagen_entera=sprite, controlador=controladores.CerebroPinky(),  color='rosa'),
            Fantasma(x=centro_x + tam_celda  , y=16 * tam_celda, imagen_entera=sprite, controlador=controladores.CerebroInky(),   color='azul'),
            Fantasma(x=centro_x + 2*tam_celda  , y=17 * tam_celda, imagen_entera=sprite, controlador=controladores.CerebroClyde(),  color='naranja'),
        ]
        
        # Variables de Estado Lógico
        self.vidas = 6
        self.puntuacion = 0
        self.bolitas_comidas = 0 # Para liberar al incio a los fantasmas
        self.game_over = False

        # Interfaz y Tipografía
        pygame.font.init() # inicializamos las fuentes por si acaso (aunque pygame.init() debería hacerlo)
        self.fuente_marcador = pygame.font.SysFont("Arial", 24, bold=True)

        # Controladores de tiempo
        self.tiempo_asustado = 0 # Se usará como temporizador para alternar las oleadas de dispersión y perseguir
        self.modo_global = "dispersion" # El juego empieza siempre en dispersión
        self.tiempo_cambio_modo = pygame.time.get_ticks()
        self.duraciones_oleada = constantes.duraciones_oleada  # Tiempos en segundos: [Tiempo Dispersión, Tiempo Persecución]
        self.bolitas_para_liberarse = constantes.bolitas_para_liberarse

        self.modo_debug = 0 # 0: Apagado, 1: Valores (Cajas), 2: Ruta (Prediccion siguientes pasos) 

    def eventos(self):
        '''
        Gestiona los eventos de E/S
        '''
        for evento in pygame.event.get(): # Registramos los eventos (de E/S)
            if evento.type == pygame.QUIT: # Si se cierra la ventana (o alt+F4) finalizamos el bucle del juego
                self.run = False
            if evento.type == pygame.KEYDOWN: # Evento -> presionamos una tecla

                if evento.key == pygame.K_SPACE: # El espacio sirve para alternar el cerebro de Pacman entre la IA o ser controlado por el jugador
                    if isinstance(self.jugador.controlador, controladores.IA):
                        self.jugador.controlador = controladores.Humano()
                        print("Pac-Man controlado por el Jugador")
                    elif isinstance(self.jugador.controlador, controladores.Humano):
                        self.jugador.controlador = controladores.IA()
                        print("Pac-Man controlado por la IA (A*) por puntos")

                if evento.key == pygame.K_i: # Añado el cerebro de supervivenciad
                    if isinstance(self.jugador.controlador, controladores.IAs):
                        self.jugador.controlador = controladores.Humano()
                        print("Pac-Man controlado por el Jugador")
                    elif isinstance(self.jugador.controlador, controladores.Humano):
                        self.jugador.controlador = controladores.IAs()
                        print("Pac-Man controlado por la IA (A*) por supervivencia")

                if evento.key == pygame.K_0: # Solo por prueba: Pulsando el 0 podemos controlar a Blinky manualmente (podríamos usar otras teclas)
                    self.fantasmas[0].controlador = controladores.Humano()

                if evento.key == pygame.K_d: # Puslando la tecla 'd' alternamos entre los 3 estados del debug: 0, 1 y 2
                    self.modo_debug = (self.modo_debug + 1) % 4
                    for f in self.fantasmas:
                        if hasattr(f.controlador, 'modo_debug'):
                            f.controlador.modo_debug = self.modo_debug
                   
    def update(self):
        '''
        Núcleo del juego. 
        Actualiza el movimiento, trata las colisiones y gestiona las oleadas de los fantasmas (dispersión <-> perseguir). 
        '''
        if self.game_over:
            return # Por ahora si acaba la partida congelamos todo. Tendremos que añadir animaciones
        
        dimensiones = (constantes.ancho_ventana , constantes.alto_ventana)

        # Actualizamos a Pacman ------------------------
        self.jugador.actualizar(dimensiones=dimensiones, muros=self.mapa.muros, lista_fantasmas=self.fantasmas, 
                                mapa_logico=self.mapa.matriz, bolitas=self.mapa.bolitas,super_bolitas=self.mapa.super_bolitas)

        # Mecánica de comer bolitas: comprobamos si el rectángulo del jugador colisiona con alguna bolita
        indice_bolita = self.jugador.forma.collidelist(self.mapa.bolitas)
        if indice_bolita != -1:
            self.mapa.bolitas.pop(indice_bolita) # La eliminamos también visualmente
            self.puntuacion += 10
            self.bolitas_comidas += 1

            if self.mapa.bolitas == []:
                self.game_over = True # Por ahora congelamos todo

            for i, fantasma in enumerate(self.fantasmas):
                # Si está bloqueado y ya hemos comido suficientes bolitas, lo liberamos
                if not fantasma.controlador.liberado and self.bolitas_comidas >= self.bolitas_para_liberarse[i]:
                    fantasma.controlador.liberado = True

        indice_super = self.jugador.forma.collidelist(self.mapa.super_bolitas)
        if indice_super != -1:
            self.mapa.super_bolitas.pop(indice_super)
            self.puntuacion += 50
            
            # Activamos el modo asustado en los fantasmas
            self.tiempo_asustado = pygame.time.get_ticks()

            for fantasma in self.fantasmas:
                if fantasma.controlador.estado in ["perseguir", "dispersion"]:
                    fantasma.controlador.estado = "asustado" # Tienen que dar la vuelta 180º y reducir su velocidad
                    self.forzar_giro_180(fantasma, constantes.velocidad_asustados)
                    
        # Controlador del tiempo en el que están asustados los fantasmas 
        tiempo_actual = pygame.time.get_ticks()
        if self.tiempo_asustado > 0:
            tiempo_transcurrido = (tiempo_actual - self.tiempo_asustado) // 1000
            
            # Activamos el parpadeo en los últimos 3 segundos
            parpadeo_activo = (5 <= tiempo_transcurrido < 8)
            peligro_inminente = (7 <= tiempo_transcurrido < 8) 
            for fantasma in self.fantasmas:
                fantasma.aviso_fin_asustado = parpadeo_activo
                fantasma.apuramos_asustado = peligro_inminente

            # Si ya han transcurrido los 8 segundos del susto volvemos al estado normal de perseguir
            if tiempo_transcurrido >= 8: 
                self.tiempo_asustado = 0
                for fantasma in self.fantasmas:
                    if fantasma.controlador.estado == "asustado":
                        # Volvemos al estado normal
                        fantasma.controlador.estado = "perseguir"
                        # Les devolvemos la velocidad normal y giran 180º
                        # En caso de que por reducir la velocidad se quedasen en un pixel impar les obligamos a moverse a uno par
                        self.forzar_giro_180(fantasma, constantes.velocidad, invertir=False)
                        self.sincronizar_cuadricula(fantasma)
    
        # Actualizamos los fantasmas --------------------------
        for fantasma in self.fantasmas: 
            fantasma.actualizar(dimensiones, self.mapa.muros, objetivo=self.jugador, lista_fantasmas=self.fantasmas)
        
        for fantasma in self.fantasmas:
            # Encogemos las 'hitbox' temporalmente 10 píxeles por cada lado para mejorar el game feel
            hitbox_pacman = self.jugador.forma.inflate(-10, -10)
            hitbox_fantasma = fantasma.forma.inflate(-10, -10)
            # Comprobamos si la hitbox encogida del fantasma choca con la de Pacman. En caso de que sí, distinguimos casos.
            if hitbox_pacman.colliderect(hitbox_fantasma): 
                if fantasma.controlador.estado == "asustado":
                    fantasma.controlador.estado = "ojos"
                    self.puntuacion += 200
                    pygame.time.delay(500) # Pausa al comerse un fantasma (habrá que añadir efectos visuales)
                    #volvemos a sincronizarlo a pixel par
                    self.sincronizar_cuadricula(fantasma)
                elif fantasma.controlador.estado in ["perseguir", "dispersion"]:
                    self.morir() # Perdemos una vida y reiniciamos posiciones
                    break # Salimos del bucle para evitar múltiples colisiones en el mismo frame
        
        # Control del cronómetro de oleadas (persecución/dispersión)
        tiempo_actual = pygame.time.get_ticks()
        
        # Si no estamos en modo asustado (el susto pausa el cronómetro de oleadas)
        if self.tiempo_asustado == 0:
            tiempo_transcurrido_oleada = (tiempo_actual - self.tiempo_cambio_modo) // 1000
            # Determinamos cuánto debe durar el modo actual
            duracion_actual = self.duraciones_oleada[0] if self.modo_global == "dispersion" else self.duraciones_oleada[1]

            if tiempo_transcurrido_oleada >= duracion_actual:
                # Reseteamos el reloj
                self.tiempo_cambio_modo = tiempo_actual     
                # Alternamos de modo
                self.modo_global = "perseguir" if self.modo_global == "dispersion" else "dispersion"
                # Aplicamos el cambio a los fantasmas vivos y forzamos el giro de 180º
                for fantasma in self.fantasmas:
                    if fantasma.controlador.estado in ["perseguir", "dispersion"]:
                        fantasma.controlador.estado = self.modo_global
                        self.forzar_giro_180(fantasma)

    def dibujar(self):
        '''
        Se encarga del renderizado de los gráficos por pantalla
        '''
        self.pantalla.fill((0, 0, 0))

        # Dibujamos el mapa
        self.mapa.dibujar(self.pantalla) 

        # Dibujamos a Pacman
        self.jugador.dibujar(self.pantalla, self.modo_debug) 
        
        # Dibujamos a los fantasmas
        for fantasma in self.fantasmas:
            fantasma.dibujar(self.pantalla, self.modo_debug)
        
        # Dibujamos el HUD (Heads-Up Display)
        texto_puntos = self.fuente_marcador.render(f"SCORE: {self.puntuacion}", True, (255, 255, 255))
        self.pantalla.blit(texto_puntos, (10, 5))

        vidas = self.fuente_marcador.render(f"VIDAS: {6-self.vidas}", True, (255, 255, 255)) # Puesto por ahora para mostrar cuantas vidas usa
        self.pantalla.blit(vidas, (430, 5))

        pygame.display.update() # Actualizamos la pantalla para mostrar los cambios

    def forzar_giro_180(self, fantasma, nueva_velocidad=None, invertir=True):
        '''
        Invierte la dirección del fantasma y ajusta la velocidad.
        '''
        # Si no se pasa una velocidad nueva, mantenemos la magnitud actual
        vel = nueva_velocidad if nueva_velocidad is not None else abs(fantasma.dx) or abs(fantasma.dy)
        multiplicador = -1 if invertir else 1

        if fantasma.dx != 0: 
            fantasma.dx = (vel * multiplicador) if fantasma.dx > 0 else (-vel * multiplicador)
            fantasma.controlador.dx = fantasma.dx
        if fantasma.dy != 0: 
            fantasma.dy = (vel * multiplicador) if fantasma.dy > 0 else (-vel * multiplicador)
            fantasma.controlador.dy = fantasma.dy

    def sincronizar_cuadricula(self, fantasma):
        '''
        Evita desalineamientos forzando pixeles pares.
        '''
        if fantasma.forma.x % 2 != 0: 
            fantasma.forma.x += 1 if fantasma.dx > 0 else -1
        if fantasma.forma.y % 2 != 0:
            fantasma.forma.y += 1 if fantasma.dy > 0 else -1

    def reiniciar_posiciones(self):
        '''
        Devuelve a Pac-Man y a los fantasmas a sus posiciones de inicio tras perder una vida
        '''
        # 'Reset' de Pacman
        self.jugador.forma.x, self.jugador.forma.y = self.spawn_pacman
        self.jugador.dx, self.jugador.dy = 0, 0
        self.jugador.controlador.dx, self.jugador.controlador.dy = 0, 0

        # 'Reset' de los fantasmas
        tam_celda = constantes.tamano_celda
        centro_x = 13 * tam_celda
        posiciones_fantasmas = [
            (centro_x, 14 * tam_celda),      # Blinky
            (centro_x, 17 * tam_celda), # Pinky
            (centro_x + tam_celda, 17 * tam_celda),      # Inky
            (centro_x + 2*tam_celda, 17 * tam_celda)  # Clyde
        ]
        for i, fantasma in enumerate(self.fantasmas):
            fantasma.forma.x, fantasma.forma.y = posiciones_fantasmas[i]
            fantasma.controlador.estado = "dispersion" # Vuelven al estado inicial de oleada
            # El update los volverá a liberar rápidamente si ya se comieron bolitas suficientes
            fantasma.controlador.liberado = self.bolitas_comidas >= self.bolitas_para_liberarse[i]
            fantasma.controlador.dx = 0 # Reset memoria cerebro
            fantasma.controlador.dy = 0
            fantasma.dx = 0 # Reset velocidad física
            fantasma.dy = 0

        # reseteamos el sistema de oleadas (dispersión/persecución) 
        self.modo_global = "dispersion"
        self.tiempo_cambio_modo = pygame.time.get_ticks()
        self.tiempo_asustado = 0

    def morir(self):
        '''
        Gestiona las muertes de Pacman
        '''
        self.vidas -= 1

        # Tenemos que añadir aún las animaciones de muerte   
        if self.vidas <= 0:
            self.game_over = True
        else:
            # Pausa de 1.5 segundos antes de reaparecer
            pygame.time.delay(1500)
            self.reiniciar_posiciones()

    def run_game(self):
        '''
        Bucle principal del juego
        '''
        while self.run:
            
            self.reloj.tick(constantes.FPS) # Limitamos a 60 fps
            self.eventos()
            self.update()
            self.dibujar()

        pygame.quit()
    

    def run_simulacion_simple(self, numero_partidas=10):
        '''
        Ejecuta partidas con la IA a máxima velocidad sin renderizar.
        Imprime resultados en formato CSV por stdout.
        Redirigir con: python main.py > datos.csv
        '''
        reloj_original = pygame.time.get_ticks
        delay_original = pygame.time.delay

        pygame.time.delay = lambda ms: None

        # Lambda tomamos la variable para que devolvuelva el tiempo_simulado actual.
        tiempo_simulado = 0
        pygame.time.get_ticks = lambda: tiempo_simulado

        self.jugador.controlador = controladores.IA()
        print("sim,muertes,puntuacion,nivel_superado,frames,tiempo_sim_s")

        for partida in range(numero_partidas):
            # Antes de reiniciar_posiciones()
            # para que tiempo_cambio_modo se inicialice a 0 y las oleadas sean correctas
            tiempo_simulado = 0
            vidas_iniciales = 3
            self.vidas          = vidas_iniciales
            self.puntuacion     = 0
            self.bolitas_comidas= 0
            self.game_over      = False
            self.reiniciar_posiciones()
            self.mapa.bolitas.clear()
            self.mapa.super_bolitas.clear()
            self.mapa.construir_mapa()

            fotogramas = 0
            while not self.game_over:
                tiempo_simulado += 16
                self.update()
                fotogramas += 1
                if not self.mapa.bolitas or fotogramas > 100_000:
                    break

            muertes = vidas_iniciales - self.vidas
            nivel_superado= not self.mapa.bolitas
            print(f"{partida+1},{muertes},{self.puntuacion},"
                f"{nivel_superado},{fotogramas},{tiempo_simulado/1000:.3f}")

        pygame.time.get_ticks = reloj_original
        pygame.time.delay     = delay_original
        pygame.quit()


if __name__ == "__main__":
    Game().run_game()
    # import cProfile
    # cProfile.run('Game().run_simulacion_simple(10)', sort='cumulative')
    # # Para simular 50 partidas instantáneas por consola:
    #Game().run_simulacion_simple(numero_partidas=100)