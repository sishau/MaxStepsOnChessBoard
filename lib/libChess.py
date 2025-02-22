from abc import ABC, abstractmethod
import numpy as np

class ChessTemplate(ABC):
    _angle_pos = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    def __init__(self, flip=False):
        self.flip = flip
        self._rotation = None
        self.ctype = None

    @property
    @abstractmethod
    def allowed_inputs(self):
        pass

    @abstractmethod
    def _move_place(self, input_angle):
        pass

    @abstractmethod
    def _move_next(self, input_angle):
        pass

    def move(self, input_angle):
        if self._rotation is None:
            next_angle =  self._move_place(input_angle)
        else:
            next_angle = self._move_next(input_angle)

        if next_angle is None:
            return None, None
        return next_angle, self._angle_pos[next_angle]

    @abstractmethod
    def __repr__(self):
        pass

class ChessA(ChessTemplate):
    def __init__(self, flip=False):
        super().__init__(flip)
        self.ctype = "A"

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, input_angle):
        self._rotation = 0 if input_angle % 2 == 0 else 1

    @property
    def allowed_inputs(self):
        return [0, 2, 4, 6] if self.rotation == 0 else [1, 3, 5, 7]

    def _move_place(self, input_angle):
        self.rotation = input_angle
        return input_angle

    def _move_next(self, input_angle):
        if input_angle not in self.allowed_inputs:
            return None
        return input_angle

    def __repr__(self):
        return "  + " if self.rotation == 0 else "  ☓ "

class ChessB(ChessTemplate):
    def __init__(self, flip=False):
        super().__init__(flip)
        self._angle_map = {
            0: {0: 6, 2: 4, 4: 2, 6: 0},
            1: {1: 7, 3: 5, 5: 3, 7: 1},
            2: {0: 2, 2: 0, 4: 6, 6: 4},
            3: {1: 3, 3: 1, 5: 7, 7: 5}
        }
        self.ctype = "B"

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, input_angle):
        self._rotation = (input_angle + 2) % 4 if self.flip else input_angle % 4

    @property
    def allowed_inputs(self):
        return [0, 2, 4, 6] if self.rotation %2 == 0 else [1, 3, 5, 7]

    def _move_place(self, input_angle):
        self.rotation = input_angle
        return (input_angle + 2) % 8 if self.flip else (input_angle - 2) % 8

    def _move_next(self, input_angle):
        if input_angle not in self.allowed_inputs:
            return None
        return self._angle_map[self.rotation][input_angle]

    def __repr__(self):
        match self.rotation:
            case 0:
                return " ╮╰ "
            case 1:
                return "  ꇤ "
            case 2:
                return " ╯╭ "
            case 3:
                return ")  ("

class ChessC(ChessTemplate):
    def __init__(self, flip=False):
        super().__init__(flip)
        self._angle_map = {
            0: {0: 7, 3: 4},
            1: {1: 0, 4: 5},
            2: {2: 1, 5: 6},
            3: {3: 2, 6: 7},
            4: {4: 3, 7: 0},
            5: {5: 4, 0: 1},
            6: {6: 5, 1: 2},
            7: {7: 6, 2: 3}
        }
        self.ctype = "C"

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, input_angle):
        self._rotation = (input_angle - 3) % 8 if self.flip else input_angle

    @property
    def allowed_inputs(self):
        return [(x + self.rotation) % 8 for x in (0, 3)]

    def _move_place(self, input_angle):
        self.rotation = input_angle
        return (input_angle + 1) % 8 if self.flip else (input_angle - 1) % 8

    def _move_next(self, input_angle):
        return None

    def __repr__(self):
        match self.rotation:
            case 0:
                return " ⸌╴ "
            case 1:
                return " ─⸍ "
            case 2:
                return " ⸝╵ "
            case 3:
                return " ⸌╷ "
            case 4:
                return " ─⸜ "
            case 5:
                return " ⸝─ "
            case 6:
                return " ╷⸍ "
            case 7:
                return " ╵⸜ "

class ChessStart(ChessTemplate):
    def __init__(self, flip=False):
        super().__init__(flip)
        self.ctype = "S"

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, input_angle):
        self._rotation = input_angle % 8

    @property
    def allowed_inputs(self):
        return [0, 1, 2, 3, 4, 5, 6, 7]

    def _move_place(self, input_angle):
        self.rotation = input_angle
        return input_angle

    def _move_next(self, input_angle):
        return None

    def __repr__(self):
        match self.rotation:
            case 0:
                return "←--o"
            case 1:
                return " ↙o "
            case 2:
                return " ↓o "
            case 3:
                return " o↘ "
            case 4:
                return "o--→"
            case 5:
                return " o↗ "
            case 6:
                return " o↑ "
            case 7:
                return " ↖o "

class ChessEnd(ChessTemplate):
    def __init__(self, flip=False):
        super().__init__(flip)
        self.ctype = "E"

    @property
    def allowed_inputs(self):
        return [0, 1, 2, 3, 4, 5, 6, 7]

    def _move_place(self, input_angle):
        return None

    def _move_next(self, input_angle):
        return None

    def __repr__(self):
        return "  O "


class ChessBoard:
    def __init__(self, size=(6, 6)):
        self.size = size
        self.grid = np.empty(size, dtype=object)
        self.chesses = {
            "A": ChessA,
            "B": ChessB,
            "C": ChessC,
            "S": ChessStart,
            "E": ChessEnd
        }

    def pos_valid(self, pos):
        return 0 <= pos[0] < self.size[0] and 0 <= pos[1] < self.size[1]

    def count_steps(self, start_pos, start_angle, chess_seq, flip_seq):
        chess_seq.append("E")
        flip_seq.append(False)
        steps = 0
        current_chess = ChessStart()
        current_pos = start_pos
        current_angle = start_angle
        self.grid[start_pos] = current_chess
        while chess_seq:
            existed_chess = self.grid[current_pos]
            if existed_chess is not None:
                current_chess = existed_chess
            else:
                chess_type = chess_seq.pop(0)
                flip = flip_seq.pop(0)
                current_chess = self.chesses[chess_type](flip)
                self.grid[current_pos] = current_chess
            if current_chess.ctype == "E":
                steps += 2
                break
            current_angle, move_pos = current_chess.move(current_angle)
            if current_angle is None:
                break
            steps += 1
            if steps > 50:
                print(f"Deed loop:\n {self.grid}")
                break
            current_pos = (current_pos[0] + move_pos[0], current_pos[1] + move_pos[1])
            if not self.pos_valid(current_pos):
                break
        return steps

    def __repr__(self):

        return f"\n{self.grid}"

if __name__ == '__main__':
    import random
    board = ChessBoard()
    start_pos = (random.randint(0, 5), random.randint(0, 5))
    start_angle = random.randint(0, 7)
    chess_seq = ["A"]*10 + ["B"]*10 + ["C"]*8
    random.shuffle(chess_seq)
    flip_seq = [random.choice([True, False]) for _ in range(28)]
    steps = board.count_steps(start_pos, start_angle, chess_seq, flip_seq)
    print(board)
    print(steps)

