import os
import pygame
from src import constantes
from src.personaje import Personaje 

# Inicializar Pygame------------------------------------
pygame.init()


#crear la ventana del juego-------------------------------


# 1. Centrar la ventana (esto debe ir ANTES de pygame.init o set_mode)
#os.environ['SDL_VIDEO_CENTERED'] = '1'


# Configurar la pantalla
#ancho, alto = 0, 0 #ponerlo en ingles en el real
#podria definir un fichero a parte para las constantes

#se puede hacer con fullscreen tambien
pantall = pygame.display.Info()
x = constantes.ancho_ventana 
y = constantes.alto_ventana 

pantalla = pygame.display.set_mode((x, y))

pygame.display.set_caption("Mi primer juego") #titulo de la ventana



# Crear el jugador--------------------------------------------------

#cargar la imagen del jugador (el convert_alpha es para que reconozca la transparencia)
sprite = pygame.image.load("Pygame//assets//graficos//sheet_pacman_personajes.png").convert_alpha()
#img_jugador = pygame.transform.scale(img_jugador, (int(constantes.ancho_personaje*constantes.escala_personaje), int(constantes.alto_personaje*constantes.escala_personaje)))



jugador = Personaje(x = 500, y = 100, imagen_entera = sprite) #crear el objeto jugador (se encargara de dibujarse bien en la clase Personaje)



#defino las variables de movimiento del personaje

mover_arriba = False
mover_abajo = False
mover_izquierda = False
mover_derecha = False

reloj = pygame.time.Clock() #para controlar los fps

run = True
while run:

    #para controlar el FRAME RATE
    reloj.tick(constantes.FPS) #limitar a 60 fps

    pantalla.fill(constantes.color_fondo) #pintar el fondo de la pantalla

    #calculamos el movimiento del jugador
    dx = 0
    dy = 0

    if mover_izquierda == True:
        dx = -constantes.velocidad
    if mover_derecha == True:
        dx = constantes.velocidad
    if mover_arriba == True: #ojo con las coordenadas, y va al reves
        dy = -constantes.velocidad
    if mover_abajo == True:
        dy = constantes.velocidad

    #para mover al jugador
    jugador.movimiento(dx, dy, x, y)

    jugador.actualizar_animacion() #actualizar la animacion del jugador segun su direccion de movimiento

    jugador.dibujar(pantalla)

    for evento in pygame.event.get(): #registrar eventos que ocurren en el juego
        if evento.type == pygame.QUIT: #si se cierra la ventana (o alt+F4)
            run = False
        if evento.type == pygame.KEYDOWN: #reconoce si se presiona una tecla
            if evento.key == pygame.K_LEFT or evento.key == pygame.K_a: #si la tecla es la flecha izquierda
                mover_izquierda = True
            if evento.key == pygame.K_RIGHT or evento.key == pygame.K_d: #si la tecla es la flecha derecha
                mover_derecha = True
            if evento.key == pygame.K_UP or evento.key == pygame.K_w: #si la tecla es la flecha arriba
                mover_arriba = True
            if evento.key == pygame.K_DOWN or evento.key == pygame.K_s: #si la tecla es la flecha abajo
                mover_abajo = True
        #print(f"{delta_x}, {delta_y}")
        if evento.type == pygame.KEYUP: #reconoce si se suelta una tecla
            if evento.key == pygame.K_LEFT or evento.key == pygame.K_a: #si la tecla es la flecha izquierda
                mover_izquierda = False
            if evento.key == pygame.K_RIGHT or evento.key == pygame.K_d: #si la tecla es la flecha derecha
                mover_derecha = False
            if evento.key == pygame.K_UP or evento.key == pygame.K_w: #si la tecla es la flecha arriba
                mover_arriba = False
            if evento.key == pygame.K_DOWN or evento.key == pygame.K_s: #si la tecla es la flecha abajo
                mover_abajo = False



    pygame.display.update() #actualizar la pantalla

pygame.quit() #cerrar pygame al salir del bucle