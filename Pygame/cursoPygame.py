import os
import pygame
import constantes
from personaje import Personaje 



jugador = Personaje(x = 500, y = 100, color = (0, 200, 255))


# 1. Centrar la ventana (esto debe ir ANTES de pygame.init o set_mode)
#os.environ['SDL_VIDEO_CENTERED'] = '1'


# Inicializar Pygame
pygame.init()

# Configurar la pantalla
#ancho, alto = 0, 0 #ponerlo en ingles en el real
#podria definir un fichero a parte para las constantes

#se puede hacer con fullscreen tambien
pantall = pygame.display.Info()
x = (pantall.current_w -constantes.ancho_ventana) 
y = (pantall.current_h-constantes.alto_ventana) 

pantalla = pygame.display.set_mode((x, y))

pygame.display.set_caption("Mi primer juego") #titulo de la ventana


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
    jugador.movimiento(dx, dy)

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