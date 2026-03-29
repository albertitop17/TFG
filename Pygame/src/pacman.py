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
        self.rotate = 0

        self.frames = [escalar_imagen(imagen_entera.subsurface(coordenadas), constantes.escala_personaje) 
                       for coordenadas in constantes.PACMAN_COORDENADAS['derecha']] #preprocesamos los frames de animacion para no tener que recortarlos y escalarlos cada vez que actualizamos la animacion
        self.imagen = self.frames[0] #inicializamos la imagen del personaje con el primer frame de animacion


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
        
        if tiempo_actual - self.frame_tiempo > cooldown_animaciones: #cambiar de frame cada 100 ms
            self.frame_tiempo = tiempo_actual
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        # Sin escalar en cada frame: usamos el frame ya pre-escalado
        self.imagen = self.frames[self.frame_index]

    def dibujar(self, interfaz, debug = False): #donde lo queremos dibujar, no hace falta que sea la misma ventana
        if debug:
            pygame.draw.rect(interfaz, (255, 0, 0), self.forma, 2) #hitbox del personaje
        imagen_dr = pygame.transform.rotate(self.imagen, self.rotate)
        interfaz.blit(imagen_dr, self.forma) #dibujar la imagen del personaje en la posicion y tamaño del rectangulo