import pygame
from pygame import gfxdraw

screenSize = 600
pygame.init()
real_screen = pygame.display.set_mode((screenSize, screenSize))
clock = pygame.time.Clock()
running = True
screen = pygame.surface.Surface((90, 90))

def queue_pos(t, width):
    n, x, y = 2*(width+1), None, None
    relative_t = t % n

    if relative_t < 2:
        x = 0
    elif relative_t <= width:
        x = relative_t-1
    elif relative_t < width+2:
        x = width-1
    else:
        x = n - relative_t -1
    if relative_t == 0:
        y = 0
    elif relative_t >= 1 and relative_t <= width:
        y = 1
    elif relative_t > 1+width:
        y = 3
    else:
        y = 2
    return x, y+t//n*4



i = 0
while running:
    screen.fill('black')

    gfxdraw.pixel(screen, *queue_pos(i, 20), [255]*3)

    real_screen.blit(pygame.transform.scale(screen, real_screen.get_rect().size), (0, 0))
    pygame.display.flip()
    clock.tick(20)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    i += 1
    if i == 200:
        i = 0
pygame.quit()