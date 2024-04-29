import pygame, h5py, colorsys
from pygame import gfxdraw
import numpy as np
from tqdm import tqdm

import sys
np.set_printoptions(threshold=sys.maxsize)

class Client():
    def __init__(self, id, attrs):
        self.id = id
        self.pos = (None, None)
        self.traj = None
        self.current_resto_id = None

        attrs[0] = max(min(attrs[0], 1), 0)
        attrs[1] = max(min(attrs[1]/10, 1), 0)
        self.color = (attrs[1]/3+.6, attrs[0], 1)
        self.color = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(*self.color))
        #self.color = (255, 255, 255)

    def step(self):
        if self.traj:
            gfxdraw.pixel(screen, *self.pos, [0] * 3)
            self.pos = self.traj[0]
            self.traj.pop(0)
            gfxdraw.pixel(screen, *self.pos, self.color)
            return True
        else:
            return False

    def swap(self, resto_id, qe):
        self.traj = [(resto_pos[self.current_resto_id]+resto_size[0], self.pos[1])]
        for i in range(1, 1+mid_line-self.pos[1]):
            self.traj.append( (self.traj[0][0], self.traj[0][1]+i) )

        direction = int((queue_start[resto_id][0] - self.traj[-1][0]) / abs(queue_start[resto_id][0] - self.traj[-1][0]))
        for i in range(1, 1+abs(queue_start[resto_id][0]-self.traj[-1][0])):
            self.traj.append( (self.traj[-(i+1)][0]+i*direction, self.traj[-1][1]) )

        targ_qp = int(qe[resto_id]) # target queue pos (id)
        for i in range(1+qdlw[0]-targ_qp):
            self.traj.append( queue_pos(qdlw[0] - i, qdlw[1], resto_id) )

        self.current_resto_id = resto_id

    def add(self, resto_id, qe, offset):
        self.pos = start_pos
        self.traj = [start_pos for i in range(offset+1)]
        for i in range(1, 1 + self.traj[0][1] - mid_line):
            self.traj.append((self.traj[0][0], self.traj[0][1] - i))

        direction = int((queue_start[resto_id][0] - self.traj[-1][0]) / abs(queue_start[resto_id][0] - self.traj[-1][0]))
        for i in range(1, 1 + abs(queue_start[resto_id][0] - self.traj[-1][0])):
            self.traj.append((self.traj[-(i + 1)][0] + i * direction, self.traj[-1][1]))

        targ_qp = int(qe[resto_id])  # target queue pos (id)
        for i in range(1 + qdlw[0] - targ_qp):
            self.traj.append(queue_pos(qdlw[0] - i, qdlw[1], resto_id))

        self.current_resto_id = resto_id


def current_queues(M_step):
    queues = np.zeros((3, MAX_LENGHT))
    for i in range(len(M_step)):
        if M_step[i][0] in [1, 2, 3]:
            queues[M_step[i][0]-1, M_step[i][1]] = i
    return queues

def queue_first_gap(queues):
    qe = np.zeros((3), dtype=int)
    for q in range(len(queues)):
        while queues[q][int(qe[q])] != 0:
            qe[q] += 1
    return qe

def queues_end(queues):
    qe = np.full((3), MAX_LENGHT, dtype=int)
    for q in range(len(queues)):
        while qe[q] > 0 and queues[q][qe[q]-1] == 0:
            qe[q] -= 1
    return qe

def queue_pos(t, width, resto_id):
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
    return x + resto_pos[resto_id] + 5, y+t//n*4 + 15

file = h5py.File('simLogData/log_3.h5', 'r')
M_steps = file['steps']
M_clientAttrs = file['clientAttrs']

MAX_LENGHT = 400
qdlw = [0, 18] #queue_default_length_width
trips = MAX_LENGHT // (2*(qdlw[1]+1)) +1
qdlw[0] = 2*(qdlw[1]+1)*trips
resto_size = (24, 14)
screen_size = (resto_size[0]*3 + 6*3, resto_size[1]+trips*4+10)
resto_pos = [1, 1+resto_size[0]+6, 1+resto_size[0]*2+6*2]
queue_start = [queue_pos(*qdlw, 0), queue_pos(*qdlw, 1), queue_pos(*qdlw, 2)]
mid_line = queue_start[0][1]+1
start_pos = (int(screen_size[0]/2), mid_line+10)
debugMode = False
videoMode = False

pygame.init()
screen_height = 400
if videoMode:
    real_screen = pygame.display.set_mode((1060, 800))
else:
    real_screen = pygame.display.set_mode((int(screen_height/screen_size[1]*screen_size[0]), screen_height))
clock = pygame.time.Clock()
running = True
restoC = pygame.image.load('demo/restoC.bmp')
restoF = pygame.image.load('demo/restoF.bmp')
restoP = pygame.image.load('demo/restoP.bmp')
screen = pygame.surface.Surface(screen_size)

clients = []
moving_clients = []

M_swap   = np.zeros((M_steps.shape[0], M_steps.shape[1]), dtype=np.uint16)
M_new    = np.zeros((M_steps.shape[0], M_steps.shape[1]), dtype=np.uint16)
M_eating = np.zeros((M_steps.shape[0], M_steps.shape[1]), dtype=np.uint16)
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

frameID= 0
def update_screen(tick=150):
    global frameID
    real_screen.blit(pygame.transform.scale(screen, real_screen.get_rect().size), (0, 0))
    pygame.display.flip()
    if not videoMode:
        clock.tick(tick)
    else:
        pygame.image.save(real_screen, f"vid/{frameID}.jpeg")
    frameID += 1

screen.fill('black')
screen.blit(restoC, (1, 1))
screen.blit(restoF, (1 + resto_size[0] + 6, 1))
screen.blit(restoP, (1 + resto_size[0] * 2 + 6 * 2, 1))
queues = current_queues(M_steps[0])

for i in tqdm(range(1, M_steps.shape[0]-1)):
    if debugMode:
        print(f"################## STEP {i} ##################")
    moving_clients = []

    # SWAPS
    moving_clients = []
    queues = current_queues(M_steps[i-1])
    qe = queues_end(queues)

    for j in range(len(M_swap[0])):
        if M_swap[i, j] != 0:
            clients[j].swap(int(M_swap[i, j]-1), qe)
            moving_clients.append(clients[j])
            queues[M_steps[i-1, j][0]-1, M_steps[i-1, j][1]] = 0
            queues[int(M_swap[i, j]-1), qe[int(M_swap[i, j]-1)]] = j

            qe[int(M_swap[i, j]-1)] += 1
    while moving_clients:
        k = 0
        while k < len(moving_clients):
            if not moving_clients[k].step():
                moving_clients.pop(k)
            else:
                k += 1
            update_screen()
    # SWAPS

    # CRAM
    if np.any(M_swap[i]):
        for q in range(len(queues)):
            new_queue = queues[q]
            new_queue = new_queue[new_queue != 0]
            for k in range(len(new_queue)):
                clients[int(new_queue[k])].traj = [queue_pos(k, qdlw[1], clients[int(new_queue[k])].current_resto_id)]
                clients[int(new_queue[k])].step()
                update_screen()
            new_queue = list(new_queue)
            while len(new_queue) < len(queues[q]):
                new_queue.append(0)
            queues[q] = new_queue.copy()
    # CRAM

    # NEW
    qe = queues_end(queues)
    moving_clients = []
    for j in range(len(M_new[i])):
        if M_new[i, j]:
            attrs = M_clientAttrs[j]
            clients.append(Client(j, attrs=attrs))
            moving_clients.append(clients[j])
            clients[j].add(M_steps[i, j][0]-1, qe, len(moving_clients)-1)
            queues[M_steps[i, j][0]-1, int(qe[M_steps[i, j][0]-1])] = j
            qe[M_steps[i, j][0]-1] += 1

    while moving_clients:
        k = 0
        while k < len(moving_clients):
            res = moving_clients[k].step()
            if not res:
                moving_clients.pop(k)
            else:
                k+=1
        update_screen()
    # NEW

    # FLUSH
    if np.any(M_eating[i]):
        for j in range(len(M_eating[i])):
            if M_eating[i, j]:
                queues[M_steps[i-1, j][0]-1, M_steps[i-1, j][1]] = 0
                gfxdraw.pixel(screen, *clients[j].pos , [255, 0, 0])
                update_screen(70)
        pygame.time.wait(100)
        for j in range(len(M_eating[i])):
            if M_eating[i, j]:
                gfxdraw.pixel(screen, *clients[j].pos , [0]*3)
                update_screen(70)
        for q in range(len(queues)):
            new_queue = queues[q]
            new_queue = new_queue[new_queue != 0]
            for k in range(len(new_queue)):
                clients[int(new_queue[k])].traj = [queue_pos(k, qdlw[1], clients[int(new_queue[k])].current_resto_id)]
                clients[int(new_queue[k])].step()
            new_queue = list(new_queue)
            while len(new_queue) < len(queues[q]):
                new_queue.append(0)
            queues[q] = new_queue.copy()
    # FLUSH

    update_screen()
    if debugMode:
        print(np.trim_zeros(queues[0], trim='b'), len(queues[0]))
        print(np.trim_zeros(queues[1], trim='b'), len(queues[1]))
        print(np.trim_zeros(queues[2], trim='b'), len(queues[2]))

    if not np.any(queues):
        screen.fill('black')
        screen.blit(restoC, (1, 1))
        screen.blit(restoF, (1 + resto_size[0] + 6, 1))
        screen.blit(restoP, (1 + resto_size[0] * 2 + 6 * 2, 1))
        update_screen()
        pygame.time.wait(500)
        break

pygame.quit()