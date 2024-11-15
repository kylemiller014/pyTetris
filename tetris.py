import pygame
import random

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 300, 600
BLOCK_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = SCREEN_WIDTH // BLOCK_SIZE, SCREEN_HEIGHT // BLOCK_SIZE
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
SCORE_BG = (50, 50, 50)
COLORS = [
    (0, 255, 255),    # Cyan
    (255, 165, 0),    # Orange
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (0, 255, 0),      # Green
    (255, 0, 0),      # Red
    (128, 0, 128)     # Purple
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],                  # I shape
    [[1, 1, 1], [0, 1, 0]],          # T shape
    [[1, 1, 0], [0, 1, 1]],          # S shape
    [[0, 1, 1], [1, 1, 0]],          # Z shape
    [[1, 1], [1, 1]],                # O shape
    [[1, 1, 1], [1, 0, 0]],          # L shape
    [[1, 1, 1], [0, 0, 1]]           # J shape
]

# Game variables
clock = pygame.time.Clock()
fall_time = 0
fall_speed = 0.5
score = 0
level = 1

class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x, self.y = GRID_WIDTH // 2 - len(self.shape[0]) // 2, 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for (x, y), color in locked_positions.items():
        grid[y][x] = color
    return grid

def draw_grid(grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(screen, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    for y in range(GRID_HEIGHT):
        pygame.draw.line(screen, GRAY, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))
    for x in range(GRID_WIDTH):
        pygame.draw.line(screen, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))

def valid_space(tetromino, grid):
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x, new_y = tetromino.x + x, tetromino.y + y
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or grid[new_y][new_x] != BLACK:
                    return False
    return True

def clear_rows(grid, locked_positions):
    global score, level
    rows_to_clear = [y for y in range(GRID_HEIGHT) if all(grid[y][x] != BLACK for x in range(GRID_WIDTH))]
    for y in rows_to_clear:
        for x in range(GRID_WIDTH):
            del locked_positions[(x, y)]
    for y in sorted(rows_to_clear):
        for pos in sorted(locked_positions.keys(), key=lambda p: p[1], reverse=True):
            x, row_y = pos
            if row_y < y:
                locked_positions[(x, row_y + 1)] = locked_positions.pop((x, row_y))
    score += len(rows_to_clear) * 100
    level = score // 500 + 1

def draw_window(grid, score, level):
    screen.fill(BLACK)
    draw_grid(grid)

    # Draw scoreboard background
    pygame.draw.rect(screen, SCORE_BG, (0, 0, SCREEN_WIDTH, 70))
    
    # Draw Score and Level
    font = pygame.font.SysFont("comicsans", 24)
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))
    
    pygame.display.update()

def show_game_over():
    font = pygame.font.SysFont("comicsans", 36)
    game_over_text = font.render("Game Over", True, WHITE)
    restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
    
    # Draw the popup background
    pygame.draw.rect(screen, SCORE_BG, (20, SCREEN_HEIGHT // 2 - 40, SCREEN_WIDTH - 40, 100))
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
    
    pygame.display.update()

def main():
    global fall_time, fall_speed, score, level
    locked_positions = {}
    grid = create_grid()
    current_tetromino = Tetromino()
    running = True
    game_over = False

    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if not game_over:
            if fall_time / 1000 >= fall_speed:
                fall_time = 0
                current_tetromino.y += 1
                if not valid_space(current_tetromino, grid):
                    current_tetromino.y -= 1
                    for y, row in enumerate(current_tetromino.shape):
                        for x, cell in enumerate(row):
                            if cell:
                                locked_positions[(current_tetromino.x + x, current_tetromino.y + y)] = current_tetromino.color
                    current_tetromino = Tetromino()
                    clear_rows(grid, locked_positions)
                    if not valid_space(current_tetromino, grid):
                        game_over = True
                    fall_speed = max(0.2, 0.5 - (level - 1) * 0.05)
                else:
                    clear_rows(grid, locked_positions)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_tetromino.x -= 1
                        if not valid_space(current_tetromino, grid):
                            current_tetromino.x += 1
                    elif event.key == pygame.K_RIGHT:
                        current_tetromino.x += 1
                        if not valid_space(current_tetromino, grid):
                            current_tetromino.x -= 1
                    elif event.key == pygame.K_DOWN:
                        current_tetromino.y += 1
                        if not valid_space(current_tetromino, grid):
                            current_tetromino.y -= 1
                    elif event.key == pygame.K_UP:
                        current_tetromino.rotate()
                        if not valid_space(current_tetromino, grid):
                            current_tetromino.rotate()
                            current_tetromino.rotate()
                            current_tetromino.rotate()
        else:
            show_game_over()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        main()
                    elif event.key == pygame.K_q:
                        running = False

        if not game_over:
            for y, row in enumerate(current_tetromino.shape):
                for x, cell in enumerate(row):
                    if cell:
                        grid[current_tetromino.y + y][current_tetromino.x + x] = current_tetromino.color
            draw_window(grid, score, level)

    pygame.quit()

if __name__ == "__main__":
    main()
