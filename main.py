import pygame
from chess_pieces import Pawn, Knight, Bishop, Rook, Queen, King

# Инициализация pygame
pygame.init()

# Константы
window_size = 640
board_size = 8
square_size = window_size // board_size
fps = 60

# Цвета
dark_square = (181, 136, 99)
light_square = (240, 217, 181)
highlight = (100, 249, 83, 150)
move_highlight = (200, 200, 200, 100)
check_highlight = (255, 0, 0, 150)
fog_of_war = (0, 0, 0)  # Непрозрачный черный цвет
promotion_background = (50, 50, 50, 200)

# Настройка дисплея
screen = pygame.display.set_mode((window_size, window_size))
pygame.display.set_caption('Шахматы')
clock = pygame.time.Clock()

# Инициализация шрифта
pygame.font.init()


class ChessGame:
    """Основной класс шахматной игры"""

    def __init__(self) -> None:
        """Инициализация шахматной игры"""
        self.board = [[None for _ in range(board_size)] for _ in range(board_size)]
        self.selected_piece = None
        self.valid_moves = []
        self.current_player = 0  # 0 для белых, 1 для черных
        self.game_over = False
        self.check = False
        self.en_passant = None
        self.promotion_pending = None  # (x, y) координаты пешки для превращения
        self.castling_rights = {
            'white_king_side': True,
            'white_queen_side': True,
            'black_king_side': True,
            'black_queen_side': True
        }
        self.initialize_board()

    def initialize_board(self) -> None:
        """Начальная расстановка фигур на доске"""
        # Пешки
        for i in range(board_size):
            self.board[1][i] = Pawn(1)  # Черные пешки
            self.board[6][i] = Pawn(0)  # Белые пешки

        # Остальные фигуры
        back_row_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        # Черные фигуры (верх)
        for i, piece_class in enumerate(back_row_order):
            self.board[0][i] = piece_class(1)

        # Белые фигуры (низ)
        for i, piece_class in enumerate(back_row_order):
            self.board[7][i] = piece_class(0)

    def draw_board(self) -> None:
        """Отрисовка шахматной доски"""
        # Отрисовка клеток
        for row in range(board_size):
            for col in range(board_size):
                color = light_square if (row + col) % 2 == 0 else dark_square
                pygame.draw.rect(screen, color,
                                 (col * square_size, row * square_size,
                                  square_size, square_size))

    def draw_pieces(self) -> None:
        """Отрисовка всех фигур на доске"""
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                if piece:
                    try:
                        image = pygame.image.load(piece.get_image_path())
                        image = pygame.transform.scale(image, (square_size - 10, square_size - 10))
                        screen.blit(image, (col * square_size + 5, row * square_size + 5))
                    except pygame.error:
                        # Запасной вариант если картинок нет
                        font = pygame.font.SysFont(None, 36)
                        text_color = (255, 255, 255) if piece.color == 1 else (0, 0, 0)
                        text = font.render(piece.symbol, True, text_color)
                        screen.blit(text, (col * square_size + 20, row * square_size + 20))

    def draw_promotion_menu(self) -> None:
        """Отрисовка меню превращения пешки"""
        if not self.promotion_pending:
            return

        x, y = self.promotion_pending
        color = self.board[y][x].color

        menu_width = square_size * 2
        menu_height = square_size * 4
        menu_x = (window_size - menu_width) // 2
        menu_y = (window_size - menu_height) // 2

        # Рисуем фон меню
        menu_bg = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_bg.fill((240, 240, 240, 240))
        screen.blit(menu_bg, (menu_x, menu_y))

        # Заголовок меню
        font_title = pygame.font.SysFont(None, 32)
        title_text = "Выберите фигуру для превращения"
        title_surface = font_title.render(title_text, True, (255, 255, 255))
        title_width = title_surface.get_width() + 20
        title_height = title_surface.get_height() + 10
        title_bg = pygame.Surface((title_width, title_height), pygame.SRCALPHA)
        title_bg.fill((0, 0, 0, 200))
        title_rect = title_surface.get_rect(center=(window_size // 2, menu_y - 25))
        title_bg_rect = title_bg.get_rect(center=title_rect.center)
        screen.blit(title_bg, title_bg_rect)
        screen.blit(title_surface, title_rect)

        # Фигуры для превращения
        pieces = [Queen, Rook, Bishop, Knight]
        piece_names = ["Ферзь", "Ладья", "Слон", "Конь"]

        for i, (piece_class, piece_name) in enumerate(zip(pieces, piece_names)):
            piece_y = menu_y + i * (menu_height // 4)

            # Подсветка при наведении
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if (menu_x <= mouse_x <= menu_x + menu_width and
                    piece_y <= mouse_y <= piece_y + menu_height // 4):
                highlight_surface = pygame.Surface((menu_width, menu_height // 4), pygame.SRCALPHA)
                highlight_surface.fill((100, 150, 255, 100))
                screen.blit(highlight_surface, (menu_x, piece_y))

            # Разделительная линия
            if i > 0:
                pygame.draw.line(screen, (150, 150, 150),
                                 (menu_x, piece_y),
                                 (menu_x + menu_width, piece_y), 2)

            # Отображение фигуры
            temp_piece = piece_class(color)

            try:
                image_size = (menu_height // 4 - 20, menu_height // 4 - 20)
                image = pygame.image.load(temp_piece.get_image_path())
                image = pygame.transform.scale(image, image_size)
                screen.blit(image, (menu_x + 15, piece_y + 10))
            except pygame.error:
                font_symbol = pygame.font.SysFont(None, 48)
                symbol_color = (0, 0, 0) if color == 0 else (255, 255, 255)
                symbol_bg_color = (255, 255, 255) if color == 1 else (0, 0, 0)

                # Фон для символа
                symbol_bg = pygame.Surface((40, 40), pygame.SRCALPHA)
                symbol_bg.fill(symbol_bg_color)
                screen.blit(symbol_bg, (menu_x + 10, piece_y + 5))

                symbol_surface = font_symbol.render(temp_piece.symbol, True, symbol_color)
                symbol_rect = symbol_surface.get_rect(center=(menu_x + 30, piece_y + menu_height // 8))
                screen.blit(symbol_surface, symbol_rect)

            # Отображаем название фигуры
            font_text = pygame.font.SysFont(None, 28)
            name_surface = font_text.render(piece_name, True, (0, 0, 0))
            name_rect = name_surface.get_rect(midleft=(menu_x + 80, piece_y + menu_height // 8))
            screen.blit(name_surface, name_rect)

    def draw_highlights(self) -> None:
        """Отрисовка подсветки выбранной фигуры и допустимых ходов"""
        if self.promotion_pending:
            return

        # Подсветка выбранной фигуры
        if self.selected_piece:
            x, y = self.selected_piece
            highlight_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            highlight_surface.fill(highlight)
            screen.blit(highlight_surface, (x * square_size, y * square_size))

            # Подсветка позиции курсора
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x, grid_y = mouse_x // square_size, mouse_y // square_size
            if 0 <= grid_x < board_size and 0 <= grid_y < board_size:
                cursor_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
                cursor_surface.fill(move_highlight)
                screen.blit(cursor_surface, (grid_x * square_size, grid_y * square_size))

        # Отрисовка допустимых ходов
        for x, y in self.valid_moves:
            pygame.draw.circle(screen, (200, 200, 200),
                               (x * square_size + square_size // 2,
                                y * square_size + square_size // 2),
                               10)

    def draw_fog_of_war(self) -> None:
        """Отрисовка тумана войны - показываются все клетки, куда могут пойти фигуры текущего игрока за один ход"""
        # Создаем поверхность для тумана войны
        fog_surface = pygame.Surface((window_size, window_size))
        fog_surface.fill(fog_of_war)

        # Определяем видимые области для текущего игрока
        visible_areas = []

        # Добавляем позиции всех фигур текущего игрока
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                if piece is not None and piece.color == self.current_player:
                    visible_areas.append((col * square_size, row * square_size, square_size, square_size))

                    # Показываем возможные ходы из этой позиции
                    moves = piece.get_valid_moves(self.board, col, row, self.en_passant)
                    for move_x, move_y in moves:
                        visible_areas.append((move_x * square_size, move_y * square_size, square_size, square_size))

        # Вырезаем видимые области из тумана войны
        for area in visible_areas:
            pygame.draw.rect(fog_surface, (255, 255, 255), area)

        fog_surface.set_colorkey((255, 255, 255))
        screen.blit(fog_surface, (0, 0))

    def draw_check_indicator(self) -> None:
        """Подсветка короля при шаге"""
        if self.promotion_pending:
            return

        king_pos = self.find_king(self.current_player)
        if king_pos and self.is_in_check(self.current_player):
            x, y = king_pos
            check_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            check_surface.fill(check_highlight)
            screen.blit(check_surface, (x * square_size, y * square_size))

    def find_king(self, color: int) -> tuple:
        """
        Найти короля указанного цвета

        Args:
            color: цвет короля (0 - белый, 1 - черный)

        Returns:
            tuple: координаты короля (x, y) или None если не найден
        """
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                if isinstance(piece, King) and piece.color == color:
                    return (col, row)
        return None

    def is_in_check(self, color: int) -> bool:
        """
        Проверить, находится ли король указанного цвета под шахом

        Args:
            color: цвет короля (0 - белый, 1 - черный)

        Returns:
            bool: True если король под шахом
        """
        king_pos = self.find_king(color)
        if not king_pos:
            return False

        opponent_color = 1 - color
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                if piece is not None and piece.color == opponent_color:
                    moves = piece.get_valid_moves(self.board, col, row, self.en_passant)
                    if king_pos in moves:
                        return True

        return False

    def get_valid_moves_for_piece(self, x: int, y: int, include_checks: bool = True) -> list:
        """
        Получить допустимые ходы для фигуры в позиции (x, y)

        Args:
            x: координата x фигуры
            y: координата y фигуры
            include_checks: учитывать ли проверку шаха

        Returns:
            list: список допустимых ходов
        """
        piece = self.board[y][x]
        if piece is None:
            return []

        # Получить базовые ходы
        moves = piece.get_valid_moves(self.board, x, y, self.en_passant)

        if not include_checks:
            return moves

        # Отфильтровать ходы, которые ставят/оставляют короля под шахом
        valid_moves = []
        for move_x, move_y in moves:
            if self.is_move_valid((x, y), (move_x, move_y)):
                valid_moves.append((move_x, move_y))

        return valid_moves

    def is_move_valid(self, start_pos: tuple, end_pos: tuple) -> bool:
        """
        Проверить, является ли ход допустимым (не оставляет короля под шахом)

        Args:
            start_pos: начальная позиция (x, y)
            end_pos: конечная позиция (x, y)

        Returns:
            bool: True если ход допустим
        """
        start_x, start_y = start_pos
        end_x, end_y = end_pos

        # Временное выполнение хода
        temp_piece = self.board[end_y][end_x]
        moving_piece = self.board[start_y][start_x]

        self.board[end_y][end_x] = moving_piece
        self.board[start_y][start_x] = None

        # Проверить, находится ли король под шахом после хода
        in_check = self.is_in_check(moving_piece.color)

        # Отменить временный ход
        self.board[start_y][start_x] = moving_piece
        self.board[end_y][end_x] = temp_piece

        return not in_check


    def handle_promotion_click(self, pos: tuple) -> None:
        """Обработка клика в увеличенном меню превращения пешки"""
        if not self.promotion_pending:
            return

        click_x, click_y = pos

        # Размеры и позиция увеличенного меню
        menu_width = square_size * 2
        menu_height = square_size * 4
        menu_x = (window_size - menu_width) // 2
        menu_y = (window_size - menu_height) // 2

        # Проверяем, был ли клик в области меню
        if not (menu_x <= click_x <= menu_x + menu_width and
                menu_y <= click_y <= menu_y + menu_height):
            return

        x, y = self.promotion_pending
        pawn = self.board[y][x]

        # Определяем, какую фигуру выбрал игрок
        relative_y = click_y - menu_y
        piece_index = relative_y // (menu_height // 4)

        piece_types = ['Q', 'R', 'B', 'N']

        if 0 <= piece_index < len(piece_types):
            new_piece = pawn.promote(piece_types[piece_index])
            self.board[y][x] = new_piece
            self.promotion_pending = None

            # Следующий ход
            self.current_player = 1 - self.current_player

            # Проверяем состояние игры после превращения
            self.check = self.is_in_check(self.current_player)
            if self.is_checkmate():
                self.game_over = True
            elif self.is_stalemate():
                self.game_over = True

    def handle_click(self, pos: tuple) -> None:
        """
        Обработка клика мыши

        Args:
            pos: позиция клика (x, y)
        """
        if self.promotion_pending:
            self.handle_promotion_click(pos)
            return

        if self.game_over:
            return

        x, y = pos
        grid_x, grid_y = x // square_size, y // square_size

        if not (0 <= grid_x < board_size and 0 <= grid_y < board_size):
            return

        # Если фигура уже выбрана, попытаться сделать ход
        if self.selected_piece:
            start_x, start_y = self.selected_piece

            # Проверить, кликнули ли на допустимый ход
            if (grid_x, grid_y) in self.valid_moves:
                self.make_move((start_x, start_y), (grid_x, grid_y))
                self.selected_piece = None
                self.valid_moves = []
            else:
                # Кликнули на другую фигуру текущего игрока выбрать ее вместо текущей
                piece = self.board[grid_y][grid_x]
                if piece is not None and piece.color == self.current_player:
                    self.selected_piece = (grid_x, grid_y)
                    self.valid_moves = self.get_valid_moves_for_piece(grid_x, grid_y)
                else:
                    self.selected_piece = None
                    self.valid_moves = []
        else:
            # Фигура еще не выбрана
            piece = self.board[grid_y][grid_x]
            if piece is not None and piece.color == self.current_player:
                self.selected_piece = (grid_x, grid_y)
                self.valid_moves = self.get_valid_moves_for_piece(grid_x, grid_y)

    def make_move(self, start_pos: tuple, end_pos: tuple) -> None:
        """
        Выполнить ход на доске

        Args:
            start_pos: начальная позиция (x, y)
            end_pos: конечная позиция (x, y)
        """
        start_x, start_y = start_pos
        end_x, end_y = end_pos

        moving_piece = self.board[start_y][start_x]

        # Обработка взятия на проходе
        if isinstance(moving_piece, Pawn) and end_pos == self.en_passant:
            # Удалить взятую пешку
            capture_y = end_y + 1 if moving_piece.color == 0 else end_y - 1
            self.board[capture_y][end_x] = None

        # Обработка рокировки
        if isinstance(moving_piece, King) and abs(end_x - start_x) == 2:
            # Короткая рокировка
            if end_x > start_x:
                rook = self.board[start_y][7]
                self.board[start_y][5] = rook
                self.board[start_y][7] = None
                if rook:
                    rook.has_moved = True
            # Длинная рокировка
            else:
                rook = self.board[start_y][0]
                self.board[start_y][3] = rook
                self.board[start_y][0] = None
                if rook:
                    rook.has_moved = True

        # Обновление позиции фигуры
        self.board[end_y][end_x] = moving_piece
        self.board[start_y][start_x] = None
        moving_piece.has_moved = True

        # Проверка на превращение пешки
        if isinstance(moving_piece, Pawn) and moving_piece.should_promote(end_y):
            self.promotion_pending = (end_x, end_y)
            return

        # Установка цели для взятия на проходе
        if (isinstance(moving_piece, Pawn) and
                abs(end_y - start_y) == 2):
            self.en_passant = (start_x, (start_y + end_y) // 2)
        else:
            self.en_passant = None

        # Смена игрока
        self.current_player = 1 - self.current_player

        # Проверка окончания игры
        self.check = self.is_in_check(self.current_player)
        if self.is_checkmate():
            self.game_over = True
        elif self.is_stalemate():
            self.game_over = True

    def is_checkmate(self) -> bool:
        """
        Проверить, находится ли текущий игрок в мате

        Returns:
            bool: True если мат
        """
        if not self.is_in_check(self.current_player):
            return False

        # Проверить, может ли любой ход вывести из-под шаха
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                if piece is not None and piece.color == self.current_player:
                    moves = self.get_valid_moves_for_piece(col, row)
                    if moves:
                        return False

        return True

    def is_stalemate(self) -> bool:
        """
        Проверить, находится ли текущий игрок в пате

        Returns:
            bool: True если пат
        """
        if self.is_in_check(self.current_player):
            return False

        # Проверить, существует ли любой допустимый ход
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                if piece is not None and piece.color == self.current_player:
                    moves = self.get_valid_moves_for_piece(col, row)
                    if moves:
                        return False

        return True

    def draw_game_state(self) -> None:
        """Отрисовка текста состояния игры"""
        if self.promotion_pending:
            return

        if self.game_over:
            if self.is_checkmate():
                winner = "Черные" if self.current_player == 0 else "Белые"
                text = f"{winner} побеждают матом!"
            else:
                text = "Пат - Ничья!"

            font = pygame.font.SysFont(None, 36)
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(window_size // 2, window_size // 2))

            # Отрисовка фона для текста
            pygame.draw.rect(screen, (0, 0, 0),
                             (text_rect.x - 10, text_rect.y - 10,
                              text_rect.width + 20, text_rect.height + 20))
            screen.blit(text_surface, text_rect)

        elif self.check:
            font = pygame.font.SysFont(None, 24)
            text = f"{'Белые' if self.current_player == 0 else 'Черные'} под шахом!"
            text_surface = font.render(text, True, (255, 0, 0))
            screen.blit(text_surface, (10, 10))


def main() -> None:
    """Главная функция игры"""
    game = ChessGame()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)

        # Отрисовка всего (основные элементы)
        game.draw_board()
        game.draw_pieces()
        game.draw_highlights()
        game.draw_fog_of_war()
        game.draw_check_indicator()
        game.draw_game_state()

        if game.promotion_pending:
            game.draw_promotion_menu()

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()

if __name__ == "__main__":
    main()