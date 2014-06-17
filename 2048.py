import random
import os
import curses
import getopt
import sys

class board:

    def __init__(self, stdscr, num_rows = 4, num_cols = 4):
        self.stdscr = stdscr
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.score = 0

        self.tiles = [tile(row, col) for row in range(num_rows) for col in range(num_cols)]

        start_tiles = min(num_rows, num_cols)

        for i in range(start_tiles):
            self.add_tile()

    def copy(self):
        new = board(None, self.num_rows, self.num_cols)
        new.tiles = [t.copy() for t in self.tiles]
        return new

    def add_tile(self, value = 2):
        empty = self.get_empty_tiles()
        empty[int(random.random() * 1000) % len(empty)].set_value(value)

    def get_tile(self, row, col):
        if (row < 0 or row >= self.num_rows or col < 0 or col >= self.num_cols):
            return None
        return self.tiles[row * self.num_cols + col]

    def set_tile(self, row, col, tile):
        self.tiles[row * self.num_cols + col] = tile

    def get_empty_tiles(self):
        return [t for t in self.tiles if t.value == 0]

    def height(self):
        height, width = self.tiles[0].dimensions()
        return self.num_rows * height

    def check_lose(self):
        empty = self.get_empty_tiles()
        if (len(empty) > 0):
            return False

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                cur = self.get_tile(row, col).value

                down = self.get_tile(row - 1, col)
                up = self.get_tile(row + 1, col)
                left = self.get_tile(row, col - 1)
                right = self.get_tile(row, col + 1)

                if (down and down.value == cur):
                    return False
                if (up and up.value == cur):
                    return False
                if (left and left.value == cur):
                    return False
                if (right and right.value == cur):
                    return False
        return True

    def move_left(self):
        num_moves = 0
        for row in range(self.num_rows):
            left_tile = self.get_tile(row, 0)
            merged = False

            for col in range(1, self.num_cols):
                cur_tile = self.get_tile(row, col)

                (left_tile, moved, merged) = self.move(left_tile, cur_tile, merged)
                if (moved):
                    num_moves += 1
        return num_moves

    def move_right(self):
        num_moves = 0
        for row in range(self.num_rows):
            right_tile = self.get_tile(row, self.num_cols - 1)
            merged = False

            for col in reversed(range(self.num_cols - 1)):
                cur_tile = self.get_tile(row, col)

                (right_tile, moved, merged) = self.move(right_tile, cur_tile, merged)
                if (moved):
                    num_moves += 1
        return num_moves

    def move_up(self):
        num_moves = 0
        for col in range(self.num_cols):
            up_tile = self.get_tile(0, col)
            merged = False

            for row in range(1, self.num_rows):
                cur_tile = self.get_tile(row, col)

                (up_tile, moved, merged) = self.move(up_tile, cur_tile, merged)
                if (moved):
                    num_moves += 1
        return num_moves


    def move_down(self):
        num_moves = 0
        for col in range(self.num_cols):
            down_tile = self.get_tile(self.num_rows - 1, col)
            merged = False

            for row in reversed(range(self.num_rows - 1)):
                cur_tile = self.get_tile(row, col)

                (down_tile, moved, merged) = self.move(down_tile, cur_tile, merged)
                if (moved):
                    num_moves += 1
        return num_moves


    def move(self, nearest_tile, cur_tile, merged):
        if (cur_tile.value == 0):
            return (nearest_tile, False, merged)

        if (nearest_tile.row == cur_tile.row):
            dist = nearest_tile.col - cur_tile.col
            new_idx = nearest_tile.col + 1 if dist < 0 else nearest_tile.col - 1
            next_tile = self.get_tile(nearest_tile.row, new_idx)

        else:
            dist = nearest_tile.row - cur_tile.row
            new_idx = nearest_tile.row + 1 if dist < 0 else nearest_tile.row - 1
            next_tile = self.get_tile(new_idx, nearest_tile.col)

        if (cur_tile.value == nearest_tile.value and not merged):
            nearest_tile.double()
            cur_tile.reset()
            cur_tile = nearest_tile
            moved = True
            merged = True
            self.score += cur_tile.value

        elif (nearest_tile.value == 0):
            nearest_tile.set_value(cur_tile.value)
            cur_tile.reset()
            cur_tile = nearest_tile
            moved = True
            merged = False

        elif (abs(dist) > 1):
            next_tile.set_value(cur_tile.value)
            cur_tile.reset()
            cur_tile = next_tile
            moved = True
            merged = False

        else:
            moved = False
            merged = False

        nearest_tile = cur_tile

        return (cur_tile, moved, merged)


    def render(self):
        for row in range(self.num_rows):
            row_tiles = []
            for col in range(self.num_cols):
                row_tiles.append(self.get_tile(row, col).render())

            for i in range(len(row_tiles[0])):
                self.stdscr.move(row * len(row_tiles[0]) + i, 0)
                cur_row = [t[i] for t in row_tiles]
                self.stdscr.addstr(' '.join(cur_row))

        self.stdscr.addstr(self.height(), 0, "Score: " + str(self.score))





class tile:

    def __init__(self, row, col, value = 0):
        self.row = row
        self.col = col
        self.value = value

    def copy(self):
        return tile(self.row, self.col, self.value)

    def dimensions(self):
        height = len(self.render())
        width = len(self.render()[0])
        return (height, width)

    def set_value(self, value):
        self.value = value

    def double(self):
        self.value *= 2

    def reset(self):
        self.value = 0

    def render(self):
        return ["+-------------+",
                "|             |",
                "|             |",
                self.num_line(),
                "|             |",
                "|             |",
                "+-------------+"]

    def num_line(self):
        num_length = len(str(self.value))
        left_spaces = round((13 - num_length) / 2)
        right_spaces = 13 - num_length - left_spaces

        line = "|"

        for i in range(left_spaces):
            line += " "

        line += str(self.value) if self.value > 0 else ' '

        for i in range(right_spaces):
            line += " "

        line += "|"

        return line


def new_game(stdscr, rows = 4, cols = 4):
    b = board(stdscr, rows, cols)
    b.render()
    
    while True:
        num_moves = 0
        key = stdscr.getkey()
        if key == 'KEY_UP':
            num_moves = b.move_up()
        elif key == 'KEY_DOWN':
            num_moves = b.move_down()
        elif key == 'KEY_LEFT':
            num_moves = b.move_left()
        elif key == 'KEY_RIGHT':
            num_moves = b.move_right()
    
        if (num_moves > 0):
            b.add_tile()
            b.render()
            if (b.check_lose()):
                break

    stdscr.addstr(b.height() + 1, 0, "Game Over. Play again? (Y/N)")
    key = 0
    while (key != 'Y' and key != 'N'):
        key = stdscr.getkey()

    stdscr.clear()

    if (key == 'Y'):
        new_game(stdscr)

if (__name__ == '__main__'):
    rows = 4
    cols = 4
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:c:")
    except getopt.GetoptError:
        print('2048.py -r <rows> -c <cols>')
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-r':
            rows = int(arg)
        elif opt == '-c':
            cols = int(arg)

    curses.wrapper(new_game, rows, cols)
    
