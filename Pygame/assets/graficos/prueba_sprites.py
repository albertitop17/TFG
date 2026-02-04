import pygame
# --- CONFIGURACIÓN ---
NOMBRE_IMAGEN = "Pygame//assets//graficos//sheet_pacman_personajes.png"
ANCHO_SPRITE = 16   # Tamaño estándar de Pacman (suelen ser 16x16)
ALTO_SPRITE = 16
ESCALA = 3          # Zoom para verlo mejor en pantalla (3x)
# ---------------------

pygame.init()

# Cargar imagen y configurar transparencia
hoja = pygame.image.load(NOMBRE_IMAGEN)
#color_fondo = hoja.get_at((0, 0))
#hoja.set_colorkey(color_fondo)

# Crear pantalla
ancho_hoja = hoja.get_width()
alto_hoja = hoja.get_height()
pantalla = pygame.display.set_mode((ancho_hoja * ESCALA, alto_hoja * ESCALA))
pygame.display.set_caption("Buscador de Coordenadas - Usa las flechas y WASD")

# Variables para mover el selector
x_sel = 0
y_sel = 0
ancho_sel = ANCHO_SPRITE
alto_sel = ALTO_SPRITE

reloj = pygame.time.Clock()
corriendo = True

while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
        
        # Controles: Flechas mueven posición, WASD cambia tamaño
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RIGHT: x_sel += 1
            if evento.key == pygame.K_LEFT:  x_sel -= 1
            if evento.key == pygame.K_DOWN:  y_sel += 1
            if evento.key == pygame.K_UP:    y_sel -= 1
            
            # Imprimir coordenadas en la consola cada vez que te mueves
            print(f"Coordenadas actuales: x={x_sel}, y={y_sel}, w={ancho_sel}, h={alto_sel}")

    # Dibujar
    pantalla.fill((50, 50, 50)) # Fondo gris oscuro
    
    # Escalar la hoja para verla grande
    hoja_grande = pygame.transform.scale(hoja, (ancho_hoja * ESCALA, alto_hoja * ESCALA))
    pantalla.blit(hoja_grande, (0, 0))

    # Dibujar el recuadro selector (ajustado a la escala)
    rect_selector = pygame.Rect(x_sel * ESCALA, y_sel * ESCALA, ancho_sel * ESCALA, alto_sel * ESCALA)
    pygame.draw.rect(pantalla, (255, 0, 0), rect_selector, 2) # Borde rojo

    pygame.display.flip()
    reloj.tick(30)

pygame.quit()