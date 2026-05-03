import pygame
from src import constantes

def camino_esta_libre(rect_actual, dx, dy, muros):
    '''
    Se encarga de detectar colisiones simulando un paso en la dirección actual
    Devolverá True si el camino está libre y False si colisiona con algún muro
    '''
    rect_prueba = rect_actual.copy()
    rect_prueba.x += dx
    rect_prueba.y += dy

    for muro in muros:
        if rect_prueba.colliderect(muro):
            return False 
    return True

class EnteFisico:
    '''
    Clase padre de Pac-Man y los fantasmas (comparten la misma física). 
    Gestiona la cinemática, colisiones y teletransporte.
    '''
    def __init__(self, x, y, controlador): 
        # Inicializamos la hitbox con las coordenadas pasadas (x,y)
        self.forma = pygame.Rect(x, y, constantes.ancho_personaje, constantes.alto_personaje) 

        # Los movimientos realizados estarán dictados según el controlador que tenga asignado
        self.controlador = controlador
        self.dx = 0
        self.dy = 0

    def actualizar(self, dimensiones, muros, objetivo=None, lista_fantasmas=None,**kwargs):
        '''
        Pipeline principal de actualización ejecutado en cada fotograma.
        Sigue un orden de ejecución determinado
        '''
        # 1º. El cerebro (Controlador) obtiene una petición de movimiento
        dx_deseada, dy_deseada = self.controlador.obtener_movimiento(rect_actual = self.forma, muros = muros, objetivo = objetivo, 
                                                                     lista_fantasmas = lista_fantasmas, **kwargs)
        # 2º. Comprobamos si el movimiento deseado es posible 
        self.gestionar_movimiento(dx_deseada, dy_deseada, muros)
        # 3º. Movemos al personaje según el movimiento permitido (gestionando la dinámica de túneles)
        self.movimiento(dimensiones, muros)
        # 4º. Actualizamos la animación del personaje según su movimiento
        self.actualizar_animacion()

    def gestionar_movimiento(self, deseado_x, deseado_y, muros):
        '''
        Realizamos comprobaciones en la solicitud de moviento. 
        Se comprueba que estemos alineados con la casilla y que no es un muro (usando 'camino_esta_libre')
        '''
        # Si no hay input o se sigue en el mismo sentido en el que ya ibamos, no hacemos nada
        if (deseado_x == 0 and deseado_y == 0) or (deseado_x == self.dx and deseado_y == self.dy):
            return
        
        # Giro 180º: Podemos girar en cualquier momento (no hace falta estar alineados con la celda)
        if deseado_x == -self.dx and deseado_y == -self.dy and (self.dx != 0 or self.dy != 0):
            self.dx = deseado_x
            self.dy = deseado_y
            return

        # GIRO DE 90º/270º: Solo se permite si se está alineado con la celda
        esta_alineado_x = (self.forma.x % constantes.tamano_celda == 0)
        esta_alineado_y = (self.forma.y % constantes.tamano_celda == 0)

        if esta_alineado_x and esta_alineado_y:
            # Si estamos en un cruce perfecto, comprobamos si hay muro en la nueva dirección
            if camino_esta_libre(self.forma, deseado_x, deseado_y, muros):
                self.dx = deseado_x
                self.dy = deseado_y
        
    def movimiento(self, dimensiones, muros):
        '''
        Realiza la acción del desplazamiento.
        Tratamos los ejes de manera independiente para que el personaje pueda 'resbalar' por los muros sin quedarse
        atascado en mitad de un túnel (no se permite quedase quietos en mitad de un túnel) 
        '''
        # Eje X 
        if self.dx != 0: # Solo calcularemos si hay movimiento en esa dirección
            self.forma.x += self.dx
            indice_muro = self.forma.collidelist(muros) # Búsqueda en C (mejor que un bucle para comprobarlos)
            
            if indice_muro != -1: # Si hay colisión
                muro_chocado = muros[indice_muro]
                # nos pegamos a las paredes para garantizar el buen funcionamiento
                if self.dx > 0:
                    self.forma.right = muro_chocado.left
                elif self.dx < 0:
                    self.forma.left = muro_chocado.right
                self.dx = 0 

        # Eje Y 
        if self.dy != 0:
            self.forma.y += self.dy
            indice_muro = self.forma.collidelist(muros)
            
            if indice_muro != -1:
                muro_chocado = muros[indice_muro]
                if self.dy > 0:
                    self.forma.bottom = muro_chocado.top
                elif self.dy < 0:
                    self.forma.top = muro_chocado.bottom
                self.dy = 0 

        # Implementamos la mecánica de teletransporte en los túneles
        if self.forma.left < 0: #si el personaje se sale por la izquierda
            self.forma.right = dimensiones[0] 
        elif self.forma.right > dimensiones[0]: #si el personaje se sale por la derecha
            self.forma.left = 0
        
        # elif self.forma.top < 0: #si el personaje se sale por arriba
        #     self.forma.bottom = dimensiones[1]
        # elif self.forma.bottom > dimensiones[1]: #si el personaje se sale por abajo
        #     self.forma.top = 0

    # Funciones vacías que serán sobrescritas las clases hijas (Pacman y Fantasma)
    def actualizar_animacion(self): pass
    def dibujar(self, interfaz): pass