import pygame
import constantes

class Personaje:
    def __init__(self, x, y, color):
        self.forma = pygame.Rect(x, y, constantes.ancho_personaje, constantes.alto_personaje)
        #otra opcion seria definirlo en el (0,0) y luego moverlo a x,y
        #self.forma.topleft = (x, y)
        #set.forma.center = (x, y)  #para centrarlo en x,y
        #set.forma.bottomright = (x, y)  #para poner la esquina inferior derecha en x,y
        #set.forma.midtop = (x, y)  #para poner el centro de la parte superior en x,y
        #set.forma.midbottom = (x, y)  #para poner el centro de la parte inferior en x,y
        #set.forma.midleft = (x, y)  #para poner el centro del lado izquierdo en x,y
        #set.forma.midright = (x, y)  #para poner el centro del lado derecho en x,y
        #set.forma.centerx = x  #para centrar horizontalmente en x
        #set.forma.centery = y  #para centrar verticalmente en y
        #set.forma.size = (ancho, alto)  #para cambiar el tamaño a ancho y alto
        #set.forma.width = ancho  #para cambiar solo el ancho
        #set.forma.height = alto  #para cambiar solo el alto
        self.color = color

    def dibujar(self, interfaz): #donde lo queremos dibujar, no hace falta que sea la misma ventana 
        pygame.draw.rect(interfaz, self.color, self.forma)

    def movimiento(self, dx, dy):
        self.forma.x += dx
        self.forma.y += dy