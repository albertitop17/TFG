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
            # Dibujamos la circunferencia del miedo de Clyde centrada en Pac-Man 
            pygame.draw.circle(interfaz, (255, 184, 82), self.forma.center, radio_miedo, 1)

        if modo_debug == 3 and hasattr(self.controlador, 'mapa_peligro_debug'): 
            # Si tiene los atributos de debug (es decir, está siendo controlado por la IA)
            tam = constantes.tamano_celda
            offset = constantes.offset_y_mapa
            mitad = tam//2

            # Diccionario de colores {50000: Rojo, 20000: Naranja oscuro, 10000: Naranja claro, 5000: Amarillo, 2000: Amarillo claro}
            # Aura de peligro: común a ambas IAs 
            colores_aura = {50000: (255, 0, 0), 20000: (255, 100, 0), 10000: (255, 150, 0), 5000: (255, 200, 0), 2000: (255, 230, 100)}

            # Dibujamos el aura de peligro (cuadrados de colores)
            for (x, y), penalizacion in self.controlador.mapa_peligro_debug.items():
                color = colores_aura.get(penalizacion, (200, 200, 200))  # gris para valores intermedios (detrás del fantasma)
                pygame.draw.rect(interfaz, color, (x * tam, (y * tam) + constantes.offset_y_mapa, tam, tam), 2)

            # Dibujamos la bolita objetivo (Marcada en verde brillante)

            # Debug Clase IAs
            if not hasattr(self.controlador, 'modo_elegido_debug'):
                meta = self.controlador.meta_bolita_debug
                if meta:
                    pygame.draw.circle(interfaz, (0, 255, 0), meta.center, 8, 2)

                # Dibujamos la ruta completa de A*
                camino = self.controlador.camino_debug
                if camino and len(camino) > 1:
                    y_tunel  = constantes.tunel
                    ancho_px = constantes.ancho_ventana
                    puntos   = [(nx * tam + mitad, ny * tam + offset + mitad) for nx, ny in camino]

                    for i in range(1, len(puntos)):
                        n1, n2 = camino[i - 1], camino[i]
                        p1, p2 = puntos[i - 1], puntos[i]
                        # Detectamos el salto de túnel: misma fila y columnas en extremos opuestos
                        if n1[1] == y_tunel and n2[1] == y_tunel and abs(n1[0] - n2[0]) > 1:
                            if n2[0] < n1[0]:   # Sale por la derecha, entra por la izquierda
                                pygame.draw.line(interfaz, (0, 255, 0), p1, (ancho_px, p1[1]), 3)
                                pygame.draw.line(interfaz, (0, 255, 0), (0, p2[1]), p2, 3)
                            else:               # Sale por la izquierda, entra por la derecha
                                pygame.draw.line(interfaz, (0, 255, 0), p1, (0, p1[1]), 3)
                                pygame.draw.line(interfaz, (0, 255, 0), (ancho_px, p2[1]), p2, 3)
                        else:
                            pygame.draw.line(interfaz, (0, 255, 0), p1, p2, 3)




            # Debug Clase IA_Ptos
            else:
                # Gradiente de utilidad sobre las bolitas candidatas (rojo = peor, verde = mejor)
                for bolita, t in self.controlador.utilidad_debug:
                    r     = int(255 * (1 - t))
                    g     = int(255 * t)
                    radio = 3 + int(4 * t)  # Las mejores opciones se dibujan más grandes
                    pygame.draw.circle(interfaz, (r, g, 0), bolita.center, radio)

                # Radios de decisión alrededor de Pac-Man
                # Verde claro: radio de búsqueda de bolita_optima
                # Azul claro: radio de activación de super-bolita
                # Rojo: radio de caza
                pygame.draw.circle(interfaz, (100, 255, 100), self.forma.center, constantes.radio_bolita_optima, 1)
                pygame.draw.circle(interfaz, (100, 200, 255), self.forma.center, constantes.radio_super, 1)
                pygame.draw.circle(interfaz, (250, 0, 0), self.forma.center, constantes.radio_caza, 1)
                # Objetivo actual marcado en verde
                meta = self.controlador.meta_bolita_debug
                if meta:
                    pygame.draw.circle(interfaz, (0, 255, 0), meta.center, 8, 2)

                # Camino A* con soporte para el salto de túnel
                camino = self.controlador.camino_debug
                if camino and len(camino) > 1:
                    y_tunel  = constantes.tunel
                    ancho_px = constantes.ancho_ventana
                    puntos   = [(nx * tam + mitad, ny * tam + offset + mitad) for nx, ny in camino]

                    for i in range(1, len(puntos)):
                        n1, n2 = camino[i - 1], camino[i]
                        p1, p2 = puntos[i - 1], puntos[i]
                        # Detectamos el salto de túnel: misma fila y columnas en extremos opuestos
                        if n1[1] == y_tunel and n2[1] == y_tunel and abs(n1[0] - n2[0]) > 1:
                            if n2[0] < n1[0]:   # Sale por la derecha, entra por la izquierda
                                pygame.draw.line(interfaz, (0, 255, 0), p1, (ancho_px, p1[1]), 3)
                                pygame.draw.line(interfaz, (0, 255, 0), (0, p2[1]), p2, 3)
                            else:               # Sale por la izquierda, entra por la derecha
                                pygame.draw.line(interfaz, (0, 255, 0), p1, (0, p1[1]), 3)
                                pygame.draw.line(interfaz, (0, 255, 0), (ancho_px, p2[1]), p2, 3)
                        else:
                            pygame.draw.line(interfaz, (0, 255, 0), p1, p2, 3)

                # Etiqueta del modo activo con fondo semitransparente
                modo = self.controlador.modo_elegido_debug
                if modo:
                    colores_modo = {"Caza": (255, 80, 80), "Sb":(255, 200, 50), "Bolitas": (80, 220, 120)}
                    color  = colores_modo.get(modo, (200, 200, 200))
                    texto  = self.fuente_debug.render(modo, True, color)
                    fondo  = pygame.Surface((texto.get_width() + 10, texto.get_height() + 6), pygame.SRCALPHA)
                    fondo.fill((0, 0, 0, 160))
                    interfaz.blit(fondo,  (8, 28))
                    interfaz.blit(texto,  (13, 30))




        # Renderizado del sprite con la rotado a la dirección de movimiento
        imagen_dr = pygame.transform.rotate(self.imagen, self.rotate) # se podría usar distintas sub-superficies del sprite (como en los fantasmas)
        
        # Dibujamos a Pacman superponiendo la imagen sobre su hitbox
        interfaz.blit(imagen_dr, self.forma) 