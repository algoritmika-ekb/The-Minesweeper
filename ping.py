import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
TILE_SIZE = 40          # размер клетки в пикселях
MARGIN = 5              # отступ между клетками
WIDTH = 10              # ширина поля (клеток)
HEIGHT = 10             # высота поля (клеток)
MINES_COUNT = 15        # количество мин

# Цвета
COLOR_BG = (30, 30, 30)
COLOR_BOARD = (80, 80, 80)
COLOR_TILE_CLOSED = (170, 170, 170)
COLOR_TILE_OPEN = (200, 200, 200)
COLOR_BORDER_LIGHT = (255, 255, 255)
COLOR_BORDER_DARK = (100, 100, 100)
COLOR_MINE = (0, 0, 0)
COLOR_FLAG = (255, 50, 50)
COLOR_TEXT = (0, 0, 0)
COLOR_WIN = (0, 200, 0)
COLOR_LOSE = (200, 0, 0)

# Цвета для цифр
COLOR_NUMBERS = {
    1: (0, 0, 255),      # синий
    2: (0, 128, 0),      # зелёный
    3: (255, 0, 0),      # красный
    4: (0, 0, 128),      # тёмно-синий
    5: (128, 0, 0),      # коричневый
    6: (0, 128, 128),    # бирюзовый
    7: (0, 0, 0),        # чёрный
    8: (128, 128, 128)   # серый
}

# Размеры окна
WINDOW_WIDTH = WIDTH * (TILE_SIZE + MARGIN) + MARGIN
WINDOW_HEIGHT = HEIGHT * (TILE_SIZE + MARGIN) + MARGIN + 80  # дополнительное место для счётчика и кнопки

# Шрифты
FONT_SMALL = pygame.font.Font(None, 24)
FONT_LARGE = pygame.font.Font(None, 36)

class Tile:
    """Класс одной клетки поля"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0
        self.rect = pygame.Rect(
            MARGIN + x * (TILE_SIZE + MARGIN),
            MARGIN + y * (TILE_SIZE + MARGIN),
            TILE_SIZE,
            TILE_SIZE
        )

    def draw(self, screen):
        """Отрисовка клетки"""
        if self.is_revealed:
            # Открытая клетка
            pygame.draw.rect(screen, COLOR_TILE_OPEN, self.rect)
            pygame.draw.rect(screen, COLOR_BORDER_DARK, self.rect, 1)
            
            if self.is_mine:
                # Рисуем мину
                center = self.rect.center
                pygame.draw.circle(screen, COLOR_MINE, center, TILE_SIZE // 3)
                pygame.draw.line(screen, COLOR_MINE, 
                               (center[0] - TILE_SIZE//4, center[1]),
                               (center[0] + TILE_SIZE//4, center[1]), 2)
                pygame.draw.line(screen, COLOR_MINE,
                               (center[0], center[1] - TILE_SIZE//4),
                               (center[0], center[1] + TILE_SIZE//4), 2)
            elif self.neighbor_mines > 0:
                # Рисуем цифру
                text = FONT_SMALL.render(str(self.neighbor_mines), True, COLOR_NUMBERS.get(self.neighbor_mines, COLOR_TEXT))
                text_rect = text.get_rect(center=self.rect.center)
                screen.blit(text, text_rect)
        else:
            # Закрытая клетка
            pygame.draw.rect(screen, COLOR_TILE_CLOSED, self.rect)
            # 3D-эффект
            pygame.draw.line(screen, COLOR_BORDER_LIGHT, self.rect.topleft, self.rect.topright, 2)
            pygame.draw.line(screen, COLOR_BORDER_LIGHT, self.rect.topleft, self.rect.bottomleft, 2)
            pygame.draw.line(screen, COLOR_BORDER_DARK, self.rect.bottomright, self.rect.topright, 2)
            pygame.draw.line(screen, COLOR_BORDER_DARK, self.rect.bottomright, self.rect.bottomleft, 2)
            
            if self.is_flagged:
                # Рисуем флаг
                flag_points = [
                    (self.rect.x + 10, self.rect.y + 10),
                    (self.rect.x + 25, self.rect.y + 18),
                    (self.rect.x + 10, self.rect.y + 26)
                ]
                pygame.draw.polygon(screen, COLOR_FLAG, flag_points)
                pygame.draw.line(screen, COLOR_TEXT,
                               (self.rect.x + 10, self.rect.y + 10),
                               (self.rect.x + 10, self.rect.y + 30), 2)

class Minesweeper:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Сапёр - Minesweeper")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.reset_game()
        
    def reset_game(self):
        """Сброс игры до начального состояния"""
        self.board = [[Tile(x, y) for y in range(HEIGHT)] for x in range(WIDTH)]
        self.game_over = False
        self.won = False
        self.first_move = True
        self.flags_placed = 0
        
        # Кнопка "Новая игра"
        self.reset_button = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 50, 100, 40)
        
        # Счётчик мин
        self.mines_left = MINES_COUNT
        
    def place_mines(self, first_x, first_y):
        """Размещение мин после первого клика, гарантируя безопасность первой клетки"""
        mines_to_place = MINES_COUNT
        safe_cells = []
        
        # Собираем все клетки, кроме первой и её соседей (для лучшего опыта)
        for x in range(WIDTH):
            for y in range(HEIGHT):
                # Исключаем первую клетку
                if x == first_x and y == first_y:
                    continue
                # Исключаем соседей первой клетки (чтобы не взорваться сразу)
                if abs(x - first_x) <= 1 and abs(y - first_y) <= 1:
                    continue
                safe_cells.append((x, y))
        
        # Перемешиваем безопасные клетки
        random.shuffle(safe_cells)
        
        # Устанавливаем мины
        for i in range(min(mines_to_place, len(safe_cells))):
            x, y = safe_cells[i]
            self.board[x][y].is_mine = True
        
        # Вычисляем количество мин вокруг каждой клетки
        self.calculate_neighbors()
        
    def calculate_neighbors(self):
        """Вычисляет количество мин вокруг каждой клетки"""
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if self.board[x][y].is_mine:
                    continue
                
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                            if self.board[nx][ny].is_mine:
                                count += 1
                self.board[x][y].neighbor_mines = count
    
    def reveal_empty_areas(self, x, y):
        """Рекурсивно открывает пустые области (flood fill)"""
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            return
        
        tile = self.board[x][y]
        if tile.is_revealed or tile.is_flagged:
            return
        
        tile.is_revealed = True
        
        if tile.neighbor_mines == 0 and not tile.is_mine:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    self.reveal_empty_areas(x + dx, y + dy)
    
    def reveal_tile(self, x, y):
        """Открывает клетку"""
        if self.game_over:
            return False
        
        tile = self.board[x][y]
        
        if tile.is_revealed or tile.is_flagged:
            return False
        
        # Первый ход: размещаем мины
        if self.first_move:
            self.first_move = False
            self.place_mines(x, y)
            # После размещения мин пересчитываем neighbours (уже есть в place_mines)
        
        # Проверка на мину
        if tile.is_mine:
            self.game_over = True
            self.won = False
            self.reveal_all_mines()
            return False
        
        # Открываем клетку
        if tile.neighbor_mines == 0:
            self.reveal_empty_areas(x, y)
        else:
            tile.is_revealed = True
        
        # Проверка победы
        self.check_win()
        return True
    
    def reveal_all_mines(self):
        """Открывает все мины при проигрыше"""
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if self.board[x][y].is_mine:
                    self.board[x][y].is_revealed = True
    
    def check_win(self):
        """Проверяет, выиграл ли игрок"""
        revealed_count = 0
        total_non_mines = WIDTH * HEIGHT - MINES_COUNT
        
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if self.board[x][y].is_revealed and not self.board[x][y].is_mine:
                    revealed_count += 1
        
        if revealed_count == total_non_mines:
            self.game_over = True
            self.won = True
            # Отмечаем все мины флагами для красоты
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    if self.board[x][y].is_mine:
                        self.board[x][y].is_flagged = True
    
    def toggle_flag(self, x, y):
        """Устанавливает или снимает флаг"""
        if self.game_over:
            return
        
        tile = self.board[x][y]
        if tile.is_revealed:
            return
        
        if not tile.is_flagged:
            if self.flags_placed < MINES_COUNT:
                tile.is_flagged = True
                self.flags_placed += 1
                self.mines_left = MINES_COUNT - self.flags_placed
        else:
            tile.is_flagged = False
            self.flags_placed -= 1
            self.mines_left = MINES_COUNT - self.flags_placed
    
    def draw(self):
        """Отрисовка всего интерфейса"""
        self.screen.fill(COLOR_BG)
        
        # Отрисовка поля
        for x in range(WIDTH):
            for y in range(HEIGHT):
                self.board[x][y].draw(self.screen)
        
        # Отрисовка информационной панели
        panel_rect = pygame.Rect(0, HEIGHT * (TILE_SIZE + MARGIN) + MARGIN, WINDOW_WIDTH, 80)
        pygame.draw.rect(self.screen, COLOR_BOARD, panel_rect)
        
        # Счётчик мин
        mine_text = FONT_LARGE.render(f"💣 {self.mines_left}", True, COLOR_TEXT)
        self.screen.blit(mine_text, (20, HEIGHT * (TILE_SIZE + MARGIN) + MARGIN + 15))
        
        # Кнопка "Новая игра"
        pygame.draw.rect(self.screen, (150, 150, 150), self.reset_button)
        pygame.draw.rect(self.screen, COLOR_BORDER_DARK, self.reset_button, 2)
        reset_text = FONT_SMALL.render("НОВАЯ", True, COLOR_TEXT)
        text_rect = reset_text.get_rect(center=self.reset_button.center)
        self.screen.blit(reset_text, text_rect)
        
        # Сообщение о победе/поражении
        if self.game_over:
            if self.won:
                msg = "ПОБЕДА! 🎉"
                color = COLOR_WIN
            else:
                msg = "ПОРАЖЕНИЕ! 💥"
                color = COLOR_LOSE
            
            msg_text = FONT_LARGE.render(msg, True, color)
            msg_rect = msg_text.get_rect(center=(WINDOW_WIDTH // 2, HEIGHT * (TILE_SIZE + MARGIN) + MARGIN + 45))
            self.screen.blit(msg_text, msg_rect)
        
        pygame.display.flip()
    
    def handle_click(self, pos, right_click=False):
        """Обрабатывает клики мыши"""
        # Проверка клика по кнопке "Новая игра"
        if self.reset_button.collidepoint(pos):
            self.reset_game()
            return
        
        # Определяем, по какой клетке кликнули
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if self.board[x][y].rect.collidepoint(pos):
                    if right_click:
                        self.toggle_flag(x, y)
                    else:
                        self.reveal_tile(x, y)
                    return
    
    def run(self):
        """Главный игровой цикл"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка
                        self.handle_click(event.pos, right_click=False)
                    elif event.button == 3:  # Правая кнопка
                        self.handle_click(event.pos, right_click=True)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Клавиша R для перезапуска
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:  # ESC для выхода
                        running = False
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Minesweeper()
    game.run()