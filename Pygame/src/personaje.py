
import pygame
from src import constantes

class Personaje:
    def __init__(self, x, y, imagen_entera): #poner en imagen predeterminada las coordenadas del sprite del personaje en la hoja de sprites?
        self.forma = pygame.Rect(x, y, constantes.ancho_personaje, constantes.alto_personaje)
        #si hubiese puesto pygame.Rect(0, 0, constantes.ancho_personaje, constantes.alto_personaje) tendria que self.forma.center = (x, y)
        #self.color = color
        self.imagen = imagen_entera.subsurface(constantes.PACMAN_COORDENADAS['derecha'][0]) #coger la parte de la imagen que corresponde al sprite del personaje
        self.imagen = pygame.transform.scale(self.imagen, (int(constantes.ancho_personaje*constantes.escala_personaje), int(constantes.alto_personaje*constantes.escala_personaje))) #escalar la imagen del personaje al tamaño definido en constantes
        self.flip = False
        self.rotate = 0

    def dibujar(self, interfaz): #donde lo queremos dibujar, no hace falta que sea la misma ventana 
        #if self.rotate:
            #imagen_flip = pygame.transform.flip(self.imagen, True, False)
        imagen_dr = pygame.transform.rotate(self.imagen, self.rotate)
        interfaz.blit(imagen_dr, self.forma) #dibujar la imagen del personaje en la posicion y tamaño del rectangulo
        #else:
        #    interfaz.blit(self.imagen, self.forma) #dibujar la imagen del personaje en la posicion y tamaño del rectangulo
        #pygame.draw.rect(interfaz, self.color, self.forma, width=1)

    def movimiento(self, dx, dy):
        if dx == 0 and dy == 0: #para que mantenga la orientacion cuando no se mueve
            return
        elif dx < 0:
            self.rotate = 180
        elif dx > 0:
            self.rotate = 0
        elif dy < 0:
            self.rotate = 90
        else:
            self.rotate = 270
        self.forma.x += dx
        self.forma.y += dy
        

