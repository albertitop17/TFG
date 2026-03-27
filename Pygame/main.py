import pygame
from src import constantes
from src.pacman import Pacman
from src.fantasma import Fantasma
from src.controladores import ControladorFantasmaAleatorio, Humano, IA, CerebroBlinky, CerebroBlinky2
from src.mapa import Mapa 

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
        cerebro = Humano() #aqui se puede cambiar el controlador del personaje
        self.jugador = Pacman(x = 50, y = 50, imagen_entera = sprite, controlador = cerebro) #crear el objeto jugador (se encargara de dibujarse bien en la clase Personaje)

        cerebro_rojo = CerebroBlinky()
        self.fantasma_rojo = Fantasma(x = 250, y = 500, imagen_entera = sprite, controlador = cerebro_rojo, color = 'rojo') 

        cerebro_rosa = ControladorFantasmaAleatorio()
        self.fantasma_rosa = Fantasma(x = 350, y = 500, imagen_entera = sprite, controlador = cerebro_rosa, color = 'rosa') 

        cerebro_azul = CerebroBlinky2()
        self.fantasma_azul = Fantasma(x = 450, y = 500, imagen_entera = sprite, controlador = cerebro_azul, color = 'azul') 

        cerebro_naranja = ControladorFantasmaAleatorio()
        self.fantasma_naranja = Fantasma(x = 500, y = 500, imagen_entera = sprite, controlador = cerebro_naranja, color = 'naranja') 

    def eventos(self):
        for evento in pygame.event.get(): #registrar eventos que ocurren en el juego
            if evento.type == pygame.QUIT: #si se cierra la ventana (o alt+F4)
                self.run = False
            # habría que añadir alguna forma para cambiar de tipo de cerebro, humano o ia
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    self.jugador.controlador = IA()
                    print("IA")
                   
    def update(self):
        #actualizamos el movimiento (le decimos que lo tiene que hacer, el cómo lo sabrá el)
        dimensiones = (constantes.ancho_ventana , constantes.alto_ventana)
        self.jugador.actualizar(dimensiones, self.mapa.muros) #actualizar el jugador, le pasamos las dimensiones de la ventana para controlar los limites del movimiento y los muros para controlar las colisiones
        self.fantasma_rojo.actualizar(dimensiones, self.mapa.muros, objetivo=self.jugador.forma) # Actualizamos al fantasma. Le pasamos 'self.jugador.forma' como objetivo para que Blinky sepa donde estamos
        self.fantasma_rosa.actualizar(dimensiones, self.mapa.muros) 
        self.fantasma_azul.actualizar(dimensiones, self.mapa.muros, objetivo=self.jugador.forma) # Actualizamos al fantasma. Le pasamos 'self.jugador.forma' como objetivo para que Inky sepa donde estamos
        self.fantasma_naranja.actualizar(dimensiones, self.mapa.muros)

    def dibujar(self):
        self.pantalla.fill(constantes.color_fondo) #pintar el fondo de la pantalla
        self.mapa.dibujar(self.pantalla) #dibujar el mapa

        self.jugador.dibujar(self.pantalla)
        self.fantasma_rojo.dibujar(self.pantalla)
        self.fantasma_rosa.dibujar(self.pantalla)
        self.fantasma_azul.dibujar(self.pantalla)
        self.fantasma_naranja.dibujar(self.pantalla)

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
