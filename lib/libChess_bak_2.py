import numpy as np

# 下一颗棋子的输入角度 对应 下颗棋子相对当前棋子的位置
ang_pos = [
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1)
]

class Chess:
    def __init__(self, chess_type, input_angle=0, flip=False):
        self.ctype = chess_type.upper()
        self.input_angle = input_angle % 8
        self.flip = flip

    @property
    def rotation(self):
        match self.ctype:
            case 'START' | "A" | "END":
                return self.input_angle
            case "B":
                return (self.input_angle + 2) % 8 if self.flip else self.input_angle
            case "C":
                return (self.input_angle - 3) % 8 if self.flip else self.input_angle
            case _:
                return None

    def allowed_angles(self):
        match self.ctype:
            case "END":
                return [0, 1, 2, 3, 4, 5, 6, 7]
            case "A" | "B":
                res = [0, 2, 4, 6]
            case 'C':
                res = [0, 3]
            case _:
                res = []
        return [(x + self.rotation) % 8 for x in res]

    def get_angle_map(self):
        match self.ctype:
            case "B":
                return {
                    0: {0: 6, 2: 4, 4: 2, 6: 0},
                    1: {1: 7, 3: 5, 5: 3, 7: 1},
                    2: {0: 2, 2: 0, 4: 6, 6: 4},
                    3: {1: 3, 3: 1, 5: 7, 7: 5},
                    4: {0: 6, 2: 4, 4: 2, 6: 0},
                    5: {1: 7, 3: 5, 5: 3, 7: 1},
                    6: {0: 2, 2: 0, 4: 6, 6: 4},
                    7: {1: 3, 3: 1, 5: 7, 7: 5}
                }
            case "C":
                return {
                    0: {0: 7, 3: 4},
                    1: {1: 0, 4: 5},
                    2: {2: 1, 5: 6},
                    3: {3: 2, 6: 7},
                    4: {4: 3, 7: 0},
                    5: {5: 4, 0: 1},
                    6: {6: 5, 1: 2},
                    7: {7: 6, 2: 3}
                }
            case _:
                return None

    def get_next_angle(self, input_angle):
        if input_angle not in self.allowed_angles():
            return None
        if self.ctype  in ["START", "A"]:
            return input_angle
        angle_map = self.get_angle_map()
        if angle_map is None:
            return None
        return angle_map[self.rotation][input_angle]

    def move(self, input_angle):
        next_angle = self.get_next_angle(input_angle)
        if next_angle is None:
            return None, None
        return next_angle, ang_pos[next_angle]

    # def __repr__(self):
    #     return f"Chess({self.ctype}, {self.rotation})"

    def __repr__(self):
        match self.ctype:
            case "START":
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
            case "A":
                match self.rotation:
                    case 0 | 2 | 4 | 6:
                        return "  + "
                    case 1 | 3 | 5 | 7:
                        return "  ☓ "
            case "B":
                match self.rotation:
                    case 0 | 4:
                        return " ╮╰ "
                    case 1 | 5:
                        return "  ꇤ "
                    case 2 | 6:
                        return " ╯╭ "
                    case 3 | 7:
                        return ")  ("

            case "C":
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
            case "END":
                return "  O "
# ⦦⦧
class ChessBoard:
    def __init__(self, size=(6, 6)):
        self.size = size
        self.grid = np.empty(size, dtype=object)

    def pos_valid(self, pos):
        return 0 <= pos[0] < self.size[1] and 0 <= pos[1] < self.size[0]

    def count_steps(self, start_pos, start_angle, chess_seq, flip_seq):
        steps = 1
        start_chess = Chess("Start", start_angle)
        self.grid[start_pos[1]][start_pos[0]] = start_chess
        current_angle = start_angle
        move_pos = ang_pos[start_angle]
        current_pos = (start_pos[0] + move_pos[0], start_pos[1] + move_pos[1])
        while chess_seq:
            if not self.pos_valid(current_pos):
                break
            existed_chess = self.grid[current_pos[1]][current_pos[0]]
            if existed_chess is not None:
                current_chess = existed_chess
            else:
                chess_type = chess_seq.pop(0)
                flip = flip_seq.pop(0)
                current_chess = Chess(chess_type, current_angle, flip)
                self.grid[current_pos[1]][current_pos[0]] = current_chess
            next_angle, move_pos = current_chess.move(current_angle)
            if current_chess.ctype == "END":
                steps += 2
                break
            if next_angle is None:
                break
            steps += 1
            if steps > 50:
                print(f"Deed loop:\n {self.grid}")
                break
            current_angle = next_angle
            current_pos = (current_pos[0] + move_pos[0], current_pos[1] + move_pos[1])

        return steps

    def __repr__(self):
        return f"ChessBoard({self.size}: \n{self.grid})"

if __name__ == '__main__':
    import random
    board = ChessBoard()
    start_pos = (random.randint(0, 5), random.randint(0, 5))
    start_angle = random.randint(0, 7)

    chess_seq = ["A"]*10 + ["B"]*10 + ["C"]*8 + ["END"]
    random.shuffle(chess_seq)
    flip_seq = [random.choice([True, False]) for _ in range(29)]
    steps = board.count_steps(start_pos, start_angle, chess_seq, flip_seq)
    print(board)
    print(steps)
