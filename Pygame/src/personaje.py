
import pygame
from src import constantes

def escalar_imagen(imagen, escala):
    ancho = int(imagen.get_width() * escala)
    alto = int(imagen.get_height() * escala)
    return pygame.transform.scale(imagen, (ancho, alto))
class Personaje:
    def __init__(self, x, y, imagen_entera): #poner en imagen predeterminada las coordenadas del sprite del personaje en la hoja de sprites?
        self.forma = pygame.Rect(x, y, constantes.ancho_personaje, constantes.alto_personaje)
        self.sprite = imagen_entera
        #si hubiese puesto pygame.Rect(0, 0, constantes.ancho_personaje, constantes.alto_personaje) tendria que self.forma.center = (x, y)
        #self.color = color
        #self.imagen = imagen_entera.subsurface(constantes.PACMAN_COORDENADAS['derecha'][0]) #coger la parte de la imagen que corresponde al sprite del personaje
        self.frame_index = 0 #para controlar el frame de animacion
        self.frame_tiempo = pygame.time.get_ticks() #almacenamos el tiempo actual para controlar la velocidad de la animacion
        self.imagen = pygame.transform.scale(imagen_entera.subsurface(constantes.PACMAN_COORDENADAS['derecha'][self.frame_index]), (int(constantes.ancho_personaje*constantes.escala_personaje), int(constantes.alto_personaje*constantes.escala_personaje))) #escalar la imagen del personaje al tamaño definido en constantes
        #valdría si escalo la imagen del sprite y no la del personaje???
        #self.flip = False nosotros nos interesa mas rotar la imagen que invertirla, asi que en vez de flip, ponemos rotate
        self.rotate = 0

   
    
    def actualizar_animacion(self): #(podriamos añadir un string de direccion) #direccion es un string que indica la direccion del movimiento del personaje
        cooldown_animaciones = 120 #tiempo en ms entre cada cambio de frame
        tiempo_actual = pygame.time.get_ticks()
        self.imagen = escalar_imagen(self.sprite.subsurface(constantes.PACMAN_COORDENADAS['derecha'][self.frame_index]), constantes.escala_personaje) #actualizar la imagen del personaje segun la direccion del movimiento y el frame de animacion
        if tiempo_actual - self.frame_tiempo > cooldown_animaciones: #cambiar de frame cada 100 ms
            self.frame_tiempo = tiempo_actual
            self.frame_index += 1
            if self.frame_index >= 4: #si el frame index supera el numero de frames de la animacion, volver al primer frame):
                self.frame_index = 0
            #self.imagen = pygame.transform.scale(imagen_entera.subsurface(constantes.PACMAN_COORDENADAS[direccion][self.frame_index]), (int(constantes.ancho_personaje*constantes.escala_personaje), int(constantes.alto_personaje*constantes.escala_personaje))) #actualizar la imagen del personaje segun la direccion del movimiento y el frame de animacion



    def dibujar(self, interfaz): #donde lo queremos dibujar, no hace falta que sea la misma ventana 
        #if self.rotate:
            #imagen_flip = pygame.transform.flip(self.imagen, True, False)
        imagen_dr = pygame.transform.rotate(self.imagen, self.rotate)
        interfaz.blit(imagen_dr, self.forma) #dibujar la imagen del personaje en la posicion y tamaño del rectangulo
        #else:
        #    interfaz.blit(self.imagen, self.forma) #dibujar la imagen del personaje en la posicion y tamaño del rectangulo
        #pygame.draw.rect(interfaz, self.color, self.forma, width=1)

    def movimiento(self, dx, dy, dimensiones): #dx y dy son la cantidad de movimiento en x e y respectivamente, x e y son el ancho y alto de la ventana para controlar los limites
        x, y = dimensiones
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

        # Asegurarse de que el personaje al salirse de los límites de la ventana entre por el lado opuesto
        if self.forma.left < 0: #si el personaje se sale por la izquierda
            self.forma.right = dimensiones[0] 

        if self.forma.right > dimensiones[0]: #si el personaje se sale por la derecha
            self.forma.left = 0

        if self.forma.top < 0: #si el personaje se sale por arriba
            self.forma.bottom = dimensiones[1]

        if self.forma.bottom > dimensiones[1]: #si el personaje se sale por abajo
            self.forma.top = 0

        

