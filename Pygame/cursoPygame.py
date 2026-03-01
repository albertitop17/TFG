import pygame
from src import constantes
from src.personaje import Personaje 

class Game:
    def __init__(self):
        
        # si quiero centrar la ventana (esto debe ir ANTES de pygame.init o set_mode)
        #os.environ['SDL_VIDEO_CENTERED'] = '1' 
        # Inicializar Pygame------------------------------------
        pygame.init()
        #crear la ventana del juego-------------------------------
        self.pantalla = pygame.display.set_mode((constantes.ancho_ventana , constantes.alto_ventana ))
        pygame.display.set_caption("Pacman") #titulo de la ventana
        self.reloj = pygame.time.Clock() #para controlar los fps
        self.run = True

        # Crear los jugadores y el mapa--------------------------------------------------
        #cargar la imagen del jugador (el convert_alpha es para que reconozca la transparencia)
        sprite = pygame.image.load("assets//graficos//sheet_pacman_personajes.png").convert_alpha()
        #img_jugador = pygame.transform.scale(img_jugador, (int(constantes.ancho_personaje*constantes.escala_personaje), int(constantes.alto_personaje*constantes.escala_personaje)))
        self.jugador = Personaje(x = 500, y = 100, imagen_entera = sprite) #crear el objeto jugador (se encargara de dibujarse bien en la clase Personaje)

        #defino las variables de movimiento del personaje

        self.mover_arriba = False
        self.mover_abajo = False
        self.mover_izquierda = False
        self.mover_derecha = False

    def eventos(self):
        for evento in pygame.event.get(): #registrar eventos que ocurren en el juego
            if evento.type == pygame.QUIT: #si se cierra la ventana (o alt+F4)
                self.run = False
            if evento.type == pygame.KEYDOWN: #reconoce si se presiona una tecla
                if evento.key == pygame.K_LEFT: #si la tecla es la flecha izquierda
                    self.mover_izquierda = True 
                    self.mover_derecha = False
                    self.mover_arriba = False
                    self.mover_abajo = False
                if evento.key == pygame.K_RIGHT: #si la tecla es la flecha derecha
                    self.mover_derecha = True
                    self.mover_izquierda = False
                    self.mover_arriba = False
                    self.mover_abajo = False
                if evento.key == pygame.K_UP: #si la tecla es la flecha arriba
                    self.mover_arriba = True
                    self.mover_izquierda = False
                    self.mover_derecha = False  
                    self.mover_abajo = False
                if evento.key == pygame.K_DOWN: #si la tecla es la flecha abajo
                    self.mover_abajo = True
                    self.mover_izquierda = False
                    self.mover_derecha = False
                    self.mover_arriba = False
            #print(f"{delta_x}, {delta_y}")
            """
            if evento.type == pygame.KEYUP: #reconoce si se suelta una tecla
                if evento.key == pygame.K_LEFT or evento.key == pygame.K_a: #si la tecla es la flecha izquierda
                    self.mover_izquierda = False
                if evento.key == pygame.K_RIGHT or evento.key == pygame.K_d: #si la tecla es la flecha derecha
                    self.mover_derecha = False
                if evento.key == pygame.K_UP or evento.key == pygame.K_w: #si la tecla es la flecha arriba
                    self.mover_arriba = False
                if evento.key == pygame.K_DOWN or evento.key == pygame.K_s: #si la tecla es la flecha abajo
                    self.mover_abajo = False
            """
    def update(self):
        #calculamos el movimiento del jugador
        dx = 0
        dy = 0  

        if self.mover_izquierda == True:
            dx = -constantes.velocidad
        if self.mover_derecha == True:
            dx = constantes.velocidad
        if self.mover_arriba == True: #ojo con las coordenadas, y va al reves
            dy = -constantes.velocidad
        if self.mover_abajo == True:
            dy = constantes.velocidad

        self.jugador.movimiento(dx, dy, dimensiones = (constantes.ancho_ventana , constantes.alto_ventana))
        self.jugador.actualizar_animacion() #actualizar la animacion del jugador segun su direccion de movimiento

    def dibujar(self):
        self.pantalla.fill(constantes.color_fondo) #pintar el fondo de la pantalla
        self.jugador.dibujar(self.pantalla)
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