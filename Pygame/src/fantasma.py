import pygame
from src import constantes
from src.fisica import EnteFisico, escalar_imagen

class Fantasma(EnteFisico):
    '''
    Entidad controlada por la Inteligencia Artificial.
    Hereda todo el motor físico de la clase EnteFísico y la expande con su correspondiente renderizado.
    Gestiona el renderizado de los fantasmas distinguiendo el estado en el que se encuentra (Perseguir, Asustado, Ojos).
    '''
    def __init__(self, x, y, imagen_entera, controlador, color):
        # Inicializamos la hitbox y las variables vectoriales de la clase padre
        super().__init__(x, y, controlador) 

        self.color = color # Para poder distinguir el fantasma
        self.sprite = imagen_entera
        self.frame_index = 0 # # Variable para controlar el frame de animación
        self.frame_tiempo = pygame.time.get_ticks() # Almacenamos el tiempo actual para controlar la velocidad de la animación

        # Para optimizar memoria y rendimiento, extraemos del sprite las coordenadas de las imagenes y las escalamos 1 sola vez al 
        # instanciar el objeto Fantasma. Lo hacemos por cada dirección (pues no son simétricos como Pacman).

        # Fantasma normal (Persecución o Dispersión)
        self.frames = {
            direccion: [
                escalar_imagen(imagen_entera.subsurface(coords), constantes.escala_personaje) for coords in lista_coords ]
            for direccion, lista_coords in constantes.FANTASMA_ROJO_COORDENADAS[self.color].items()   }
        # Fantasma asustado (azul oscuro)
        self.frames_asustado = [
            escalar_imagen(imagen_entera.subsurface(coords), constantes.escala_personaje)
            for coords in constantes.FANTASMA_ESTADOS_ESPECIALES['asustado_azul']  ]
        # Fantasma asustado (blanco)
        self.frames_asustado_blanco = [
            escalar_imagen(imagen_entera.subsurface(coords), constantes.escala_personaje)
            for coords in constantes.FANTASMA_ESTADOS_ESPECIALES['asustado_blanco']  ]
        # Ojos del fantasma (cuando es comido)
        self.frames_ojos = {
            direccion: escalar_imagen(imagen_entera.subsurface(coords), constantes.escala_personaje)
            for direccion, coords in constantes.FANTASMA_ESTADOS_ESPECIALES['ojos'].items()  }

        self.aviso_fin_asustado = False # Variable para decirle al fantasma que su tiempo de "asustado" se acaba

        self.imagen = self.frames['derecha'][0] # Inicializamos la imagen con el primer frame de animación
        

    def actualizar_animacion(self):
        '''
        Actualiza la imagen del sprite separado en 2 lógicas:
        - Primero mediante la dirección a la que va determinamos donde tienen que mirar los ojos del fantasma.
        - Después 
        - Luego realizamos un ciclo de animaciones de los fantasmas mediante el reloj interno
        '''
         # Obtenemos la orientación basada en el vector de velocidad (dx, dy)
        if self.dx > 0: direccion_visual = 'derecha'
        elif self.dx < 0: direccion_visual = 'izquierda'
        elif self.dy > 0: direccion_visual = 'abajo'
        else: direccion_visual = 'arriba'
        
            
         # Animaciones por frame
        cooldown_animaciones = constantes.cooldown_animaciones # Tiempo transcurrido entre el cambio de fotograma (120 ms)
        tiempo_actual = pygame.time.get_ticks()
        
        # Distinguimos casos en función del estado del fantasma: (perseguir, asustado o ojos) 
        estado = self.controlador.estado

        if estado == "perseguir" or estado == "dispersion":
             # Si la diferencia entre el tiempo actual y el último registro supera nuestro 'cooldown' actualizamos la animación 
            if tiempo_actual - self.frame_tiempo > cooldown_animaciones: 
                self.frame_tiempo = tiempo_actual
                self.frame_index = (self.frame_index + 1) % len(self.frames[direccion_visual])
            self.imagen = self.frames[direccion_visual][self.frame_index]

        elif estado == "asustado":
            # Asustado no depende de la dirección (los ojos no cambian de dirección)
            if tiempo_actual - self.frame_tiempo > cooldown_animaciones:
                self.frame_tiempo = tiempo_actual
                self.frame_index = (self.frame_index + 1) % len(self.frames_asustado)
                
            # Si tenemos el aviso activado y la división del tiempo es par (cambia cada 200ms)
            if self.aviso_fin_asustado and (tiempo_actual // 200) % 2 == 0:
                self.imagen = self.frames_asustado_blanco[self.frame_index]
            else:
                self.imagen = self.frames_asustado[self.frame_index]

        elif estado == "ojos":
            # Los ojos no tienen animación de fotogramas, solo cambian si giran
            self.imagen = self.frames_ojos[direccion_visual]

    def dibujar(self, interfaz, modo_debug = 0): 
        ''' 
        Se encarga del renderizado del sprite usando Bit-Blit.
        Además dibuja diferentes elementos visuales en el modo Debug para visualizar la lógica de movimiento de los fantasmas. 
        ''' 
        # Dibujamos a los fantasmas superponiendo la imagen sobre su hitbox
        interfaz.blit(self.imagen, self.forma)
        
        # DEBUG (tenemos 2 modos debug distintos)
        if not modo_debug or self.controlador.estado == "asustado":
            return # Si no hay debug, ahorramos comprobaciones

        # Tomamos el color correspondiente en el diccionario de colores
        color_linea = constantes.colores_debug.get(self.color, (255, 255, 255))

        # Modo 1: Solo mostrar valores de las cajas heurísticas y el vector que apunta al objetivo 
        if modo_debug == 1 and hasattr(self.controlador, 'objetivo_debug') and self.controlador.objetivo_debug:
            
            meta = self.controlador.objetivo_debug

            # Exclusivo de Inky: Usa la posición de Blinky para trazar un vector 
            if self.color == 'azul' and hasattr(self.controlador, 'pivote_debug') and self.controlador.blinky_debug:
                pivote = self.controlador.pivote_debug
                blinky_pos = self.controlador.blinky_debug
                if self.controlador.estado == "perseguir":
                    # Línea 1: Desde Blinky hasta el pivote (Gris claro)
                    pygame.draw.line(interfaz, (200, 200, 200), blinky_pos, pivote, 2)
                    # Línea 2: Desde el pivote hasta la meta (Gris claro)
                    pygame.draw.line(interfaz, (200, 200, 200), pivote, meta, 2)
                # Dibujar el pivote como un círculo
                pygame.draw.circle(interfaz, (150, 150, 150), pivote, 6)
                
            else: # Para el resto de fantasmas: Dibujamos un vector directamente al objetivo
                pygame.draw.line(interfaz, color_linea, self.forma.center, meta, 2)


            # Calculamos la esquina superior izquierda restando la mitad del ancho/alto (12/2 = 6)
            interfaz.fill(color_linea, (meta[0] - 6, meta[1] - 6, 12, 12))

            # Para todos dibujamos cajas con el valor de la heurística
            for pos, valor in self.controlador.opciones_debug:
                texto = self.fuente_debug.render(str(valor), True, (255, 255, 255))
                interfaz.blit(texto, (pos[0] + 10, pos[1] + 15))
                pygame.draw.rect(interfaz, (255, 255, 255), (pos[0], pos[1], constantes.tamano_celda, constantes.tamano_celda), 1)

        # Modo 2: Mostramos una simulación predictiva de la ruta que van a seguir (4 pasos delante)
        elif modo_debug == 2 and hasattr(self.controlador, 'ruta_debug') and self.controlador.ruta_debug:
            ruta = self.controlador.ruta_debug

            for i, pos in enumerate(ruta):
                radio = 7 - (i * 2) 
                pygame.draw.circle(interfaz, color_linea, pos, radio)
                
                if i > 0:
                    pygame.draw.line(interfaz, color_linea, ruta[i-1], pos, 2)
                else:
                    pygame.draw.line(interfaz, color_linea, self.forma.center, pos, 2)