Для работы потребуются библиотеки Python, и поэтому перед тем, как приступить к написанию, убедитесь, что у вас установлен Python (версия 3.12 или выше), если нет, то вы можете скачать её с официального сайта python.org. После скачивания python, нужно установить библиотеку:
<br>

<p align="center">
<img width="305" height="60" alt="image" src="https://github.com/user-attachments/assets/0b671e60-3113-4b0f-9955-b654cf354fab" />
</p>

#Структура проекта:

Cкачать фотографии фигур можно с GitHub
<br>

<p align="center">
<img width="648" height="237" alt="image" src="https://github.com/user-attachments/assets/418d81b6-25fa-484f-afd1-a01f0e986dd0" />
</p>

#2. Основная часть
##2.1 Реализация шахматных фигур
Каждая шахматная фигура реализована как отдельный класс, наследуемый от базового класса **ChessPiece**, такой объектно-ориентированный подход обеспечивает простоту расширения и поддержки кода. Каждый класс фигуры содержит метод **get_valid_moves()**, который возвращает список допустимых ходов для данной фигуры из текущей позиции
```python
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
```
##2.1.1 Пешка (Pawn)
Пешка является самой многочисленной, но при этом одной из самых сложных в реализации фигур из-за особых правил перемещения. В отличие от других фигур, пешка имеет различные правила для обычного хода, для хода с перовой клетки, для взятия фигур на проходе, также смены самой пешки на другую фигуру при достижении конца доски

Белая пешка движется вверх по доске (уменьшение координаты Y), а черная – вниз (увеличение координаты Y). Со стартовой позиции пешка может сделать двойной ход на две клетки вперед, если путь свободен. Для взятия фигур противника пешка движется по диагонали на одну клетку вперед. Особый случай - "взятие на проходе" - позволяет пешке взять пешку противника, которая только что сделала двойной ход и переместилась на соседнюю вертикаль
<br>

<p align="center">
<img width="649" height="650" alt="image" src="https://github.com/user-attachments/assets/ff81607c-bbd6-4b82-ab09-1cdd59d0f5ed" />
</p>
```python
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
```
##2.1.2 Конь (Knight)
Конь единственная фигура, способная перепрыгивать через другие фигуры, его движение описывается характерной буквой "Г", он перемещается на две клетки по одной оси и на одну клетку по другой. Это создает восемь возможных направлений движения из любой точки доски
<img width="458" height="457" alt="image" src="https://github.com/user-attachments/assets/a89451e6-1462-4dd8-b7d2-f2613d2c763d" />
```python
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
```
##2.1.3 Слон (Bishop)
Слон перемещается исключительно по диагоналям на любое количество клеток до тех пор, пока не встретит препятствие. Каждый слон остается на клетках одного цвета на протяжении всей игры
<br>

<p align="center">
<img width="520" height="520" alt="image" src="https://github.com/user-attachments/assets/95a22e41-4867-4a23-9d24-a320f9be82ee" />
</p>
```python
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
```
##2.1.4 Ладья (Rook)
Ладья движется по горизонталям и вертикалям на любое количество клеток. В начальной позиции ладьи занимают угловые клетки доски и участвуют в специальном ходе рокировке. Алгоритм перемещения ладьи аналогичен слону, но использует четыре ортогональных направления вместо диагональных
<img width="350" height="350" alt="image" src="https://github.com/user-attachments/assets/1c84b7e4-78c5-484f-9b7a-32458e8f8348" />
```python
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
```
##2.1.5 Ферзь (Queen)
Ферзь сочетает в себе возможности ладьи и слона, что делает его самой мощной фигурой на доске. Он может перемещаться на любое количество клеток по горизонтали, вертикали или диагонали. В реализации мы используем композицию, объединяя ходы ладьи и слона
<br>

<p align="center">
<img width="540" height="540" alt="image" src="https://github.com/user-attachments/assets/e215c792-3722-4d46-a39c-9def75fdd044" />
</p>
```python
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
```
##2.1.6 Король (King)
Король самая важная фигура, чья потеря означает проигрыш партии. Он перемещается на одну клетку в любом направлении. Особый ход рокировка позволяет королю переместиться на две клетки в сторону ладьи, а ладье перепрыгнуть через короля

В реализации учитывается, что король не может перемещаться на атакованные клетки, что проверяется в основном игровом цикле. Рокировка возможна только если король и соответствующая ладья не двигались с начала игры, между ними нет других фигур, и король не проходит через атакованные клетки
<img width="704" height="369" alt="image" src="https://github.com/user-attachments/assets/711ad95e-0bd1-4cc6-86a8-5bd50a811c59" />

```python
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
```
Каждая фигура демонстрирует различные аспекты объектно-ориентированного программирования: наследование, инкапсуляцию и полиморфизм. Общий интерфейс **get_valid_moves** позволяет единообразно обрабатывать все типы фигур в основном игровом цикле, при этом каждая фигура сохраняет свою уникальную логику поведения


#3. Итоги 
<br>

<p align="center">
<img width="645" height="646" alt="image" src="https://github.com/user-attachments/assets/3f36d2a5-0fa8-4626-a93e-850d2cff7fca" />
</p>
<br>

<p align="center">
<img width="780" height="769" alt="image" src="https://github.com/user-attachments/assets/70cc1395-2300-45b4-8fa5-527c5eec98e4" />
</p>

