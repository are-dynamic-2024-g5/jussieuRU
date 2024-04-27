import pygame, h5py
from pygame import gfxdraw
import numpy as np
from tqdm import tqdm

import sys
np.set_printoptions(threshold=sys.maxsize)

file = h5py.File('simLogData/log_0.h5', 'r')
M_steps = file['steps']
M_clientAttrs = file['clientAttrs']

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

M_swap   = np.zeros((M_steps.shape[0], M_steps.shape[1]))
M_new    = np.zeros((M_steps.shape[0], M_steps.shape[1]))
M_eating = np.zeros((M_steps.shape[0], M_steps.shape[1]))
M_inline = np.zeros((M_steps.shape[0], M_steps.shape[1]), dtype=np.uint16)
for i in tqdm(range(M_steps.shape[0]-1)):
    for j in range(M_steps.shape[1]):
        if M_steps[i, j, 0] != M_steps[i+1, j, 0]:
            if M_steps[i+1, j, 0] == 4:
                M_eating[i+1, j] = 1
            elif M_steps[i, j, 0] == 0:
                M_new[i+1, j] = 1
            else:
                M_swap[i+1, j] = M_steps[i+1, j, 0]
        elif M_steps[i, j, 1] != M_steps[i+1, j, 1]:
            M_inline[i+1, j] = M_steps[i+1, j, 1]

i = 0
while running:
    screen.fill('black')

    gfxdraw.pixel(screen, *queue_pos(i, 20), [255]*3)

    real_screen.blit(pygame.transform.scale(screen, real_screen.get_rect().size), (0, 0))
    pygame.display.flip()
    clock.tick(50)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    i += 1
    if i == 200:
        i = 0
pygame.quit()