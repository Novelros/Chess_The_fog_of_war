import pygame


class ChessPiece:
    """Базовый класс для всех шахматных фигур"""

    def __init__(self, color: int, symbol: str) -> None:
        """
        Инициализация шахматной фигуры

        Args:
            color: 0 - для белых, 1 - для черных
            symbol: символ фигуры (например: K - король)
        """
        self.color = color
        self.symbol = symbol
        self.has_moved = False

    def get_image_path(self) -> str:
        """Получить путь к изображению фигуры"""
        return f"{self.color}{self.symbol}.png"

    def get_valid_moves(self, board: list, x: int, y: int, en_passant: tuple = None) -> list:
        """Получить допустимые ходы для фигуры должен быть реализован в подклассах"""
        return []

    def is_opponent(self, other_piece) -> bool:
        """Проверить, является ли другая фигура фигурой противника"""
        return (other_piece is not None) and (other_piece.color != self.color)

    def is_empty_or_opponent(self, board: list, x: int, y: int) -> bool:
        """Проверить, является ли клетка пустой или содержит фигуру противника"""
        if not (0 <= x < 8 and 0 <= y < 8):
            return False
        target_piece = board[y][x]
        return target_piece is None or self.is_opponent(target_piece)


class Pawn(ChessPiece):
    """Класс пешки"""

    def __init__(self, color: int) -> None:
        super().__init__(color, 'P')

    def get_valid_moves(self, board: list, x: int, y: int, en_passant: tuple = None) -> list:
        """
        Получить допустимые ходы для пешки

        Args:
            board: шахматная доска
            x: текущая координата x
            y: текущая координата y
            en_passant: координаты для взятия на проходе

        Returns:
            list: список допустимых ходов
        """
        moves = []
        direction = -1 if self.color == 0 else 1  # Белые двигаются вверх, черные вниз

        # Ход вперед (на одну клетку)
        if 0 <= y + direction < 8 and board[y + direction][x] is None:
            moves.append((x, y + direction))

            # Двойной ход с начальной позиции
            start_row = 6 if self.color == 0 else 1
            if y == start_row and board[y + 2 * direction][x] is None:
                moves.append((x, y + 2 * direction))

        # Взятия
        for dx in [-1, 1]:
            new_x, new_y = x + dx, y + direction
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                target = board[new_y][new_x]
                if target is not None and self.is_opponent(target):
                    moves.append((new_x, new_y))

                # Взятие на проходе
                if en_passant == (new_x, new_y):
                    moves.append((new_x, new_y))

        return moves

    def should_promote(self, y: int) -> bool:
        """
        Проверить, должна ли пешка превратиться в другую фигуру

        Args:
            y: текущая координата y пешки

        Returns:
            bool: True, если пешка достигла последней горизонтали и False, если нет
        """
        # Белая пешка достигла верхнего края (y=0)
        if self.color == 0 and y == 0:
            return True
        # Черная пешка достигла нижнего края (y=7)
        if self.color == 1 and y == 7:
            return True
        return False

    def promote(self, piece_type: str) -> ChessPiece:
        """
        Превратить пешку в другую фигуру

        Args:
            piece_type: тип фигуры для превращения ('Q', 'R', 'B', 'N')

        Returns:
            ChessPiece: новая фигура
        """
        piece_classes = {
            'Q': Queen,
            'R': Rook,
            'B': Bishop,
            'N': Knight
        }

        if piece_type in piece_classes:
            return piece_classes[piece_type](self.color)
        else:
            return Queen(self.color)


class Knight(ChessPiece):
    """Класс коня (обозначается как N в шахматах)"""

    def __init__(self, color: int) -> None:
        super().__init__(color, 'N')

    def get_valid_moves(self, board: list, x: int, y: int, en_passant: tuple = None) -> list:
        """
        Получить допустимые ходы для коня

        Args:
            board: шахматная доска
            x: текущая координата x
            y: текущая координата y
            en_passant: координаты для взятия на проходе

        Returns:
            list: список допустимых ходов
        """
        moves = []
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

        for dx, dy in knight_moves:
            new_x, new_y = x + dx, y + dy
            if self.is_empty_or_opponent(board, new_x, new_y):
                moves.append((new_x, new_y))

        return moves


class Bishop(ChessPiece):
    """Класс слона"""

    def __init__(self, color: int) -> None:
        super().__init__(color, 'B')

    def get_valid_moves(self, board: list, x: int, y: int, en_passant: tuple = None) -> list:
        """
        Получить допустимые ходы для слона

        Args:
            board: шахматная доска
            x: текущая координата x
            y: текущая координата y
            en_passant: координаты для взятия на проходе

        Returns:
            list: список допустимых ходов
        """
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dx, dy in directions:
            for i in range(1, 8):
                new_x, new_y = x + i * dx, y + i * dy
                if not (0 <= new_x < 8 and 0 <= new_y < 8):
                    break

                if board[new_y][new_x] is None:
                    moves.append((new_x, new_y))
                elif self.is_opponent(board[new_y][new_x]):
                    moves.append((new_x, new_y))
                    break
                else:
                    break

        return moves


class Rook(ChessPiece):
    """Класс ладьи"""

    def __init__(self, color: int) -> None:
        super().__init__(color, 'R')

    def get_valid_moves(self, board: list, x: int, y: int, en_passant: tuple = None) -> list:
        """
        Получить допустимые ходы для ладьи

        Args:
            board: шахматная доска
            x: текущая координата x
            y: текущая координата y
            en_passant: координаты для взятия на проходе

        Returns:
            list: список допустимых ходов
        """
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in directions:
            for i in range(1, 8):
                new_x, new_y = x + i * dx, y + i * dy
                if not (0 <= new_x < 8 and 0 <= new_y < 8):
                    break

                if board[new_y][new_x] is None:
                    moves.append((new_x, new_y))
                elif self.is_opponent(board[new_y][new_x]):
                    moves.append((new_x, new_y))
                    break
                else:
                    break

        return moves


class Queen(ChessPiece):
    """Класс ферзя"""

    def __init__(self, color: int) -> None:
        super().__init__(color, 'Q')

    def get_valid_moves(self, board: list, x: int, y: int, en_passant: tuple = None) -> list:
        """
        Получить допустимые ходы для ферзя

        Args:
            board: шахматная доска
            x: текущая координата x
            y: текущая координата y
            en_passant: координаты для взятия на проходе

        Returns:
            list: список допустимых ходов
        """
        # Ферзь ходит как ладья + слон
        rook_moves = Rook(self.color).get_valid_moves(board, x, y)
        bishop_moves = Bishop(self.color).get_valid_moves(board, x, y)
        return rook_moves + bishop_moves


class King(ChessPiece):
    """Класс короля"""

    def __init__(self, color: int) -> None:
        super().__init__(color, 'K')

    def get_valid_moves(self, board: list, x: int, y: int, en_passant: tuple = None) -> list:
        """
        Получить допустимые ходы для короля

        Args:
            board: шахматная доска
            x: текущая координата x
            y: текущая координата y
            en_passant: координаты для взятия на проходе

        Returns:
            list: список допустимых ходов
        """
        moves = []
        king_moves = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        for dx, dy in king_moves:
            new_x, new_y = x + dx, y + dy
            if self.is_empty_or_opponent(board, new_x, new_y):
                moves.append((new_x, new_y))

        # Рокировка
        if not self.has_moved:
            # Короткая рокировка
            if (board[y][x + 1] is None and board[y][x + 2] is None and
                    isinstance(board[y][x + 3], Rook) and not board[y][x + 3].has_moved):
                moves.append((x + 2, y))

            # Длинная рокировка
            if (board[y][x - 1] is None and board[y][x - 2] is None and
                    board[y][x - 3] is None and
                    isinstance(board[y][x - 4], Rook) and not board[y][x - 4].has_moved):
                moves.append((x - 2, y))

        return moves