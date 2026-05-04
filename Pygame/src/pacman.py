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

        if modo_debug == 3: 
            # Si tiene los atributos de debug (es decir, está siendo controlado por la IA)
            if hasattr(self.controlador, 'mapa_peligro_debug'):

                tam = constantes.tamano_celda
                # Diccionario de colores {5000: Rojo, 2000: Naranja oscuro, 1000: Naranja claro, 500: amarillo}
                colores_aura = {5000: (255, 0, 0), 2000: (255, 100, 0), 1000: (255, 150, 0), 500: (255, 200, 0)}

                # Dibujamos el aura de peligro (cuadrados de colores)
                for (x, y), penalizacion in self.controlador.mapa_peligro_debug.items():
                    # Obtenemos el color directamente (si no existe, blanco por defecto)
                    color = colores_aura.get(penalizacion, (255, 255, 255))
                    pygame.draw.rect(interfaz, color, (x * tam, (y * tam) + constantes.offset_y_mapa, tam, tam), 2)

                # Dibujamos la bolita objetivo (Marcada en verde brillante)
                meta = self.controlador.meta_bolita_debug
                if meta:
                    pygame.draw.circle(interfaz, (0, 255, 0), meta.center, 8, 2)

                # Dibujamos la ruta completa
                camino = self.controlador.camino_debug
                if modo_debug == 3 and camino and len(camino) > 1:
                    mitad = tam // 2
                    offset_total = constantes.offset_y_mapa + mitad
                    # Convertimos las casillas de la matriz a las coordenadas (centro) en píxeles
                    puntos_pixeles = [(nx * tam + mitad, ny * tam + offset_total) for nx, ny in camino]
                    pygame.draw.lines(interfaz, (0, 255, 0), False, puntos_pixeles, 3)

        imagen_dr = pygame.transform.rotate(self.imagen, self.rotate) # se podría usar distintas sub-superficies del sprite (como en los fantasmas)
        
        # Dibujamos a Pacman superponiendo la imagen sobre su hitbox
        interfaz.blit(imagen_dr, self.forma) 