import pygame
from src import constantes

class Personaje:
    def __init__(self, x, y, color, imagen ): #poner en imagen predeterminada las coordenadas del sprite del personaje en la hoja de sprites?
        self.forma = pygame.Rect(x, y, constantes.ancho_personaje, constantes.alto_personaje)
        #si hubiese puesto pygame.Rect(0, 0, constantes.ancho_personaje, constantes.alto_personaje) tendria que self.forma.center = (x, y)
        self.color = color
        self.imagen = imagen
        self.flip = False

    def dibujar(self, interfaz): #donde lo queremos dibujar, no hace falta que sea la misma ventana 
        if self.flip:
            imagen_flip = pygame.transform.flip(self.imagen, True, False)
            interfaz.blit(imagen_flip, self.forma) #dibujar la imagen del personaje en la posicion y tamaño del rectangulo
        else:
            interfaz.blit(self.imagen, self.forma) #dibujar la imagen del personaje en la posicion y tamaño del rectangulo
        #pygame.draw.rect(interfaz, self.color, self.forma, width=1)

    def movimiento(self, dx, dy):
        if dx < 0:
            self.flip = True
        elif dx > 0:
            self.flip = False
        self.forma.x += dx
        self.forma.y += dy