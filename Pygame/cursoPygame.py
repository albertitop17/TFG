import os
import pygame
import constantes


# 1. Centrar la ventana (esto debe ir ANTES de pygame.init o set_mode)
#os.environ['SDL_VIDEO_CENTERED'] = '1'


# Inicializar Pygame
pygame.init()

# Configurar la pantalla
#ancho, alto = 0, 0 #ponerlo en ingles en el real
#podria definir un fichero a parte para las constantes

pantall = pygame.display.Info()
x = (pantall.current_w -constantes.ancho_ventana) 
y = (pantall.current_h-constantes.alto_ventana) 

pantalla = pygame.display.set_mode((x, y))

pygame.display.set_caption("Mi primer juego") #titulo de la ventana

run = True
while run:
    for evento in pygame.event.get(): #registrar eventos que ocurren en el juego
        if evento.type == pygame.QUIT: #si se cierra la ventana (o alt+F4)
            run = False
