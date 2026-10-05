import pygame
import random
from src import constantes
from src import controladores
from src.pacman import Pacman
from src.fantasma import Fantasma
from src.mapa import Mapa 
from sim.config_sim import ConfigSimulacion


DEBUG = constantes.DEBUG
class Game:
    '''
    Clase Principal (Motor del juego)
    Controla el bucle del juego, instanciando las entidades, gestionando colisiones y cambiando los estados de los fantasmas

    Todas las dinámicas temporales (oleadas dispersión/persecución y duración del estado asustado) se miden en frames 
    Así el movimiento y los temporizadores comparten una única unidad: 1 frame
    
    Para jugar: Game().run_game()  (config=None -> con ventana y sprites).
    Para simular: Game(ConfigSimulacion(sin_ventana=True)).simular_una_partida().
    '''

    def __init__(self, config = None):
        
        # Si config es None se inicializa el código principal: con ventana, y los 3 posibles controladores.
        if config is None:
            config = ConfigSimulacion(sin_ventana=False, vidas=3)
        
        # Obtenemos qué tipo de partida se debe ejecutar
        self.config = config
        self.sin_ventana = config.sin_ventana

        # Inicializamos el motor de Pygame
        pygame.init()
        # Inicializamos las fuentes por si acaso (aunque pygame.init() debería hacerlo)
        pygame.font.init() 

        # En función de la configuración escogida, se crea o no la pantalla principal
        if self.sin_ventana:
            # No se renderiza nada
            self.pantalla = None
            sprite = pygame.Surface((256, 256), pygame.SRCALPHA) # Sprite falso para que no falle
        else:
            # Creamos la ventana del juego
            self.pantalla = pygame.display.set_mode((constantes.ancho_ventana, constantes.alto_ventana))
            pygame.display.set_caption("TFG Pacman") # Título de la ventana
            sprite = pygame.image.load("assets//graficos//sheet_pacman_personajes.png").convert_alpha()


        self.sprite = sprite
        self.reloj = pygame.time.Clock() # Para controlar los FPS
        self.run = True

        # Ahora creamos el mapa, a Pac-Man y a los fantasmas

        # Mapa
        self.mapa = Mapa(self.config.mapa)
        puerta_colision = pygame.Rect(constantes.x_puerta, 11 * constantes.tamano_celda + constantes.offset_y_mapa, constantes.ancho_puerta, constantes.tamano_celda)
        self.muros_pacman = self.mapa.muros + [puerta_colision]  # añadimos la puerta como muro solo para Pac-Man

        # Pacman
        self.spawn_pacman = (13 * constantes.tamano_celda, 24 * constantes.tamano_celda) # Guardamos la variable para luego poder reaparecer

        # Elegimos el controlador. En caso de la IA_Ptos inicializamos los radios de caza, super y bolita
        if self.sin_ventana:
            if self.config.controlador_pacman == controladores.IA_Ptos:
                ctrl_pacman = controladores.IA_Ptos(radio_caza=self.config.radios_ia.get("radio_caza"),radio_super=self.config.radios_ia.get("radio_super"),
                        radio_bolita_optima=self.config.radios_ia.get("radio_bolita_optima"))
            else:
                ctrl_pacman = self.config.controlador_pacman()
        else:
            # Controlador provisional para cuando se juega con ventana. El real se elige luego
            ctrl_pacman = controladores.Humano()

        self.jugador = Pacman(x=self.spawn_pacman[0], y=self.spawn_pacman[1], imagen_entera=sprite, controlador=ctrl_pacman)

        # Fantasmas (a partir de la configuración, para así poder extrapolarlo y hacer experimentos en un futuro)
        self.fantasmas = self.crear_fantasmas()
        
        # Variables de Estado 
        self.vidas = self.config.vidas   # Numero de vidas (escogidas en la configuración, 3 por defecto)
        self.puntuacion = 0              # Contador de la puntuación
        self.bolitas_comidas = 0         # Para liberar al incio a los fantasmas
        self.game_over = False           # Indica si la partida ha acabado

        # Interfaz y Tipografía
        self.fuente_marcador = pygame.font.SysFont("Arial", 24, bold=True)

        # Controladores de tiempo (temporizadores basados en frames)
        FPS = constantes.FPS
        self.frame = 0                  # Contador de frames de la partida
        self.frame_asustado = None      # Frame en el que se ha comido la ultima super-bolita (None significa que no está en susto)

        self.frame_cambio_modo = 0      # Frame del último cambio de oleada
        self.modo_global = "dispersion" # El juego empieza siempre en dispersión

        # Duraciones convertidas de segundos a frames (una sola vez). Asi se puede hacer las simulaciones sin fallos.
        self.duraciones_oleada_frames = [s * FPS for s in constantes.duraciones_oleada]
        self.frames_susto    = constantes.susto_total_s    * FPS
        self.frames_parpadeo = constantes.susto_parpadeo_s * FPS
        self.frames_peligro  = constantes.susto_peligro_s  * FPS
        self.bolitas_para_liberarse = [e.liberar_con for e in self.config.fantasmas] # REVISAR ESTA LINEA

        self.modo_debug = 0 # 0: Apagado, 1: Valores (Cajas), 2: Ruta (Prediccion siguientes pasos) 

    def crear_fantasmas(self):
        '''
        Instancia los fantasmas que se hayan establecido en la configuración.
        Por defecto los 4 originales.
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
 
                # 0: control manual de Blinky (queda comentado pero se podría probar)
                # elif evento.key == pygame.K_0:
                #     self.fantasmas[0].controlador = controladores.Humano()
    
    def pausas_visuales(self, ms):
        '''
        Pausa para que quede como el juego real. Pero para la simulación es contraproducente.
        Como no avanza el contador de frames, estas pausas no consumen tiempo de juego (ni de oleada ni de susto)
        '''
        if not self.sin_ventana:
            pygame.time.delay(ms)


    def update(self):
        '''
        Núcleo del juego. 
        Actualiza el movimiento, trata las colisiones y gestiona las oleadas de los fantasmas (dispersión <-> perseguir). 
        '''
        if self.game_over:
            return
        
        # 1 update equivale a 1 frame que equivale a 1 paso de movimiento 
        self.frame += 1

        dimensiones = (constantes.ancho_ventana , constantes.alto_ventana)

        # Actualizamos a Pacman 
        self.jugador.actualizar(dimensiones=dimensiones, muros=self.muros_pacman, lista_fantasmas=self.fantasmas, 
                                mapa_logico=self.mapa.matriz, bolitas=self.mapa.bolitas,super_bolitas=self.mapa.super_bolitas)

        # Mecánica de comer bolitas: comprobamos si el rectángulo del jugador colisiona con alguna bolita
        indice_bolita = self.jugador.forma.collidelist(self.mapa.bolitas)
        if indice_bolita != -1:
            self.mapa.bolitas.pop(indice_bolita) # La eliminamos también visualmente
            self.puntuacion += 10
            self.bolitas_comidas += 1

            if self.mapa.bolitas == []:
                self.game_over = True # Acaba la partida

            # Mecánica para ir liberando los fantasmas
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
    
        # Actualizamos los fantasmas
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
                    if not self.sin_ventana: # Dibujamos el 200 en pantalla durante el delay
                        sprite_200 = self.sprite.subsurface(pygame.Rect(1, 136, 15, 15)) 
                        sprite_200 = pygame.transform.scale(sprite_200, (constantes.tamano_celda, constantes.tamano_celda))
                        self.pantalla.blit(sprite_200, (fantasma.forma.x, fantasma.forma.y))
                        pygame.display.update()
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
        
        # # Dibujamos a los fantasmas
        # for fantasma in self.fantasmas:
        #     fantasma.dibujar(self.pantalla, self.modo_debug)
        orden = self.fantasmas if (self.frame // 20) % 2 == 0 else reversed(self.fantasmas)
        for fantasma in orden:
            fantasma.dibujar(self.pantalla, self.modo_debug)
        
        # Dibujamos el HUD superior
        texto_puntos = self.fuente_marcador.render(f"SCORE: {self.puntuacion}", True, (255, 255, 255))
        self.pantalla.blit(texto_puntos, (10, 5))

        vidas = self.fuente_marcador.render(f"VIDAS: {self.vidas}", True, (255, 255, 255)) 
        self.pantalla.blit(vidas, (430, 5))

        # Dibujamos el HUD inferior
        y_hud = constantes.offset_y_mapa + len(self.mapa.matriz) * constantes.tamano_celda + 4

        fuente_ctrl = pygame.font.SysFont("Arial", 20, bold=True)
        fuente_tecla = pygame.font.SysFont("Arial", 14, bold=True)

        # Color del controlador activo
        if isinstance(self.jugador.controlador, controladores.Humano):
            color_ctrl = (255, 255,   0)
            nombre_ctrl = "Humano"
        elif isinstance(self.jugador.controlador, controladores.IA_Segura):
            color_ctrl = (210, 160, 255)
            nombre_ctrl = "IA Segura"
        elif isinstance(self.jugador.controlador, controladores.IA_Ptos):
            color_ctrl = (100, 255, 160)
            nombre_ctrl = "IA Puntos"

        # Izquierda: nombre del controlador en grande
        ctrl_surf = fuente_ctrl.render(nombre_ctrl, True, color_ctrl)
        self.pantalla.blit(ctrl_surf, (10, y_hud + 14))

        # Línea separadora vertical
        pygame.draw.line(self.pantalla, (60, 60, 60),(175, y_hud + 2), (175, y_hud + 54), 1)

        # Dibujamos las instrucciones en las teclas
        modos_debug = ["Apagado", "Valores", "Ruta", "Peligro"]
        teclas = [
            ("H: Humano", (255, 255, 0), 0, 0),("S: IA Segura", (210, 160, 255), 1, 0),
            ("P: IA Puntos", (100, 255, 160),   0, 1),
            (f"D: Debug [{modos_debug[self.modo_debug]}]", (190, 120, 60),   1, 1),
        ]
        for texto, color, col, fila in teclas:
            t = fuente_tecla.render(texto, True, color)
            self.pantalla.blit(t, (182 + col * 188, y_hud + 6 + fila *  26))
        
        if self.game_over: # Se imprime cuando se acaba la partida 
            if not self.mapa.bolitas: # Se ha acabado ganando
                texto = "VICTORIA"
                color = (0, 255, 0)
            else: # Se ha acabado perdiendo
                texto =  "DERROTA"
                color = (255, 50, 50)

            fin = self.fuente_marcador.render(texto, True, color)
            self.pantalla.blit(fin, (constantes.ancho_ventana // 2 - fin.get_width() // 2, 5))
        

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

        # Trabajo futuro: animaciones muerte 
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
        fuente_op    = pygame.font.SysFont("Arial", 22, bold=True)
        fuente_tecla = pygame.font.SysFont("Arial", 22)
        fuente_sub   = pygame.font.SysFont("Arial", 18, bold=True)
 
        opciones = [
            ("[H]", "Humano",    controladores.Humano,    (255, 255,   0)),
            ("[S]", "IA Segura", controladores.IA_Segura, (210, 160, 255)),
            ("[P]", "IA Puntos", controladores.IA_Ptos,   (100, 255, 160)),
        ]

        seleccion = 0
        # Logo PAC-MAN del sprite sheet 
        logo = self.sprite.subsurface(pygame.Rect(85, 172, 191, 47))
        logo = pygame.transform.scale(logo, (191 * 2, 47 * 2))
 
        # Frames de Pac-Man mirando a la derecha (4 frames)
        coords_pac = [(18,0,15,15),(1,0,15,15),(18,0,15,15),(35,0,15,15)]
        sprites_pac = []
        for cx, cy, cw, ch in coords_pac:
            img = self.sprite.subsurface(pygame.Rect(cx, cy, cw, ch))
            img = pygame.transform.scale(img, (cw * 3, ch * 3))
            sprites_pac.append(img)
 
        ancho  = constantes.ancho_ventana
        cx_pan = ancho // 2
 
        # Bolitas distribuidas por toda la pantalla (x, y)
        bolitas_pos = [
            # Esquinas
            (25, 30), (515, 30), (25, 660), (515, 660),
            # Puestas aleatoriamente para rellenar
            (100, 25), (200, 40), (310, 22), (420, 38),(80, 670), (180, 655), (290, 672), (390, 658), (490, 668),
            (20, 130), (30, 220), (18, 320), (28, 420), (22, 520),(530, 130), (540, 230), (528, 340), (535, 440), (525, 540),
            (60, 260), (480, 255), (55, 340), (490, 335),(65, 415), (475, 420),(100, 490), (440, 485), (100,550),(125,610),
            (200, 600) ,(280,550), (350, 600), (400, 560), (430,620), (300,440),(230,435),(360,445),(160,440),(420,440)
        ]
 
        frame_anim = 0

        while True:
            self.pantalla.fill((0, 0, 0))
            frame_anim += 1
            frame_pac  = (frame_anim // 8) % 4
 
            # Dibujamos el logo
            self.pantalla.blit(logo, (cx_pan - logo.get_width() // 2, 65))
 
            # Dibujamos bolitas sincronizadas con Pac-Man de decoración
            r_bolita = 5 if frame_pac != 3 else 3
            for bx, by in bolitas_pos:
                pygame.draw.circle(self.pantalla, (255, 184, 174), (bx, by), r_bolita)

            # Lo coloreamos más fuerte si lo estamos seleccionando
            for i, (tecla, nombre, _, color) in enumerate(opciones):
                y      = 210 + i * 80
                es_sel = (i == seleccion)
 
                # Fondo de selección
                rect_sel = pygame.Rect(cx_pan - 140, y - 8, 270, 58)
                if es_sel:
                    pygame.draw.rect(self.pantalla, (30, 30, 30), rect_sel, border_radius=8)
                    pygame.draw.rect(self.pantalla, color, rect_sel, width=2, border_radius=8)
 
                # Tecla y nombre
                color_txt = color if es_sel else tuple(c // 4 for c in color)
                t_tecla  = fuente_tecla.render(tecla,  True, color_txt)
                t_nombre = fuente_op.render(nombre, True, color_txt)
                self.pantalla.blit(t_tecla,  (cx_pan - 118, y + 10))
                self.pantalla.blit(t_nombre, (cx_pan -  66, y + 10))
 
                # Pac-Man animado fuera del recuadro
                if es_sel:
                    self.pantalla.blit(sprites_pac[frame_pac], (rect_sel.right + 10, y + 6))
 
            # Instrucciones
            lineas = ["Pulsa la tecla correspondiente","o","mueve con las flechas + ENTER"]
            for i, linea in enumerate(lineas):
                surf = fuente_sub.render(linea, True, (210, 210, 210))
                self.pantalla.blit(surf, (cx_pan - surf.get_width() // 2, 455 + i * 22))
 
            pygame.display.update()
            self.reloj.tick(60)

            # Gestionamos la selección del modo de juego
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
                        return opciones[seleccion][2]()
 
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

        # Reponemos las bolitas y super-bolitas 
        self.mapa.construir_mapa()

        # Recolocamos a todos los agentes
        self.reiniciar_posiciones()
        
        self.frame = 0
        self.frame_cambio_modo = 0

    def simular_una_partida(self, semilla=None):
        '''
        Ejecuta una partida completa a máxima velocidad y devuelve sus métricas.
        Devuelve un dict; el simulador se encarga de llevarlo al CSV.
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


    def ver_partida(self, controlador, semilla):
        '''
        Reproduce con ventana una partida concreta a velocidad normal, fijando la semilla 
        para poder repetir una partida ya simulada (por ejemplo, la de mejor puntuación).
        Se salta la pantalla de selección de controlador.
        '''
        random.seed(semilla)
        self.jugador.controlador = controlador

        while self.run:
            self.reloj.tick(constantes.FPS)
            self.eventos()
            self.update()
            self.dibujar()

        pygame.quit()

if __name__ == "__main__":
    # Vemos qué modo se quiere ejecutar
    print("\n1 - Jugar\n2 - Simular\n3 - Recorrer valores de un radio")
    # Pedimos el modo para jugar, en caso de que no pongan uno se inicializa el juego normal
    opcion = input("Elige el modo a ejecutar: ").strip() or "1" # Strip elimina espacios sin querer 

    if opcion == "1":
        Game().run_game()

    elif opcion == "2":
        from sim.simulador import simular
        from sim.config_sim import ConfigSimulacion
        from src import controladores

        # En caso de ser una simulación pedimos el modo concreto de controlador a simular
        print("Elige el controlador de Pac-Man: 1 = IA_Ptos,  2 = IA_Segura")
        controlador = controladores.IA_Ptos if (input("Controlador: ").strip() or "1") != "2" else controladores.IA_Segura

        numero_partidas = input("Partidas: ").strip()
        n = int(numero_partidas) if numero_partidas.isdigit() else 10000 # En caso de que no se ponga bien un numero de partidas 
        csv = input("Nombre del CSV donde escribir (.csv): ").strip() or "resultados.csv" # Si no predeterminado en resultados.csv 
        consola = (input("¿Quieres imprimir cada partida por pantalla? (s/n): ").strip().lower() == "s")

        simular(config=ConfigSimulacion(sin_ventana=True, controlador_pacman=controlador), n_partidas=n, csv_path=csv, consola = consola)

    elif opcion == "3":
        from sim.barrido import barrido_radio

        radios = {"1": "radio_caza", "2": "radio_super", "3": "radio_bolita_optima"}
        print("Elige el radio a recorrer: 1=radio_caza  2=radio_super  3=radio_bolita_optima")
        nombre = radios.get(input("Radio: ").strip(), "radio_caza") # Si no, se usa el radio de caza

        numero_partidas = input("Cuantas partidas por cada valor del radio: ").strip()
        n = int(numero_partidas) if numero_partidas.isdigit() else 2500 # En caso de que no se ponga bien, 2500 por defecto
        png = input(f"Nombre del archivo PNG donde dibujar las gráficas (.png): ").strip() or None # Nombre de la imagen de salida
        csv = input("Nombre del archivo CSV (.csv) (Enter para no guardar): ").strip() or None

        # Si se quisiese cambia rel predeterminado de los valores de las celdas se hace aqui abajo (trabajo futuro sacarlo fuera)
        barrido_radio(nombre, valores_celdas=[2, 4, 6, 8, 10, 12, 14], n_partidas=n, png_path=png, csv_path= csv) 

    elif opcion == "4":
        from src import controladores
        Game().ver_partida(controlador=controladores.IA_Ptos(), semilla=648) #7454
    # from sim.config_sim import ConfigSimulacion
    # from src import controladores

    # cfg = ConfigSimulacion(sin_ventana=False, controlador_pacman=controladores.IA_Ptos)
    # juego = Game(cfg)
    # juego.jugador.controlador = controladores.IA_Ptos()
    # juego.simular_una_partida(semilla=41)

    