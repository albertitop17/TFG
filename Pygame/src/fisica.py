import pygame
from src import constantes

def camino_esta_libre(rect_actual, dx, dy, muros):
    """
    Simula un paso en la dirección dx, dy y devuelve True si el camino está libre,
    o False si colisiona con algún muro.
    """
    rect_prueba = rect_actual.copy()
    rect_prueba.x += dx
    rect_prueba.y += dy

    for muro in muros:
        if rect_prueba.colliderect(muro):
            return False # Chocó, el camino no está libre
            
    return True


class EnteFisico:
    def __init__(self, x, y, controlador): #poner en imagen predeterminada las coordenadas del sprite del personaje en la hoja de sprites?
        self.forma = pygame.Rect(x, y, constantes.ancho_personaje, constantes.alto_personaje)
        self.forma.width = constantes.tamano_celda #ajustamos el tamaño del rectángulo del personaje al tamaño de la celda para facilitar las colisiones y el movimiento 
        self.forma.height = constantes.tamano_celda

        self.controlador = controlador
        self.dx = 0
        self.dy = 0

    def actualizar(self, dimensiones, muros, objetivo=None, lista_fantasmas=None,**kwargs):
        # 1. El cerebro decide el movimiento
        #le pasamos la forma del personaje y los muros para que el controlador pueda tomar decisiones informadas sobre el movimiento (por ejemplo, para la IA)
        dx_deseada, dy_deseada = self.controlador.obtener_movimiento(self.forma, muros, objetivo = objetivo, lista_fantasmas = lista_fantasmas, **kwargs)
        # 2. Comprobamos si el movimiento deseado es posible 
        self.gestionar_movimiento(dx_deseada, dy_deseada, muros)
        # 3. Movemos al personaje según el movimiento permitido
        self.movimiento(dimensiones, muros)
        # 4. Actualizamos la animación del personaje según su movimiento
        self.actualizar_animacion()


    def gestionar_movimiento(self, deseado_x, deseado_y, muros):
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

        '''
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
        if camino_esta_libre(self.forma, deseado_x, deseado_y, muros): #Confirmamos el giro
            self.dx = deseado_x
            self.dy = deseado_y
        else:
            # Si a pesar de alinearnos sigue habiendo muro, deshacemos el empujón magnético
            self.forma.x = pos_x_original
            self.forma.y = pos_y_original

        #print(f"Intención: ({deseado_x}, {deseado_y}), Movimiento actual: ({self.dx}, {self.dy}), Colisiona: {colisiona}")
        '''
        # GIRO DE 90/270 GRADOS: Solo se permite si el ente está alineado con la cuadrícula
        esta_alineado_x = (self.forma.x % constantes.tamano_celda == 0)
        esta_alineado_y = (self.forma.y % constantes.tamano_celda == 0)

        if esta_alineado_x and esta_alineado_y:
            # Si estamos en un cruce perfecto, comprobamos si hay muro en la nueva dirección
            if camino_esta_libre(self.forma, deseado_x, deseado_y, muros):
                self.dx = deseado_x
                self.dy = deseado_y
        
    def movimiento(self, dimensiones, muros):
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

    # Funciones vacías que sobrescribirán los hijos (Pacman y Fantasma)
    def actualizar_animacion(self): pass
    def dibujar(self, interfaz): pass