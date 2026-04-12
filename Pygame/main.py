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
        self.jugador = Pacman(x = 13 * constantes.tamano_celda, y = 24 * constantes.tamano_celda, imagen_entera = sprite, controlador = controladores.Humano()) #crear el objeto jugador (se encargara de dibujarse bien en la clase Personaje)

        # Lista de fantasmas: (x, y, color, cerebro)
        centro_x = 13 * constantes.tamano_celda
        self.fantasmas = [
            Fantasma(x=centro_x     , y=14 * constantes.tamano_celda, imagen_entera=sprite, controlador=controladores.CerebroBlinky(), color='rojo'),
            Fantasma(x=centro_x - 40, y=17 * constantes.tamano_celda, imagen_entera=sprite, controlador=controladores.CerebroPinky(), color='rosa'),
            Fantasma(x=centro_x     , y=17 * constantes.tamano_celda, imagen_entera=sprite, controlador=controladores.CerebroInky(), color='azul'),
            Fantasma(x=centro_x + 40, y=17 * constantes.tamano_celda, imagen_entera=sprite, controlador=controladores.CerebroClyde(), color='naranja'),
        ]
        
        self.puntuacion = 0
        self.bolitas_comidas = 0 #para liberar al inici a los fantasmas

        #para escribir texto
        pygame.font.init() #¿?¿?¿?¿?
        self.fuente_marcador = pygame.font.SysFont("Arial", 24, bold=True)

        self.tiempo_asustado = 0 #contador para el modo asustado

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
                if fantasma.controlador.estado == "perseguir":
                    fantasma.controlador.estado = "asustado"
                    
                    # --- NUEVO: REVERSIÓN FORZADA 180º ---
                    # Invertimos la velocidad física del ente
                    fantasma.dx *= -1
                    fantasma.dy *= -1
                    # Invertimos la memoria de dirección del cerebro
                    fantasma.controlador.dx *= -1
                    fantasma.controlador.dy *= -1

        # tiempo asustados de los fantasmas
        tiempo_actual = pygame.time.get_ticks()
        if self.tiempo_asustado > 0:
            tiempo_transcurrido = (tiempo_actual - self.tiempo_asustado) // 1000
            if tiempo_transcurrido >= 8: # Duración del susto: 8 segundos
                self.tiempo_asustado = 0
                for fantasma in self.fantasmas:
                    # Volvemos al estado normal
                    fantasma.controlador.estado = "perseguir"

        for fantasma in self.fantasmas: #actualizamos en fisica
            fantasma.actualizar(dimensiones, self.mapa.muros, objetivo=self.jugador, lista_fantasmas=self.fantasmas)

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
