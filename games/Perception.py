import pygame
import pandas as pd
import os

pygame.init()

#colours
GREY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

#display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Perception Game")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

#load files
image_folder = "Images"
image_files = [f"{image_folder}/{i}.jpg" for i in range(1, 11)]
answers_df = pd.read_excel("answers.xlsx")

#instruction pages
instruction_page = True
next_button_rect = pygame.Rect(700, 500, 80, 50)

while instruction_page:
    screen.fill(WHITE)

    instruction_text = font.render("Welcome to the Same or Different Game!", True, BLACK)
    instruction_text2 = font.render("Press 'Next' to start the game.", True, BLACK)
    screen.blit(instruction_text, (50, 200))
    screen.blit(instruction_text2, (50, 250))

    pygame.draw.rect(screen, BLUE, next_button_rect)
    next_text = font.render("Next", True, WHITE)
    screen.blit(next_text, (720, 515))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if next_button_rect.collidepoint(mouse_pos):
                instruction_page = False


ready_page = True

while ready_page:
    screen.fill(WHITE)

    ready_text = font.render("Are you ready?", True, BLACK)
    ready_text2 = font.render("Press 'Next' to start the game.", True, BLACK)
    screen.blit(ready_text, (50, 200))
    screen.blit(ready_text2, (50, 250))

    pygame.draw.rect(screen, (0, 0, 255), next_button_rect)
    next_text = font.render("Next", True, WHITE)
    screen.blit(next_text, (720, 515))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if next_button_rect.collidepoint(mouse_pos):
                ready_page = False

#Main game

running = True

#initialise variables
image_index = 0
current_image = None
score = 0


while running and image_index < 10:
    screen.fill(WHITE)

    #load image
    if current_image is None:
        current_image = pygame.image.load(image_files[image_index])
        current_image = pygame.transform.scale(current_image, (WIDTH, HEIGHT))

    screen.blit(current_image, (0, 0))

    #buttons
    same_button = pygame.Rect(100, 500, 100, 50)
    different_button = pygame.Rect(600, 500, 140, 50)
    pygame.draw.rect(screen, BLUE, same_button)
    pygame.draw.rect(screen, RED, different_button)
    same_text = font.render("Same", True, WHITE)
    different_text = font.render("Different", True, WHITE)
    screen.blit(same_text, (120, 515))
    screen.blit(different_text, (620, 515))

    #score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

    question_start_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if same_button.collidepoint(mouse_pos):
                user_answer = "Same"

                #calculate time taken
                question_end_time = pygame.time.get_ticks()
                time_spent_on_question = (question_end_time - question_start_time) / 1000.0
                print(f"Time spent on question {image_index + 1}: {time_spent_on_question} seconds")

                #check answer
                correct_answer = answers_df.loc[image_index, "Answer"]
                if user_answer == correct_answer:
                    score += 1

                #adjust variables
                image_index += 1
                current_image = None

            elif different_button.collidepoint(mouse_pos):
                user_answer = "Different"

                #calculate time taken
                question_end_time = pygame.time.get_ticks()
                time_spent_on_question = (question_end_time - question_start_time) / 1000.0
                print(f"Time spent on question {image_index + 1}: {time_spent_on_question} seconds")

                #check answer
                correct_answer = answers_df.loc[image_index, "Answer"]
                if user_answer == correct_answer:
                    score += 1

                #adjust variables
                image_index += 1
                current_image = None

    clock.tick(30)

pygame.quit()


