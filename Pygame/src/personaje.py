import pygame
from src import constantes

class Personaje:
    def __init__(self, x, y, color, imagen ): #poner en imagen predeterminada las coordenadas del sprite del personaje en la hoja de sprites?
        self.forma = pygame.Rect(x, y, constantes.ancho_personaje, constantes.alto_personaje)
        self.color = color
        self.imagen = imagen
        

    def dibujar(self, interfaz): #donde lo queremos dibujar, no hace falta que sea la misma ventana 
        interfaz.blit(self.imagen, self.forma) #dibujar la imagen del personaje en la posicion y tamaño del rectangulo
        #pygame.draw.rect(interfaz, self.color, self.forma, width=1)

    def movimiento(self, dx, dy):
        self.forma.x += dx
        self.forma.y += dy