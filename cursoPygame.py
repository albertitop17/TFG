import pygame

# Inicializar Pygame
pygame.init()

# Configurar la pantalla
#ancho, alto = 0, 0 #ponerlo en ingles en el real
#podria definir un fichero a parte para las constantes
#quiero que salga a mitad de pantalla

pantall = pygame.display.Info()
x = (pantall.current_w -100) 
y = (pantall.current_h-100) 

pantalla = pygame.display.set_mode((x, y))

#pygame.display.set_caption("Mi primer juego con Pygame")

run = True
while run:
    for evento in pygame.event.get(): #registrar eventos que ocurren en el juego
        if evento.type == pygame.QUIT: #si se cierra la ventana (o alt+F4)
            run = False

print("lechu calvo")