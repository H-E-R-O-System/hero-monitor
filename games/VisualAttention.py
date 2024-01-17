import pygame
import sys
import random

pygame.init()

#colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#display
WIDTH, HEIGHT = 400, 400
GRID_SIZE = 4
CELL_SIZE = WIDTH // GRID_SIZE
MAX_ROUNDS = 20  

#generate game grid
def generate_grid(difficulty):
    letters_easy = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    letters_medium = [('E', 'F'), ('W', 'V'), ('L', 'I')]
    letters_hard = [('u', 'ú'), ('b', 'd'), ('m', 'n')]

    if difficulty == 'easy':
        letters = letters_easy
    elif difficulty == 'medium':
        letter_pair = random.choice(letters_medium)
        letters = ''.join(letter_pair)
    elif difficulty == 'hard':
        letter_pair = random.choice(letters_hard)
        letters = ''.join(letter_pair)
    else:
        raise ValueError("Invalid difficulty level")

    common_letter = random.choice(letters)
    grid = [[common_letter] * GRID_SIZE for _ in range(GRID_SIZE)]

    row = random.randint(0, GRID_SIZE - 1)
    col = random.randint(0, GRID_SIZE - 1)

    odd_letter = random.choice(letters.replace(common_letter, ''))
    grid[row][col] = odd_letter

    return grid, (row, col)

#draw grid
def draw_grid(screen, grid):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            pygame.draw.rect(screen, WHITE, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            font = pygame.font.Font(None, 36)
            text = font.render(grid[row][col], True, BLACK)
            text_rect = text.get_rect(center=(col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2))
            screen.blit(text, text_rect)

#sisplay final results
def display_final_results(screen, score, average_time):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    time_text = font.render(f"Average Time: {average_time} milliseconds", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
    time_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(score_text, score_rect)
    screen.blit(time_text, time_rect)
    pygame.display.flip()

# main game
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Visual attention")
    clock = pygame.time.Clock()

    score = 0
    total_time = 0
    rounds_played = 0
    correct_answers = 0  
    difficulty = 'easy'  
    current_grid, odd_position = generate_grid(difficulty)
    time_start = 0  

    while rounds_played < MAX_ROUNDS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                row = mouse_y // CELL_SIZE
                col = mouse_x // CELL_SIZE
                user_input = current_grid[row][col]

                if user_input == current_grid[odd_position[0]][odd_position[1]]:
                    score += 1
                    correct_answers += 1
                    time_taken = pygame.time.get_ticks() - time_start
                    total_time += time_taken
                    print(f"Correct! Time taken: {time_taken} milliseconds\n")
                else:
                    time_taken = pygame.time.get_ticks() - time_start
                    print(f"Wrong! The odd letter was: {current_grid[odd_position[0]][odd_position[1]]} \n")
                    print(f"Time taken: {time_taken} milliseconds\n")    
                    
                #new grid
                current_grid, odd_position = generate_grid(difficulty)
                time_start = pygame.time.get_ticks()  

                #increase difficulty
                if correct_answers == 5:
                    correct_answers = 0  
                    if difficulty == 'easy':
                        difficulty = 'medium'
                    elif difficulty == 'medium':
                        difficulty = 'hard'

                rounds_played += 1

        screen.fill(BLACK)
        draw_grid(screen, current_grid)
        pygame.display.flip()
        clock.tick(10)  
    
    average_time = total_time / MAX_ROUNDS if MAX_ROUNDS > 0 else 0
    display_final_results(screen, score, average_time)
    waiting_for_quit = True
    while waiting_for_quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting_for_quit = False

if __name__ == "__main__":
    main()