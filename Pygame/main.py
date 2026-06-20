import pygame
import random
from src import constantes
from src import controladores
from src.pacman import Pacman
from src.fantasma import Fantasma
from src.mapa import Mapa 
from config_sim import ConfigSimulacion

DEBUG = constantes.DEBUG
class Game:
    '''
    Clase Principal (Motor del juego)
    Controla el bucle del juego, instanciando las entidades, gestionando colisiones y actuando como máquina de estados (dispersion <-> perseguir)

    Todas las dinámicas temporales (oleadas dispersión/persecución y duración del estado asustado) se miden en frames 
    Así el movimiento y los temporizadores comparten una única unidad: 1 frame
    A 60 FPS, 1 frame es aprox 16.67 ms, de modo que una oleada de 7 seg equivale a 7*60 = 420 frames.

    Para jugar: Game().run_game()  (config=None -> con ventana y sprites).
    Para simular: Game(ConfigSimulacion(headless=True)).simular_una_partida().
    '''

    def __init__(self, config = None):
        
        # config=None significa "juego real": con ventana, sprites y control humano.
        if config is None:
            config = ConfigSimulacion(headless=False, vidas=3)
        self.config = config
        self.headless = config.headless

        # Inicializamos el motor de Pygame
        pygame.init()
        # Inicializamos las fuentes por si acaso (aunque pygame.init() debería hacerlo)
        pygame.font.init() 

        
        if self.headless:
            # No se renderiza nada
            self.pantalla = None
            sprite = pygame.Surface((256, 256), pygame.SRCALPHA) # Sprite falso para que no falle
        else:
            # Creamos la ventana del juego
            self.pantalla = pygame.display.set_mode((constantes.ancho_ventana, constantes.alto_ventana))
            pygame.display.set_caption("TFG Pacman") # Título de la ventana
            sprite = pygame.image.load("assets//graficos//sheet_pacman_personajes.png").convert_alpha()


        # Creamos el Mapa y las Entidades
        self.sprite = sprite
        self.reloj = pygame.time.Clock() # Para controlar los FPS
        self.run = True

        # Mapa
        self.mapa = Mapa() 

        # Pacman
        self.spawn_pacman = (13 * constantes.tamano_celda, 24 * constantes.tamano_celda) # Guardamos la variable para luego poder reaparecer

        if self.headless: # En simulación lo controla la IA desde el inicio (con sus radios)
            ctrl_pacman = controladores.IA_Ptos(radio_caza=self.config.radios_ia.get("radio_caza"),radio_super=self.config.radios_ia.get("radio_super"),
                    radio_bolita_optima=self.config.radios_ia.get("radio_bolita_optima"))
        else:
            # Controlador provisional. El real se elige luego
            ctrl_pacman = controladores.Humano()

        self.jugador = Pacman(x=self.spawn_pacman[0], y=self.spawn_pacman[1], imagen_entera=sprite, controlador=ctrl_pacman)

         # Fantasmas (a partir de la configuración)
        self.fantasmas = self.crear_fantasmas()

        # # Fantasmas: Lista de fantasmas: (x, y, color, cerebro)
        # tam_celda = constantes.tamano_celda
        # centro_x = 13 * tam_celda
        # self.fantasmas = [
        #     Fantasma(x=centro_x              , y=13 * tam_celda, imagen_entera=sprite, controlador=controladores.CerebroBlinky(), color='rojo'),
        #     Fantasma(x=centro_x              , y=15 * tam_celda, imagen_entera=sprite, controlador=controladores.CerebroPinky(),  color='rosa'),
        #     Fantasma(x=centro_x + tam_celda  , y=16 * tam_celda, imagen_entera=sprite, controlador=controladores.CerebroInky(),   color='azul'),
        #     Fantasma(x=centro_x + 2*tam_celda  , y=17 * tam_celda, imagen_entera=sprite, controlador=controladores.CerebroClyde(),  color='naranja'),
        # ]
        
        # Variables de Estado Lógico
        self.vidas = self.config.vidas 
        self.puntuacion = 0
        self.bolitas_comidas = 0 # Para liberar al incio a los fantasmas
        self.game_over = False

        # Interfaz y Tipografía
        self.fuente_marcador = pygame.font.SysFont("Arial", 24, bold=True)

        # Controladores de tiempo (temporizadores basados en frames)
        FPS = constantes.FPS
        self.frame = 0                  # Contador de frames de la partida
        self.frame_asustado = None      # Frame en el que se ha comido la ultima super-bolita (None significa que no está en susto)

        self.frame_cambio_modo = 0      # Frame del último cambio de oleada
        self.modo_global = "dispersion" # El juego empieza siempre en dispersión

        # Duraciones convertidas de segundos a frames (una sola vez)
        self.duraciones_oleada_frames = [s * FPS for s in constantes.duraciones_oleada]
        self.frames_susto    = constantes.susto_total_s    * FPS
        self.frames_parpadeo = constantes.susto_parpadeo_s * FPS
        self.frames_peligro  = constantes.susto_peligro_s  * FPS
        self.bolitas_para_liberarse = [e.liberar_con for e in self.config.fantasmas] # REVISAR ESTA LINEA

        # self.tiempo_asustado = 0 # Se usará como temporizador para alternar las oleadas de dispersión y perseguir
        # self.modo_global = "dispersion" # El juego empieza siempre en dispersión
        # self.tiempo_cambio_modo = pygame.time.get_ticks()
        # self.duraciones_oleada = constantes.duraciones_oleada  # Tiempos en segundos: [Tiempo Dispersión, Tiempo Persecución]
        # self.bolitas_para_liberarse = constantes.bolitas_para_liberarse

        self.modo_debug = 0 # 0: Apagado, 1: Valores (Cajas), 2: Ruta (Prediccion siguientes pasos) 


    def crear_fantasmas(self):
        '''
        Instancia los fantasmas descritos en la configuración.
        '''

        tam = constantes.tamano_celda
        fantasmas = []
        for e in self.config.fantasmas:
            col, fila = e.spawn_celda
            f = Fantasma(x=col * tam, y=fila * tam, imagen_entera=self.sprite,
                         controlador=e.cerebro(), color=e.color)
            fantasmas.append(f)
        return fantasmas
    
    '''
    BUCLE DEL JUEGO (GAME LOOP)
    '''
    def eventos(self):
        '''
        Gestiona los eventos de E/S (solo en el juego real, no en las simulaciones)
        '''
        for evento in pygame.event.get(): # Registramos los eventos (de E/S)
            if evento.type == pygame.QUIT: # Si se cierra la ventana (o alt+F4) finalizamos el bucle del juego
                self.run = False
            if evento.type == pygame.KEYDOWN: # Evento -> presionamos una tecla

                 # H: controlador Humano
                if evento.key == pygame.K_h:
                    self.jugador.controlador = controladores.Humano()
                    print("Controlador: Humano")
 
                # S: IA Segura
                elif evento.key == pygame.K_s:
                    self.jugador.controlador = controladores.IA_Segura()
                    print("Controlador: IA Segura")
 
                # P: IA Puntos
                elif evento.key == pygame.K_p:
                    self.jugador.controlador = controladores.IA_Ptos()
                    print("Controlador: IA Puntos")
 
                # D: cicla entre los modos debug (0 -> 1 -> 2 -> 3 -> 0)
                elif evento.key == pygame.K_d:
                    self.modo_debug = (self.modo_debug + 1) % 4
                    for f in self.fantasmas:
                        if hasattr(f.controlador, 'modo_debug'):
                            f.controlador.modo_debug = self.modo_debug
 
                # 0: control manual de Blinky (para pruebas)
                elif evento.key == pygame.K_0:
                    self.fantasmas[0].controlador = controladores.Humano()
    
    def pausas_visuales(self, ms):
        '''
        Pausa para que quede como el juego real. Pero para la simulación es contraproducente.
        Como no avanza el contador de frames, estas pausas no consumen tiempo de juego (ni de oleada ni de susto)
        '''
        if not self.headless:
            pygame.time.delay(ms)


    def update(self):
        '''
        Núcleo del juego. 
        Actualiza el movimiento, trata las colisiones y gestiona las oleadas de los fantasmas (dispersión <-> perseguir). 
        '''
        if self.game_over:
            return # Por ahora si acaba la partida congelamos todo. Tendremos que añadir animaciones
        
        # 1 update equivale a 1 frame que equivale a 1 paso de movimiento 
        self.frame += 1

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

        # Mecánica de comer super-bolitas
        indice_super = self.jugador.forma.collidelist(self.mapa.super_bolitas)
        if indice_super != -1:
            self.mapa.super_bolitas.pop(indice_super)
            self.puntuacion += 50
            
            # Activamos el modo asustado en los fantasmas (frame de inicio)
            self.frame_asustado = self.frame
            for fantasma in self.fantasmas:
                if fantasma.controlador.estado in ["perseguir", "dispersion"]:
                    fantasma.controlador.estado = "asustado" # Tienen que dar la vuelta 180º y reducir su velocidad
                    self.forzar_giro_180(fantasma, constantes.velocidad_asustados)
                    
        # Controlador del tiempo en el que están asustados los fantasmas 
        if self.frame_asustado is not None:
            frames_susto_transcurridos = self.frame - self.frame_asustado

            # Activamos el parpadeo en los últimos 3 segundos
            parpadeo_activo   = (self.frames_parpadeo <= frames_susto_transcurridos < self.frames_susto)
            peligro_inminente = (self.frames_peligro  <= frames_susto_transcurridos < self.frames_susto) 
            for fantasma in self.fantasmas:
                fantasma.aviso_fin_asustado = parpadeo_activo
                fantasma.apuramos_asustado = peligro_inminente

            # Si ya han transcurrido los 8 segundos del susto volvemos al estado normal de perseguir
            if frames_susto_transcurridos >= self.frames_susto: 
                self.tiempo_asustado = None
                for fantasma in self.fantasmas:
                    if fantasma.controlador.estado == "asustado":
                        # Volvemos al estado normal
                        fantasma.controlador.estado = "perseguir"
                        # Les devolvemos la velocidad normal y giran 180º
                        # En caso de que por reducir la velocidada se quedasen en un pixel impar les obligamos a moverse a uno par
                        self.forzar_giro_180(fantasma, constantes.velocidad, invertir=False)
                        self.sincronizar_cuadricula(fantasma)
    
        # Actualizamos los fantasmas --------------------------
        for fantasma in self.fantasmas: 
            fantasma.actualizar(dimensiones, self.mapa.muros, objetivo=self.jugador, lista_fantasmas=self.fantasmas)
        
        # Gestionamos las colisiones entre los fantasmas y Pac-Man
        for fantasma in self.fantasmas:
            # Encogemos las 'hitbox' temporalmente 10 píxeles por cada lado para mejorar el game feel
            hitbox_pacman = self.jugador.forma.inflate(-10, -10)
            hitbox_fantasma = fantasma.forma.inflate(-10, -10)
            # Comprobamos si la hitbox encogida del fantasma choca con la de Pacman. En caso de que sí, distinguimos casos.
            if hitbox_pacman.colliderect(hitbox_fantasma): 
                if fantasma.controlador.estado == "asustado":
                    fantasma.controlador.estado = "ojos"
                    self.puntuacion += 200
                    self.pausas_visuales(500) # Pausa al comerse un fantasma 500 ms
                    #volvemos a sincronizarlo a pixel par
                    self.sincronizar_cuadricula(fantasma)
                elif fantasma.controlador.estado in ["perseguir", "dispersion"]:
                    self.morir() # Perdemos una vida y reiniciamos posiciones
                    break # Salimos del bucle para evitar múltiples colisiones en el mismo frame
        
        # Control del cronómetro de oleadas (persecución/dispersión) en frames
        # Si no estamos en modo asustado (el susto pausa el cronómetro de oleadas)

        if self.frame_asustado is None:

            frames_oleada_transcurrido = self.frame - self.frame_cambio_modo

            # Determinamos cuánto debe durar el modo actual
            duracion_actual = self.duraciones_oleada_frames[0] if self.modo_global == "dispersion" else self.duraciones_oleada_frames[1]

            if frames_oleada_transcurrido >= duracion_actual:
                # Reseteamos los frames
                self.frame_cambio_modo = self.frame     
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
        
        # Dibujamos el HUD superior
        texto_puntos = self.fuente_marcador.render(f"SCORE: {self.puntuacion}", True, (255, 255, 255))
        self.pantalla.blit(texto_puntos, (10, 5))

        vidas = self.fuente_marcador.render(f"VIDAS: {3-self.vidas}", True, (255, 255, 255)) # Puesto por ahora para mostrar cuantas vidas usa
        self.pantalla.blit(vidas, (430, 5))

        # Dibujamos el HUD inferior

        y_hud = constantes.offset_y_mapa + len(self.mapa.matriz) * constantes.tamano_celda + 4
        fuente_hud = pygame.font.SysFont("Arial", 13)
 
        # Nombre del controlador activo
        nombre_ctrl = type(self.jugador.controlador).__name__
        ctrl_txt = fuente_hud.render(f"Ctrl: {nombre_ctrl}", True, (200, 200, 200))
        self.pantalla.blit(ctrl_txt, (8, y_hud))
 
        # Leyenda de teclas
        modos_debug = ["Apagado", "Valores", "Ruta", "Peligro"]
        leyenda = (f"H: Humano   S: IA Segura   P: IA Puntos   "    
                   f"D: Debug [{modos_debug[self.modo_debug]}]")
        ley_txt = fuente_hud.render(leyenda, True, (160, 160, 160))
        self.pantalla.blit(ley_txt, (8, y_hud + 16))

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
        tam = constantes.tamano_celda
        # Reseteamos a Pacman
        self.jugador.forma.x, self.jugador.forma.y = self.spawn_pacman
        self.jugador.dx, self.jugador.dy = 0, 0
        self.jugador.controlador.dx, self.jugador.controlador.dy = 0, 0

        # Reseteamos de los fantasmas (las posiciones se definen en la configuración)
        for i, fantasma in enumerate(self.fantasmas):
            col, fila = self.config.fantasmas[i].spawn_celda
            fantasma.forma.x, fantasma.forma.y = col * tam, fila * tam
            fantasma.controlador.estado = "dispersion" # Vuelven al estado inicial de oleada
            # El update los volverá a liberar rápidamente si ya se comieron bolitas suficientes
            fantasma.controlador.liberado = self.bolitas_comidas >= self.bolitas_para_liberarse[i]
            fantasma.controlador.dx = 0 # Reset memoria cerebro
            fantasma.controlador.dy = 0
            fantasma.dx = 0 # Reset velocidad física
            fantasma.dy = 0

        # Reseteamos el sistema de oleadas (dispersión/persecución) 
        self.modo_global = "dispersion"
        self.frame_cambio_modo = self.frame
        self.frame_asustado = None

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
            self.pausas_visuales(1500)
            self.reiniciar_posiciones()

    def pantalla_seleccion(self):
        '''
        Pantalla previa al juego: el jugador elige con qué controlador empezar.
        Devuelve el controlador seleccionado.
        '''
        fuente_titulo = pygame.font.SysFont("Arial", 28, bold=True)
        fuente_op     = pygame.font.SysFont("Arial", 20)
        fuente_sub    = pygame.font.SysFont("Arial", 15)
 
        opciones = [("[H]  Humano", controladores.Humano),("[S]  IA Segura", controladores.IA_Segura),("[P]  IA Puntos", controladores.IA_Ptos)]
        seleccion = 0  # índice resaltado con el teclado (o deja que el usuario pulse directo)
 
        while True:
            self.pantalla.fill((0, 0, 0))
 
            # Título
            titulo = fuente_titulo.render("PAC-MAN  —  Elige controlador", True, (255, 255, 0))
            self.pantalla.blit(titulo, (constantes.ancho_ventana // 2 - titulo.get_width() // 2, 180))
 
            # Opciones
            for i, (texto, _) in enumerate(opciones):
                color = (255, 255, 255) if i == seleccion else (120, 120, 120)
                op_txt = fuente_op.render(texto, True, color)
                self.pantalla.blit(op_txt, (constantes.ancho_ventana // 2 - op_txt.get_width() // 2, 260 + i * 40))
 
            # Instrucción
            sub = fuente_sub.render("Pulsa la tecla entre corchetes o con las flechas + ENTER", True, (100, 100, 100))
            self.pantalla.blit(sub, (constantes.ancho_ventana // 2 - sub.get_width() // 2, 400))
 
            pygame.display.update()
 
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_h:
                        return controladores.Humano()
                    elif evento.key == pygame.K_s:
                        return controladores.IA_Segura()
                    elif evento.key == pygame.K_p:
                        return controladores.IA_Ptos()
                    elif evento.key == pygame.K_UP:
                        seleccion = (seleccion - 1) % len(opciones)
                    elif evento.key == pygame.K_DOWN:
                        seleccion = (seleccion + 1) % len(opciones)
                    elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return opciones[seleccion][1]()
                    
    def run_game(self):
        '''
        Bucle principal del juego
        '''
        self.jugador.controlador = self.pantalla_seleccion()

        while self.run:    
            self.reloj.tick(constantes.FPS) # Limitamos a 60 fps
            self.eventos()
            self.update()
            self.dibujar()

        pygame.quit()
    
    def reset_partida(self, semilla=None):
        '''
        Permite hacer una nueva partida sin reiniciar Pygame ni recargar los sprites. 
        La simulación rápida reutiliza el mismo Game entre partidas.
        '''
        if semilla is not None:
            random.seed(semilla)

        self.vidas = self.config.vidas
        self.puntuacion = 0
        self.bolitas_comidas = 0
        self.game_over = False
        self.frame = 0
        self.frame_cambio_modo = 0
        self.frame_asustado = None
        self.modo_global = "dispersion"
 
        # Reconstruimos el mapa. 
        # Vaciamos muros, bolitas y super-bolitas antes de recrearlo para que no se acumulen partida tras partida
        self.mapa.muros.clear()
        self.mapa.bolitas.clear()
        self.mapa.super_bolitas.clear()

        # Reponemos las bolitas, super-boliras y muros (VER SI SE PUEDE SOLO PONER EN EL MAPA LOS MUROS SI NO ES LA PRIMERA VEZ PARA NO TENER Q ESTAR TOD0 EL RATO VACIANDO Y LLENANDO CUANDO NO CAMBIAN)
        self.mapa.construir_mapa()

        # Recolocamos a todos los agentes
        self.reiniciar_posiciones()
        
        self.frame = 0
        self.frame_cambio_modo = 0

    def simular_una_partida(self, semilla=None):
        '''
        Ejecuta una partida completa a máxima velocidad y devuelve sus métricas.
        Devuelve un dict; el simulador se encarga de volcarlo a CSV.
        '''
        self.reset_partida(semilla)
        # Bucle del juego sin eventos ni renderidazo ni reloj
        while not self.game_over and self.frame < self.config.max_frames:
            self.update()
            if not self.mapa.bolitas:
                break
        
        datos = {"nivel_superado": int(not self.mapa.bolitas),"muertes": self.config.vidas - self.vidas,"puntuacion": self.puntuacion,
                    "frames": self.frame,"tiempo_sim_s": round(self.frame / constantes.FPS, 3)}
        return datos

if __name__ == "__main__":
    Game().run_game()