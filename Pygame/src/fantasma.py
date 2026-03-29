import pygame
from src import constantes
from src.fisica import EnteFisico

# Función auxiliar para escalar imágenes
def escalar_imagen(imagen, escala):
    ancho = int(imagen.get_width() * escala)
    alto = int(imagen.get_height() * escala)
    return pygame.transform.scale(imagen, (ancho, alto))

class Fantasma(EnteFisico):
    def __init__(self, x, y, imagen_entera, controlador, color):
        super().__init__(x, y, controlador) #llamamos a la fisica del padre

        self.color = color
        self.sprite = imagen_entera
        self.frame_index = 0 #para controlar el frame de animacion
        self.frame_tiempo = pygame.time.get_ticks() #almacenamos el tiempo actual para controlar la velocidad de la animacion


        # Pre-escalamos todos los frames de todas las direcciones una sola vez
        self.frames = {
            direccion: [
                escalar_imagen(imagen_entera.subsurface(coords), constantes.escala_personaje)
                for coords in lista_coords
            ]
            for direccion, lista_coords in constantes.FANTASMA_ROJO_COORDENADAS[self.color].items()
        }
        self.imagen = self.frames['derecha'][0]

    def actualizar_animacion(self):
        # 1. DETERMINAR LA DIRECCIÓN VISUAL
        # Por defecto, si está quieto, miramos a dónde iba antes.
        # Creamos una variable 'direccion_visual' para usar como clave del diccionario.
        if self.dx > 0:
            direccion_visual = 'derecha'
        elif self.dx < 0:
            direccion_visual = 'izquierda'
        elif self.dy > 0:
            direccion_visual = 'abajo'
        elif self.dy < 0:
            direccion_visual = 'arriba'
        else:
            # Si dx y dy son 0 (chocado), mantenemos la animación actual.
            # No actualizamos la imagen y salimos.
            return
        
        cooldown_animaciones = 120 #tiempo en ms entre cada cambio de frame
        tiempo_actual = pygame.time.get_ticks()
        
        if tiempo_actual - self.frame_tiempo > cooldown_animaciones: #cambiar de frame cada 200 ms
            self.frame_tiempo = tiempo_actual
            self.frame_index = (self.frame_index + 1) % len(self.frames[direccion_visual])
    
        # Sin escalar en cada frame: usamos el frame ya pre-escalado
        self.imagen = self.frames[direccion_visual][self.frame_index]

    def dibujar(self, interfaz, debug = False): #donde lo queremos dibujar, no hace falta que sea la misma ventana
        interfaz.blit(self.imagen, self.forma) #dibujar la imagen del personaje en la posicion y tamaño del rectangulo
        if debug and hasattr(self.controlador, 'objetivo_debug') and self.controlador.objetivo_debug:
        # Si el controlador tiene la variable objetivo_debug y no está vacía...

            # Dibujamos el "Vector de Puntería" (Línea desde el fantasma hasta Pac-Man)
            # Usamos el color de este fantasma para la línea (ej. Rojo)
            color_linea = (255, 0, 0) if self.color == 'rojo' else (255, 184, 255)
            
            pygame.draw.line(
                interfaz, 
                color_linea, 
                self.forma.center, # Desde el centro del fantasma
                self.controlador.objetivo_debug, # Hasta el centro de Pac-Man
                2 # Grosor de la línea
            )

            # 3. (Opcional) Dibujar un punto que indique hacia dónde está intentando empujar la IA
            # Proyectamos un punto en la dirección en la que se mueve
            punto_futuro_x = self.forma.centerx + (self.dx * 10)
            punto_futuro_y = self.forma.centery + (self.dy * 10)
            pygame.draw.circle(interfaz, (0, 255, 0), (punto_futuro_x, punto_futuro_y), 5)