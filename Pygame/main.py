import pygame
from src import constantes
from src import controladores
from src.pacman import Pacman
from src.fantasma import Fantasma
from src.mapa import Mapa 

DEBUG = constantes.DEBUG
class Game:
    def __init__(self):
        
        # Inicializar Pygame------------------------------------
        pygame.init()
        #crear la ventana del juego-------------------------------
        self.pantalla = pygame.display.set_mode((constantes.ancho_ventana , constantes.alto_ventana ))
        pygame.display.set_caption("Pacman") #titulo de la ventana

        self.reloj = pygame.time.Clock() #para controlar los fps
        self.run = True

        # Creamos el mapa y los jugadores --------------------------------------------------
        sprite = pygame.image.load("assets//graficos//sheet_pacman_personajes.png").convert_alpha()
        self.mapa = Mapa() #crear el mapa 

        #PACMAN
        self.spawn_pacman = (13 * constantes.tamano_celda, 24 * constantes.tamano_celda) #para luego respawnear
        self.jugador = Pacman(x = self.spawn_pacman[0], y = self.spawn_pacman[1], imagen_entera = sprite, controlador = controladores.Humano()) #crear el objeto jugador (se encargara de dibujarse bien en la clase Personaje)

        # Lista de fantasmas: (x, y, color, cerebro)
        centro_x = 13 * constantes.tamano_celda
        self.fantasmas = [
            Fantasma(x=centro_x     , y=14 * constantes.tamano_celda, imagen_entera=sprite, controlador=controladores.CerebroBlinky(), color='rojo'),
            Fantasma(x=centro_x - 40, y=17 * constantes.tamano_celda, imagen_entera=sprite, controlador=controladores.CerebroPinky(), color='rosa'),
            Fantasma(x=centro_x     , y=17 * constantes.tamano_celda, imagen_entera=sprite, controlador=controladores.CerebroInky(), color='azul'),
            Fantasma(x=centro_x + 40, y=17 * constantes.tamano_celda, imagen_entera=sprite, controlador=controladores.CerebroClyde(), color='naranja'),
        ]
        

        self.vidas = 3
        self.puntuacion = 0
        self.bolitas_comidas = 0 #para liberar al inici a los fantasmas
        self.game_over = False

        #para escribir texto
        pygame.font.init() #¿?¿?¿?¿?
        self.fuente_marcador = pygame.font.SysFont("Arial", 24, bold=True)

        self.tiempo_asustado = 0 #contador para el modo asustado

        self.modo_global = "dispersion" # El juego empieza siempre en dispersión
        self.tiempo_cambio_modo = pygame.time.get_ticks()
        # Tiempos en segundos: [Tiempo Dispersión, Tiempo Persecución]
        self.duraciones_oleada = constantes.duraciones_oleada

        self.modo_debug = 0 # 0: Apagado, 1: Valores (Cajas), 2: Ruta (Prediccion siguientes pasos) 

    def eventos(self):
        for evento in pygame.event.get(): #registrar eventos que ocurren en el juego
            if evento.type == pygame.QUIT: #si se cierra la ventana (o alt+F4)
                self.run = False
            # habría que añadir alguna forma para cambiar de tipo de cerebro, humano o ia
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    self.jugador.controlador = controladores.IA()
                    print("IA")
                if evento.key == pygame.K_d:
                    # Alternar entre 0, 1 y 2
                    self.modo_debug = (self.modo_debug + 1) % 3
                    #Avisamos a todos los cerebros del nuevo modo
                    for f in self.fantasmas:
                        if hasattr(f.controlador, 'modo_debug'):
                            f.controlador.modo_debug = self.modo_debug
                   
    def update(self):
        #actualizamos el movimiento (le decimos que lo tiene que hacer, el cómo lo sabrá el) 
        dimensiones = (constantes.ancho_ventana , constantes.alto_ventana)
        self.jugador.actualizar(dimensiones, self.mapa.muros) #actualizar el jugador, le pasamos las dimensiones de
            #la ventana para controlar los limites del movimiento y los muros para controlar las colisiones

        #Mecánica de comer bolitas: comprobamos si el rectángulo del jugador colisiona con alguna bolita o super-bolita
        # collidelist devuelve el índice del elemento con el que chocamos, o -1 si no chocamos con nada
        indice_bolita = self.jugador.forma.collidelist(self.mapa.bolitas)
        if indice_bolita != -1:
            # Eliminamos la bolita de la lista (desaparece visual y físicamente)
            self.mapa.bolitas.pop(indice_bolita)
            self.puntuacion += 10
            self.bolitas_comidas += 1
            # (¡Aquí irá la lógica de liberar fantasmas más adelante!)

        indice_super = self.jugador.forma.collidelist(self.mapa.super_bolitas)
        if indice_super != -1:
            self.mapa.super_bolitas.pop(indice_super)
            self.puntuacion += 50
            
            # activamos el modo asustado en los fantasmas
            self.tiempo_asustado = pygame.time.get_ticks()
            for fantasma in self.fantasmas:
                # Solo les damos la vuelta si estaban persiguiendo (si son "ojos" no se inmutan)
                if fantasma.controlador.estado in ["perseguir", "dispersion"]:
                    fantasma.controlador.estado = "asustado" #tienen que dar la vuelta 180º y reducir su velocidad
                    # frenado y giro 180º (forzamos la velocidad a magnitud 1 en sentido contrario)
                    # velocidad física del ente 
                    if fantasma.dx != 0: fantasma.dx = -constantes.velocidad_asustados if fantasma.dx > 0 else constantes.velocidad_asustados
                    if fantasma.dy != 0: fantasma.dy = -constantes.velocidad_asustados if fantasma.dy > 0 else constantes.velocidad_asustados
                    # memoria de dirección del cerebro
                    if fantasma.controlador.dx != 0: fantasma.controlador.dx = -constantes.velocidad_asustados if fantasma.controlador.dx > 0 else constantes.velocidad_asustados
                    if fantasma.controlador.dy != 0: fantasma.controlador.dy = -constantes.velocidad_asustados if fantasma.controlador.dy > 0 else constantes.velocidad_asustados

        # controlador del tiempo asustados de los fantasmas 
        tiempo_actual = pygame.time.get_ticks()
        if self.tiempo_asustado > 0:
            tiempo_transcurrido = (tiempo_actual - self.tiempo_asustado) // 1000
            if tiempo_transcurrido >= 8: # Duración del susto: 8 segundos
                self.tiempo_asustado = 0
                for fantasma in self.fantasmas:
                    if fantasma.controlador.estado == "asustado":
                        # Volvemos al estado normal
                        fantasma.controlador.estado = "perseguir"
                        # les devolvemos la velocidad normal
                        vel = constantes.velocidad
                        if fantasma.dx != 0: fantasma.dx = vel if fantasma.dx > 0 else -vel
                        if fantasma.dy != 0: fantasma.dy = vel if fantasma.dy > 0 else -vel
                        if fantasma.controlador.dx != 0: fantasma.controlador.dx = vel if fantasma.controlador.dx > 0 else -vel
                        if fantasma.controlador.dy != 0: fantasma.controlador.dy = vel if fantasma.controlador.dy > 0 else -vel

                        # sincronizamos la cuadricula impar
                        # Si se han quedado en un píxel impar, los empujamos 1 píxel hacia adelante para que no se salten la baldosa
                        if fantasma.forma.x % 2 != 0: 
                            fantasma.forma.x += 1 if fantasma.dx > 0 else -1
                        if fantasma.forma.y % 2 != 0:
                            fantasma.forma.y += 1 if fantasma.dy > 0 else -1

        for fantasma in self.fantasmas: #actualizamos en fisica
            fantasma.actualizar(dimensiones, self.mapa.muros, objetivo=self.jugador, lista_fantasmas=self.fantasmas)

        for fantasma in self.fantasmas:
            # Comprobamos si sus rectángulos se superponen
            if self.jugador.forma.colliderect(fantasma.forma): #nos hemos comido al fantasma o nos ha comido a nosotros
                if fantasma.controlador.estado == "asustado":
                    fantasma.controlador.estado = "ojos"
                    self.puntuacion += 200
                    pygame.time.delay(1000)
                    #volvemos a sincronizarlo a la cuadricula (par)
                    if fantasma.forma.x % 2 != 0: 
                        fantasma.forma.x += 1 if fantasma.dx > 0 else -1
                    if fantasma.forma.y % 2 != 0:
                        fantasma.forma.y += 1 if fantasma.dy > 0 else -1
                        
                elif fantasma.controlador.estado in ["perseguir", "dispersion"]:
                    self.morir() #perdemos una vida y reiniciamos posiciones
                    break # Salimos del bucle para evitar múltiples colisiones en el mismo frame
                
        # control del cronometro de oleadas (persecución/dispersión)
        tiempo_actual = pygame.time.get_ticks()
        
        # Si no estamos en modo asustado (el susto pausa el cronómetro de oleadas)
        if self.tiempo_asustado == 0:
            tiempo_transcurrido_oleada = (tiempo_actual - self.tiempo_cambio_modo) // 1000
            # Determinamos cuánto debe durar el modo actual
            duracion_actual = self.duraciones_oleada[0] if self.modo_global == "dispersion" else self.duraciones_oleada[1]

            if tiempo_transcurrido_oleada >= duracion_actual:
                # reseteamos el reloj
                self.tiempo_cambio_modo = tiempo_actual     
                # alternamos el modo
                self.modo_global = "perseguir" if self.modo_global == "dispersion" else "dispersion"
                # aplicamos el cambio a los fantasmas y forzamos el giro de 180º
                for fantasma in self.fantasmas:
                    # Solo aplicamos esto a fantasmas vivos (los ojos y los asustados van a lo suyo)
                    if fantasma.controlador.estado in ["perseguir", "dispersion"]:
                        fantasma.controlador.estado = self.modo_global
                        # al igual que cunado comemos la super-bolita, se hace un giro de 180º
                        fantasma.dx *= -1
                        fantasma.dy *= -1
                        fantasma.controlador.dx *= -1
                        fantasma.controlador.dy *= -1

    def dibujar(self):
        self.pantalla.fill(constantes.color_fondo) #pintar el fondo de la pantalla
        self.mapa.dibujar(self.pantalla) #dibujar el mapa

        #dibujamos el jugador y los fantasmas
        self.jugador.dibujar(self.pantalla, self.modo_debug) 
        for fantasma in self.fantasmas:
            fantasma.dibujar(self.pantalla, self.modo_debug)

        #dibujar el marcador (en la esquina superior izquierda)
        texto_puntos = self.fuente_marcador.render(f"SCORE: {self.puntuacion}", True, (255, 255, 255))
        self.pantalla.blit(texto_puntos, (10, 5))

        pygame.display.update() #actualizar la pantalla para mostrar los cambios

    def reiniciar_posiciones(self):
        """Devuelve a Pac-Man y a los fantasmas a sus posiciones de inicio"""
        # reseteamos el pacman
        self.jugador.forma.x, self.jugador.forma.y = self.spawn_pacman
        self.jugador.dx, self.jugador.dy = 0, 0
        self.jugador.controlador.dx, self.jugador.controlador.dy = 0, 0

        # reseteamos fantasmas
        centro_x = 13 * constantes.tamano_celda
        posiciones_fantasmas = [
            (centro_x, 14 * constantes.tamano_celda),      # Blinky
            (centro_x - 40, 17 * constantes.tamano_celda), # Pinky
            (centro_x, 17 * constantes.tamano_celda),      # Inky
            (centro_x + 40, 17 * constantes.tamano_celda)  # Clyde
        ]
        for i, fantasma in enumerate(self.fantasmas):
            fantasma.forma.x, fantasma.forma.y = posiciones_fantasmas[i]
            fantasma.controlador.estado = "dispersion" # Vuelven al estado inicial de oleada
            fantasma.controlador.dx = constantes.velocidad # Reset memoria cerebro
            fantasma.controlador.dy = 0
            fantasma.dx = constantes.velocidad # Reset velocidad física
            fantasma.dy = 0
        # reseteamos el sistema de oleadas (dispersión/persecución) 
        self.modo_global = "dispersion"
        self.tiempo_cambio_modo = pygame.time.get_ticks()

    def morir(self):
        self.vidas -= 1
        #indicar en pantalla que hemos muerto con algun texto??        
        if self.vidas <= 0:
            self.game_over = True
            #acabar el juego de alguna forma???
        else:
            # Pausa de 1.5 segundos antes de reaparecer
            pygame.time.delay(1500)
            self.reiniciar_posiciones()

    def run_game(self):
        while self.run:
            #para controlar el FRAME RATE
            self.reloj.tick(constantes.FPS) #limitar a 60 fps
            self.eventos()
            self.update()
            self.dibujar()
        pygame.quit() #cerrar pygame al salir del bucle

if __name__ == "__main__":
    Game().run_game()