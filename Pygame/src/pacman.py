import pygame
from src import constantes
from src.fisica import EnteFisico

def escalar_imagen(imagen, escala):
    ancho = int(imagen.get_width() * escala)
    alto = int(imagen.get_height() * escala)
    return pygame.transform.scale(imagen, (ancho, alto))

class Pacman(EnteFisico):
    def __init__(self, x, y, imagen_entera, controlador):
        super().__init__(x, y, controlador) #llamamos a la fisica del padre

        self.sprite = imagen_entera
        self.frame_index = 0 #para controlar el frame de animacion
        self.frame_tiempo = pygame.time.get_ticks() #almacenamos el tiempo actual para controlar la velocidad de la animacion
        self.imagen = pygame.transform.scale(imagen_entera.subsurface(constantes.PACMAN_COORDENADAS['derecha'][self.frame_index]), (int(constantes.ancho_personaje*constantes.escala_personaje), int(constantes.alto_personaje*constantes.escala_personaje))) #escalar la imagen del personaje al tamaño definido en constantes
        self.rotate = 0


    def actualizar_animacion(self):
        if self.dx == 0 and self.dy == 0: #para que mantenga la orientacion cuando no se mueve
            pass
        elif self.dx < 0:
            self.rotate = 180
        elif self.dx > 0:
            self.rotate = 0
        elif self.dy < 0:
            self.rotate = 90
        else:
            self.rotate = 270

        #(podriamos añadir un string de direccion) #direccion es un string que indica la direccion del movimiento del personaje
        cooldown_animaciones = 120 #tiempo en ms entre cada cambio de frame
        tiempo_actual = pygame.time.get_ticks()
        self.imagen = escalar_imagen(self.sprite.subsurface(constantes.PACMAN_COORDENADAS['derecha'][self.frame_index]), constantes.escala_personaje) #actualizar la imagen del personaje segun la direccion del movimiento y el frame de animacion

        if tiempo_actual - self.frame_tiempo > cooldown_animaciones: #cambiar de frame cada 100 ms
            self.frame_tiempo = tiempo_actual
            self.frame_index += 1
            if self.frame_index >= 4: #si el frame index supera el numero de frames de la animacion, volver al primer frame):
                self.frame_index = 0

    def dibujar(self, interfaz): #donde lo queremos dibujar, no hace falta que sea la misma ventana
        pygame.draw.rect(interfaz, (255, 0, 0), self.forma, 2) #hitbox del personaje
        imagen_dr = pygame.transform.rotate(self.imagen, self.rotate)
        interfaz.blit(imagen_dr, self.forma) #dibujar la imagen del personaje en la posicion y tamaño del rectangulo