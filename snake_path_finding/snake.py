import pygame
from settings import *
from copy import deepcopy
from random import randrange


class Square:
    def __init__(self, pos, surface, is_apple=False):
        self.pos = pos
        self.surface = surface
        self.is_apple = is_apple
        self.is_tail = False
        self.dir = [-1, 0]

        if self.is_apple:
            self.dir = [0, 0]

    def draw(self, clr=SNAKE_CLR):
        x, y = self.pos[0], self.pos[1]
        ss, gs = SQUARE_SIZE, GAP_SIZE

        if self.dir == [-1, 0]:
            pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss + gs, ss if not self.is_tail else ss - 2*gs, ss - 2*gs))

        if self.dir == [1, 0]:
            pygame.draw.rect(self.surface, clr, (x * ss - gs, y * ss + gs, ss if not self.is_tail else ss - 2*gs, ss - 2*gs))

        if self.dir == [0, 1]:
            pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss - gs, ss - 2*gs, ss if not self.is_tail else ss - 2*gs))

        if self.dir == [0, -1]:
            pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss + gs, ss - 2*gs, ss if not self.is_tail else ss - 2*gs))

        if self.is_apple:
            pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss + gs, ss - 2*gs, ss - 2*gs))

    def move(self, direction):
        self.dir = direction
        self.pos[0] += self.dir[0]
        self.pos[1] += self.dir[1]

    def hitting_wall(self):
        return self.pos[0] < 0 or self.pos[0] >= ROWS or self.pos[1] < 0 or self.pos[1] >= ROWS


class Snake:
    def __init__(self, surface):
        self.surface = surface
        self.is_dead = False
        self.squares_start_pos = [[ROWS // 2 + i, ROWS // 2] for i in range(INITIAL_SNAKE_LENGTH)]
        self.turns = {}
        self.dir = [-1, 0]
        self.score = 0
        self.moves_without_eating = 0
        self.apple = Square([randrange(ROWS), randrange(ROWS)], self.surface, is_apple=True)

        self.previous_apple_pos = deepcopy(self.apple.pos)
        self.apple_distance = 0
        self.apple_cursor_pos = [randrange(ROWS), randrange(ROWS)]
        self.manual_food_mode = True

        self.squares = [Square(pos, self.surface) for pos in self.squares_start_pos]
        self.head = self.squares[0]
        self.tail = self.squares[-1]
        self.tail.is_tail = True

        self.path = []
        self.is_virtual_snake = False
        self.total_moves = 0
        self.won_game = False

    def draw(self):
        self.apple.draw(APPLE_CLR)
        self.head.draw(HEAD_CLR)
        for sqr in self.squares[1:]:
            if self.is_virtual_snake:
                sqr.draw(VIRTUAL_SNAKE_CLR)
            else:
                sqr.draw()

        # Draw distance info
        font = pygame.font.SysFont('Arial', 20)
        text = font.render(f'Distance: {self.apple_distance}', True, (255, 255, 255))
        self.surface.blit(text, (10, 10))

        if self.manual_food_mode:
            pygame.draw.rect(self.surface, (0, 0, 255),
                             (self.apple_cursor_pos[0] * SQUARE_SIZE + GAP_SIZE,
                              self.apple_cursor_pos[1] * SQUARE_SIZE + GAP_SIZE,
                              SQUARE_SIZE - 2 * GAP_SIZE,
                              SQUARE_SIZE - 2 * GAP_SIZE), 2)

    def set_direction(self, direction):
        if direction == 'left' and self.dir != [1, 0]:
            self.dir = [-1, 0]
        elif direction == 'right' and self.dir != [-1, 0]:
            self.dir = [1, 0]
        elif direction == 'up' and self.dir != [0, 1]:
            self.dir = [0, -1]
        elif direction == 'down' and self.dir != [0, -1]:
            self.dir = [0, 1]
        self.turns[self.head.pos[0], self.head.pos[1]] = self.dir

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]: self.set_direction('left')
        elif keys[pygame.K_RIGHT]: self.set_direction('right')
        elif keys[pygame.K_UP]: self.set_direction('up')
        elif keys[pygame.K_DOWN]: self.set_direction('down')

        if self.manual_food_mode:
            if keys[pygame.K_a]: self.apple_cursor_pos[0] = max(0, self.apple_cursor_pos[0] - 1)
            elif keys[pygame.K_d]: self.apple_cursor_pos[0] = min(ROWS - 1, self.apple_cursor_pos[0] + 1)
            elif keys[pygame.K_w]: self.apple_cursor_pos[1] = max(0, self.apple_cursor_pos[1] - 1)
            elif keys[pygame.K_s]: self.apple_cursor_pos[1] = min(ROWS - 1, self.apple_cursor_pos[1] + 1)
            elif keys[pygame.K_SPACE]:
                if self.is_position_free(self.apple_cursor_pos):
                    self.previous_apple_pos = deepcopy(self.apple.pos)
                    self.apple.pos = deepcopy(self.apple_cursor_pos)
                    self.apple_distance = distance(self.previous_apple_pos, self.apple.pos)

    def move(self):
        for j, sqr in enumerate(self.squares):
            p = (sqr.pos[0], sqr.pos[1])
            if p in self.turns:
                turn = self.turns[p]
                sqr.move(turn)
                if j == len(self.squares) - 1:
                    self.turns.pop(p)
            else:
                sqr.move(sqr.dir)
        self.moves_without_eating += 1

    def add_square(self):
        self.squares[-1].is_tail = False
        tail = self.squares[-1]
        direction = tail.dir
        offset = {tuple([1, 0]): [-1, 0], tuple([-1, 0]): [1, 0],
                  tuple([0, 1]): [0, -1], tuple([0, -1]): [0, 1]}
        new_pos = [tail.pos[0] + offset[tuple(direction)][0],
                   tail.pos[1] + offset[tuple(direction)][1]]
        new_square = Square(new_pos, self.surface)
        new_square.dir = direction
        new_square.is_tail = True
        self.squares.append(new_square)

    def reset(self):
        self.__init__(self.surface)

    def hitting_self(self):
        return any(sqr.pos == self.head.pos for sqr in self.squares[1:])

    def generate_apple(self):
        # Not needed in manual mode
        pass

    def eating_apple(self):
        if self.head.pos == self.apple.pos and not self.is_virtual_snake and not self.won_game:
            self.moves_without_eating = 0
            self.score += 1
            return True

    def go_to(self, position):
        x, y = self.head.pos
        if x - 1 == position[0]: self.set_direction('left')
        if x + 1 == position[0]: self.set_direction('right')
        if y - 1 == position[1]: self.set_direction('up')
        if y + 1 == position[1]: self.set_direction('down')

    def is_position_free(self, position):
        if position[0] >= ROWS or position[0] < 0 or position[1] >= ROWS or position[1] < 0:
            return False
        return not any(sqr.pos == position for sqr in self.squares)

    def bfs(self, s, e):
        q = [s]
        visited = {tuple(pos): False for pos in GRID}
        visited[s] = True
        prev = {tuple(pos): None for pos in GRID}

        while q:
            node = q.pop(0)
            for next_node in ADJACENCY_DICT[node]:
                if self.is_position_free(next_node) and not visited[tuple(next_node)]:
                    q.append(tuple(next_node))
                    visited[tuple(next_node)] = True
                    prev[tuple(next_node)] = node

        path = []
        p_node = e
        while prev[p_node] is not None:
            path.insert(0, p_node)
            p_node = prev[p_node]
            if p_node == s:
                return path
        return []

    def create_virtual_snake(self):
        v_snake = Snake(self.surface)
        for _ in range(len(self.squares) - len(v_snake.squares)):
            v_snake.add_square()
        for i, sqr in enumerate(v_snake.squares):
            sqr.pos = deepcopy(self.squares[i].pos)
            sqr.dir = deepcopy(self.squares[i].dir)
        v_snake.dir = deepcopy(self.dir)
        v_snake.turns = deepcopy(self.turns)
        v_snake.apple.pos = deepcopy(self.apple.pos)
        v_snake.apple.is_apple = True
        v_snake.is_virtual_snake = True
        return v_snake

    def get_path_to_tail(self):
        tail_pos = deepcopy(self.squares[-1].pos)
        self.squares.pop(-1)
        path = self.bfs(tuple(self.head.pos), tuple(tail_pos))
        self.add_square()
        return path

    def set_path(self):
        v_snake = self.create_virtual_snake()
        path_1 = v_snake.bfs(tuple(v_snake.head.pos), tuple(v_snake.apple.pos))
        path_2 = []
        if path_1:
            for pos in path_1:
                v_snake.go_to(pos)
                v_snake.move()
            v_snake.add_square()
            path_2 = v_snake.get_path_to_tail()
        if path_2:
            return path_1
        return self.get_path_to_tail() or []

    def update(self):
        self.handle_events()
        self.path = self.set_path()
        if self.path:
            self.go_to(self.path[0])
        self.draw()
        self.move()
        if self.score == SNAKE_MAX_LENGTH:
            self.won_game = True
            print("Snake won the game after", self.total_moves, "moves")
            pygame.time.wait(1000 * WAIT_SECONDS_AFTER_WIN)
            return 1
        self.total_moves += 1
        if self.hitting_self() or self.head.hitting_wall():
            print("Snake died, retrying...")
            self.reset()
        if self.moves_without_eating == MAX_MOVES_WITHOUT_EATING:
            print("Snake stuck, retrying...")
            self.reset()
        if self.eating_apple():
            self.add_square()
