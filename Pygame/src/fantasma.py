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

    def dibujar(self, interfaz, modo_debug = 0): 
        interfaz.blit(self.imagen, self.forma)
        
        # MODO 1: Solo mostrar valores y la línea roja/rosa
        if modo_debug == 1 and hasattr(self.controlador, 'objetivo_debug') and self.controlador.objetivo_debug:
            
            # exclusivo de inky 
            if self.color == 'azul' and hasattr(self.controlador, 'pivote_debug') and self.controlador.pivote_debug and self.controlador.blinky_debug:
                pivote = self.controlador.pivote_debug
                meta = self.controlador.objetivo_debug
                blinky_pos = self.controlador.blinky_debug

                # Línea 1: Desde Blinky hasta el pivote (Gris claro)
                pygame.draw.line(interfaz, (200, 200, 200), blinky_pos, pivote, 2)
                # Línea 2: Desde el pivote hasta la meta (Gris claro)
                pygame.draw.line(interfaz, (200, 200, 200), pivote, meta, 2)

                # Dibujar el pivote como un círculo
                pygame.draw.circle(interfaz, (150, 150, 150), pivote, 6)
                
                # Dibujar la meta como un cuadradito cyan 
                rect_meta = pygame.Rect(0, 0, 12, 12)
                rect_meta.center = meta
                pygame.draw.rect(interfaz, (0, 255, 255), rect_meta)

            # resto de fantasmas
            else:
                if self.color == 'rojo': color_linea = (255, 0, 0)
                elif self.color == 'rosa': color_linea = (255, 184, 255)
                else: color_linea = (255, 184, 82)

                #pygame.draw.line(interfaz, color_linea, self.forma.center, self.controlador.objetivo_debug, 2)

                rect_meta = pygame.Rect(0, 0, 12, 12)
                rect_meta.center = self.controlador.objetivo_debug
                pygame.draw.rect(interfaz, color_linea, rect_meta)
                

            # --- NÚMEROS Y CAJAS (Para todos) ---
            fuente = pygame.font.SysFont("Arial", 18, bold=True)
            for pos, valor in self.controlador.opciones_debug:
                texto = fuente.render(str(valor), True, (255, 255, 255))
                interfaz.blit(texto, (pos[0] + 10, pos[1] + 15))
                # Dibujamos la cajita blanca
                rect_eval = pygame.Rect(pos[0], pos[1], constantes.tamano_celda, constantes.tamano_celda)
                pygame.draw.rect(interfaz, (255, 255, 255), rect_eval, 1)

        # MODO 2: Solo mostrar la predicción de la ruta (Línea verde)
        elif modo_debug == 2 and hasattr(self.controlador, 'ruta_debug') and self.controlador.ruta_debug:
            for i, pos in enumerate(self.controlador.ruta_debug):
                radio = 10 - (i * 2) 
                if self.color == 'rojo': color = (255, 0, 0)
                elif self.color == 'rosa': color = (255, 184, 255)
                elif self.color == 'azul': color = (0, 255, 255)
                else: color = (255, 184, 82)
                pygame.draw.circle(interfaz, color, pos, radio)
                
                if i > 0:
                    pygame.draw.line(interfaz, color, self.controlador.ruta_debug[i-1], pos, 2)
                else:
                    pygame.draw.line(interfaz, color, self.forma.center, pos, 2)