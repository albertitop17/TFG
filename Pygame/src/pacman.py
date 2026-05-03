import pygame
from src import constantes
from src.fisica import EnteFisico, escalar_imagen

class Pacman(EnteFisico):
    '''
    Ente controlado por el jugador o por la IA.
    Hereda todo el motor físico de la clase EnteFísico y la expande con su correspondiente renderizado.
    Mediante su correspondiente sub-sprite realiza las animaciones a tiempo real. 
    '''
    def __init__(self, x, y, imagen_entera, controlador):
        # Inicializamos la hitbox y las variables vectoriales de la clase padre
        super().__init__(x, y, controlador) 
        
        self.sprite = imagen_entera 
        self.frame_index = 0 # Variable para controlar el frame de animación
        self.frame_tiempo = pygame.time.get_ticks() # Almacenamos el tiempo actual para controlar la velocidad de la animación
        self.rotate = 0 # Ángulo de rotación de la animación (en grados)

        # Para optimizar memoria y rendimiento, extraemos del sprite las coordenadas de la imagen y las escalamos 1 sola vez al 
        # instanciar el objeto Pacman.
        self.frames = [escalar_imagen(imagen_entera.subsurface(coordenadas), constantes.escala_personaje) 
                       for coordenadas in constantes.PACMAN_COORDENADAS['derecha']] 
        self.imagen = self.frames[0] # Inicializamos la imagen con el primer frame de animación

    def actualizar_animacion(self):
        '''
        Actualiza la imagen del sprite separado en 2 lógicas:
        - Primero mediante rotaciones giramos el personaje en función de su dirección
        - Luego realizamos un ciclo de animaciones de la boca de Pacman mediante el reloj interno
        '''
        # Calculamos la orientación (podríamos usar los ditintos sprites en vez de girar este)
        if self.dx == 0 and self.dy == 0: #
            pass # Si está frente a un muro quieto, mantiene su orientación 
        elif self.dx < 0:
            self.rotate = 180 # Izquierda
        elif self.dx > 0:
            self.rotate = 0 # Derecha
        elif self.dy < 0:
            self.rotate = 90 # Arriba (En las coordenadas de Pygame, la Y decrece al subir)
        else:
            self.rotate = 270 # Abajo

        # Animaciones por frame
        cooldown_animaciones = constantes.cooldown_animaciones # Tiempo transcurrido entre el cambio de fotograma (120 ms)
        tiempo_actual = pygame.time.get_ticks()
        
        # Si la diferencia entre el tiempo actual y el último registro supera nuestro 'cooldown' actualizamos la animación 
        if tiempo_actual - self.frame_tiempo > cooldown_animaciones: 
            self.frame_tiempo = tiempo_actual
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        # Actualizamos la imagen actual desde el banco de imagenes precargado 
        self.imagen = self.frames[self.frame_index]

    def dibujar(self, interfaz, modo_debug = 0): #donde lo queremos dibujar, no hace falta que sea la misma ventana
        '''
        Se encarga del renderizado aplicando las transformaciones geométricas y ejecutando el Bit-Blit hacia la pantalla principal
        '''
        # Añadimos erramientas visuales para el modo DEBUG (para poder ver visualmente los objetivos de los fantasmas)
        if modo_debug == 1:
            radio_miedo = 8 * constantes.tamano_celda
            color_naranja = (255, 184, 82)
            # Dibujamos la circunferencia del miedo de Clyde centrada en Pac-Man 
            pygame.draw.circle(interfaz, color_naranja, self.forma.center, radio_miedo, 1)

        imagen_dr = pygame.transform.rotate(self.imagen, self.rotate) # se podría usar distintas sub-superficies del sprite (como en los fantasmas)
        
        # Dibujamos a Pacman superponiendo la imagen sobre su hitbox
        interfaz.blit(imagen_dr, self.forma) 