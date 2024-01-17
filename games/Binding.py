import pygame
import sys
import os
import pandas as pd

pygame.init()

GREY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Game")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

#load files
image_folder = "images"
image_sets = [f"images{i}" for i in range(1, 33)]
excel_file_path = "bindinganswers.xlsx"  
answers_df = pd.read_excel(excel_file_path)

#buttons
def display_buttons():
    font = pygame.font.Font(None, 36)
    same_button = pygame.Rect(50, 500, 200, 50)
    different_button = pygame.Rect(550, 500, 200, 50)
    pygame.draw.rect(screen, WHITE, same_button)
    pygame.draw.rect(screen, WHITE, different_button)
    same_text = font.render("Same", True, BLACK)
    different_text = font.render("Different", True, BLACK)
    screen.blit(same_text, (same_button.x + 50, same_button.y + 15))
    screen.blit(different_text, (different_button.x + 20, different_button.y + 15))

#instruction pages
def display_instructions():
    font = pygame.font.Font(None, 36)
    instruction_text = [
        "Welcome to the Image Comparison Game!",
        "Instructions:......."
    ]

    screen.fill(GREY)  
    for i, line in enumerate(instruction_text):
        text = font.render(line, True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, 50 + i * 40))
        screen.blit(text, text_rect)

    pygame.display.flip()

    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting_for_key = False

        clock.tick(60)

    screen.fill(GREY)
    pygame.display.flip()

display_instructions()

# Main game 
for image_set in image_sets:
    user_response = None  

    #diplay image_1 for 2 seconds
    image_path_1 = os.path.join(image_folder, f"{image_set}_1.jpg")
    image_1 = pygame.image.load(image_path_1)
    image_rect = image_1.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(image_1, image_rect)
    pygame.display.flip()
    pygame.time.wait(2000)

    #display grey screen for 1 second
    screen.fill(GREY)
    pygame.display.flip()
    pygame.time.wait(1000)

    #display image_2 for 2 seconds 
    image_path_2 = os.path.join(image_folder, f"{image_set}_2.jpg")
    image_2 = pygame.image.load(image_path_2)
    screen.blit(image_2, image_rect)
    display_buttons()
    pygame.display.flip()

    #user response 
    while user_response is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                same_button_rect = pygame.Rect(50, 500, 200, 50)
                different_button_rect = pygame.Rect(550, 500, 200, 50)
                if same_button_rect.collidepoint(mouse_pos):
                    user_response = "Same"
                elif different_button_rect.collidepoint(mouse_pos):
                    user_response = "Different"

        clock.tick(60)

    screen.fill(GREY)
    pygame.display.flip()

    #check answer
    correct_answer = answers_df.loc[answers_df['Trial'] == image_set, 'Answer'].values[0]
    is_correct = user_response == correct_answer

    if is_correct:
        print(f"Correct! User response for {image_set}: {user_response}")
    else:
        print(f"Incorrect! User response for {image_set}: {user_response}")

pygame.quit()
sys.exit()
