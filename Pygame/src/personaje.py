
import pygame
from src import constantes

def escalar_imagen(imagen, escala):
    ancho = int(imagen.get_width() * escala)
    alto = int(imagen.get_height() * escala)
    return pygame.transform.scale(imagen, (ancho, alto))
class Personaje:
    def __init__(self, x, y, imagen_entera, controlador): #poner en imagen predeterminada las coordenadas del sprite del personaje en la hoja de sprites?
        self.forma = pygame.Rect(x, y, constantes.ancho_personaje, constantes.alto_personaje)
        self.forma.width = constantes.tamano_celda #ajustamos el tamaño del rectángulo del personaje al tamaño de la celda para facilitar las colisiones y el movimiento 
        self.forma.height = constantes.tamano_celda
        self.sprite = imagen_entera
        self.frame_index = 0 #para controlar el frame de animacion
        self.frame_tiempo = pygame.time.get_ticks() #almacenamos el tiempo actual para controlar la velocidad de la animacion
        self.imagen = pygame.transform.scale(imagen_entera.subsurface(constantes.PACMAN_COORDENADAS['derecha'][self.frame_index]), (int(constantes.ancho_personaje*constantes.escala_personaje), int(constantes.alto_personaje*constantes.escala_personaje))) #escalar la imagen del personaje al tamaño definido en constantes
        self.rotate = 0
        #cuestiones 1 marzo
        self.controlador = controlador
        self.dx = 0
        self.dy = 0
    

    def actualizar(self, dimensiones, muros):
        # 1. El cerebro decide el movimiento
        dx_deseada, dy_deseada = self.controlador.obtener_movimiento(self.forma, muros) #le pasamos la forma del personaje y los muros para que el controlador pueda tomar decisiones informadas sobre el movimiento (por ejemplo, para la IA)
        # 2. Comprobamos si el movimiento deseado es posible 
        self.gestionar_movimiento(dx_deseada, dy_deseada, dimensiones, muros)
        # 3. Movemos al personaje según el movimiento permitido
        self.movimiento(dimensiones, muros)
        # 4. Actualizamos la animación del personaje según su movimiento
        self.actualizar_animacion()

    def gestionar_movimiento(self, deseado_x, deseado_y, dimensiones, muros):
        # Si no hay input, no hacemos nada (al principio?)
        if deseado_x == 0 and deseado_y == 0:
            return
        # Si la intención es igual a lo que ya estamos haciendo, no calculamos nada
        if deseado_x == self.dx and deseado_y == self.dy:
            return
        # GIRO 180 GRADOS: al instante 
        if deseado_x == -self.dx and deseado_y == -self.dy and (self.dx != 0 or self.dy != 0):
            self.dx = deseado_x
            self.dy = deseado_y
            return

        # GIRO 90 GRADOS: Solo si puedo hacer el giro sin colisionar con un muro (sino lo guardaré hasta que pueda hacerlo)
        # Simulamos un paso en la dirección deseada creando un rectángulo fantasma
        # ALINEACIÓN MAGNÉTICA ("Snap to Grid" o "Cornering")
        # Guardamos la posición original por si el giro falla
        pos_x_original = self.forma.x
        pos_y_original = self.forma.y

        # Definimos el margen de error igual a la velocidad (para que nunca se salte un hueco)
        margen = constantes.velocidad 

        # Si queremos ir Arriba/Abajo, ajustamos nuestra posición X al centro del pasillo
        if deseado_y != 0 and self.dx != 0:
            resto_x = self.forma.x % constantes.tamano_celda
            if resto_x <= margen:
                self.forma.x -= resto_x # Nos empuja un poquito a la izquierda para alinear
            elif resto_x >= constantes.tamano_celda - margen:
                self.forma.x += (constantes.tamano_celda - resto_x) # Nos empuja a la derecha

        # Si queremos ir Izquierda/Derecha, ajustamos nuestra posición Y al centro del pasillo
        elif deseado_x != 0 and self.dy != 0:
            resto_y = self.forma.y % constantes.tamano_celda
            if resto_y <= margen:
                self.forma.y -= resto_y # Nos empuja arriba
            elif resto_y >= constantes.tamano_celda - margen:
                self.forma.y += (constantes.tamano_celda - resto_y) # Nos empuja abajo

        # Ahora que (quizás) estamos perfectamente alineados, probamos el rectángulo
        rect_prueba = self.forma.copy()
        rect_prueba.x += deseado_x
        rect_prueba.y += deseado_y

        colisiona = False
        for muro in muros:
            if rect_prueba.colliderect(muro):
                colisiona = True
                break
            
        if not colisiona: #Confirmamos el giro
            self.dx = deseado_x
            self.dy = deseado_y
        else:# Si a pesar de alinearnos sigue habiendo muro, deshacemos el empujón magnético
            self.forma.x = pos_x_original
            self.forma.y = pos_y_original

        #print(f"Intención: ({deseado_x}, {deseado_y}), Movimiento actual: ({self.dx}, {self.dy}), Colisiona: {colisiona}")

    def movimiento(self, dimensiones, muros): #dx y dy son la velocidad de movimiento en x e y respectivamente, x e y son el ancho y alto de la ventana para controlar los limites
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
        #tratamos los ejes por separado para que el personaje pueda deslizarse por las paredes en lugar de quedarse atascado
        #movimiento con colisiones en el eje x
        self.forma.x += self.dx
        for muro in muros:
            if self.forma.colliderect(muro): # Si choco con un muro
                if self.dx > 0: # Si iba a la derecha, me pego a su lado izquierdo
                    self.forma.right = muro.left
                elif self.dx < 0: # Si iba a la izquierda, me pego a su lado derecho
                    self.forma.left = muro.right
                self.dx = 0 # Si choco con un muro, la velocidad se anula
        #movimiento con colisiones en el eje y
        self.forma.y += self.dy
        for muro in muros:
            if self.forma.colliderect(muro):
                if self.dy > 0: # Si iba hacia abajo, me pego a su techo
                    self.forma.bottom = muro.top
                elif self.dy < 0: # Si iba hacia arriba, me pego a su suelo
                    self.forma.top = muro.bottom
                self.dy = 0 # Si choco con un muro, la velocidad se anula

        # Asegurarse de que el personaje al salirse de los límites de la ventana entre por el lado opuesto
        if self.forma.left < 0: #si el personaje se sale por la izquierda
            self.forma.right = dimensiones[0] 
        if self.forma.right > dimensiones[0]: #si el personaje se sale por la derecha
            self.forma.left = 0
        if self.forma.top < 0: #si el personaje se sale por arriba
            self.forma.bottom = dimensiones[1]
        if self.forma.bottom > dimensiones[1]: #si el personaje se sale por abajo
            self.forma.top = 0

    def actualizar_animacion(self): #(podriamos añadir un string de direccion) #direccion es un string que indica la direccion del movimiento del personaje
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


    

        

