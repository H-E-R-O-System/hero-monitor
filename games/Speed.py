import pygame
import math
import random
import time

pygame.init()

#colours
WHITE = (255,255,255)
BLACK = (0,0,0)
PURPLE = (120,0,120)
BLUE = (0,0,255)
RED = (255,0,0)
ORANGE = (255,102,0)
PINK = (255,0,255)
GREEN = (153,204,0)
colors = [RED,PURPLE,BLUE,ORANGE,PINK,GREEN]

#display
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Speed Game")
screen.fill(WHITE)
clock = pygame.time.Clock()

#initial variables
initial_time = time.time()
data = [0,0,0,0,0,0,0,0,0,0]
clickcount = 0
score = 0
font = pygame.font.Font(None, 36)
surface = font.render("Speed Battery", False, RED)

cx = random.randint(15, WIDTH - 15)
cy = random.randint(40, HEIGHT - 400)
width_of_circle = random.randint(14, 20)
pygame.draw.circle(screen, random.choice(colors), (cx, cy), width_of_circle)


# Main Game
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    
    x = pygame.mouse.get_pos()[0]
    y = pygame.mouse.get_pos()[1]
    click = pygame.mouse.get_pressed()

    sqx = (x - cx)**2
    sqy = (y - cy)**2

    if math.sqrt(sqx + sqy) < width_of_circle and click[0] ==1:

        screen.fill(WHITE)
        clickcount += 1

        #time taken 
        final_time = time.time()
        timespent = initial_time - final_time
        print("time taken =",timespent)
        data.append(timespent)

        average = sum(data) / len(data)
        average_round = round(average, 3)
        average_text = font.render(f'-------{average_round} is your average--------', False, RED)
        width_of_circle = random.randint(15,30 )
        cx = random.randint(20, WIDTH - 100)
        cy = random.randint(20, HEIGHT - 100)
        if clickcount == 10:
            print('average =', average_text)
            screen.blit(average_text, (30, 550))
            width_of_circle = random.randint(0, 0)

        pygame.draw.circle(screen, random.choice(colors), (cx,cy), width_of_circle)

    screen.blit(surface,(200,20))
    pygame.display.update()
    clock.tick()
    
