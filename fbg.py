#!/usr/bin/env python3

import random
from copy import deepcopy
import datetime
import sys
import curses
import time


colors = {
    'I': 1,
    'O': 2,
    'T': 3,
    'J': 4,
    'L': 5,
    'S': 6,
    'Z': 7,
    'G': 8,
    'X': 10,
    }


pieces = {
    'I': [
        [' ', 'I', ' ', ' '],
        [' ', 'I', ' ', ' '],
        [' ', 'I', ' ', ' '],
        [' ', 'I', ' ', ' ']],
    'O': [
        ['O', 'O'],
        ['O', 'O']],
    'T': [
        [' ', ' ', ' '],
        ['T', 'T', 'T'],
        [' ', 'T', ' ']],
    'J': [
        [' ', ' ', ' '],
        ['J', 'J', 'J'],
        [' ', ' ', 'J']],
    'L': [
        [' ', ' ', ' '],
        ['L', 'L', 'L'],
        ['L', ' ', ' ']],
    'S': [
        [' ', ' ', ' '],
        [' ', 'S', 'S'],
        ['S', 'S', ' ']],
    'Z': [
        [' ', ' ', ' '],
        ['Z', 'Z', ' '],
        [' ', 'Z', 'Z']],
    }


def is_collision(board, piece, x, y):
    for py in range(len(piece)):
        by = py + y
        for px in range(len(piece[py])):
            bx = px + x
            if piece[py][px] != ' ':
                if by < 0 or by >= len(board):
                    return True
                if bx < 0 or bx >= len(board[by]):
                    return True
                if board[by][bx] != ' ':
                    return True
    return False


def merge_piece(board, piece, x, y):
    new_board = deepcopy(board)
    for py in range(len(piece)):
        by = py + y
        for px in range(len(piece[py])):
            bx = px + x
            if piece[py][px] != ' ':
                new_board[by][bx] = piece[py][px]
    return new_board


def rotate_left(piece):
    return [[piece[x][y] for x in range(len(piece[y])-1, -1, -1)] for y in range(len(piece))]


def rotate_right(piece):
    return rotate_left(rotate_left(rotate_left(piece)))


def handle_scores(board):
    uncleared = [deepcopy(row) for row in board if not all(block != ' ' for block in row)]
    lines = len(board) - len(uncleared)
    new_board = [[' ' for x in range(len(board[y]))] for y in range(lines)] + uncleared
    return lines, new_board


def add_pending_lines(board, lines, gap_x):
    overflow = False
    new_board = [[b for b in board[y]] for y in range(lines, len(board))]
    new_board.extend([['X' if x != gap_x else ' ' for x in range(len(board[0]))] for y in range(lines)])
    overflow = any(b != ' ' for y in range(0, lines) for b in board[y])
    return overflow, new_board



def draw_blocks(scr, blocks, oy, ox):
    for y in range(len(blocks)):
        for x in range(len(blocks[y])):
            if blocks[y][x] != ' ':
                color = colors[blocks[y][x]]
                scr.addstr(oy+y, ox+2*x, '[]', curses.color_pair(color))


class FallingBlockGame:

    WIDTH = 12
    HEIGHT = 24

    def __init__(self):
        self.board = [[' ' for x in range(self.WIDTH)] for y in range(self.HEIGHT)]
        self.scores = {1: 0, 2: 0, 3: 0, 4: 0}
        self.next_piece = random.choice(list(pieces.keys()))
        self.set_next_piece()
        self.game_over = False
        self.pending_scores = []
        self.pending_lines = 0
        self.gap_x = random.randrange(0, self.WIDTH)

    def set_next_piece(self):
        self.piece_name = self.next_piece
        self.next_piece = random.choice(list(pieces.keys()))
        self.piece = deepcopy(pieces[self.piece_name])
        self.x = self.WIDTH//2 - len(self.piece[0])//2
        self.y = 0

    def draw_next_piece(self, scr, oy, ox):
        scr.addstr(oy, ox, 'Next piece: {}'.format(self.next_piece))
        draw_blocks(scr, pieces[self.next_piece], oy+1, ox)

    def draw_score(self, scr, oy, ox):
        scr.addstr(oy, ox, 'Score: {}'.format(str(self.scores)))

    def draw_border(self, scr, oy, ox):
        scr.addstr(oy, ox, '*'*(2*self.WIDTH+2))
        scr.addstr(oy + self.HEIGHT+1, ox, '*'*(2*self.WIDTH+2))
        for y in range(1, self.HEIGHT+1):
            scr.addstr(oy + y, ox, '*')
            scr.addstr(oy + y, ox + 2*self.WIDTH+1, '*')

    def draw_ghost_piece(self, scr, oy, ox):
        ghost_piece = [['G' if block != ' ' else ' ' for block in row] for row in self.piece]
        gx = self.x
        gy = self.y
        while not is_collision(self.board, ghost_piece, gx, gy+1):
            gy += 1
        draw_blocks(scr, ghost_piece, oy + gy, ox + 2*gx)

    def draw_board(self, scr, oy, ox):
        draw_blocks(scr, self.board, oy, ox)
        self.draw_ghost_piece(scr, oy, ox)
        draw_blocks(scr, self.piece, oy + self.y, ox + 2*self.x)

    def draw(self, scr, oy, ox):
        self.draw_board(scr, oy + 1, ox + 1)
        self.draw_border(scr, oy + 0, ox + 0)
        self.draw_next_piece(scr, oy + 1, ox + 2*self.WIDTH+4)
        self.draw_score(scr, oy + self.HEIGHT+2, ox + 0)

    def fall(self):
        if is_collision(self.board, self.piece, self.x, self.y+1):
            self.board = merge_piece(self.board, self.piece, self.x, self.y)
            lines, self.board = handle_scores(self.board)
            if lines:
                self.scores[lines] += 1
                self.pending_scores.append(lines)
            overflow = self.add_pending_lines()
            if overflow:
                self.game_over = True
            self.set_next_piece()
            if is_collision(self.board, self.piece, self.x, self.y):
                self.game_over = True
        else:
            self.y += 1

    def add_pending_lines(self):
        if self.pending_lines:
            overflow, self.board = add_pending_lines(self.board, self.pending_lines, self.gap_x)
            self.pending_lines = 0
            return overflow
        return False


    def move(self, dx, dy):
        if not is_collision(self.board, self.piece, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def rotate_left(self):
        new_piece = rotate_left(self.piece)
        if not is_collision(self.board, new_piece, self.x, self.y):
            self.piece = new_piece

    def rotate_right(self):
        new_piece = rotate_right(self.piece)
        if not is_collision(self.board, new_piece, self.x, self.y):
            self.piece = new_piece

    def drop(self):
        while not is_collision(self.board, self.piece, self.x, self.y+1):
            self.y += 1

    def get_pending_scores(self):
        ret = self.pending_scores.copy()
        self.pending_scores.clear()
        return ret

   
def main(stdscr):
    stdscr.nodelay(1)
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, 16):
        curses.init_pair(i, 0, i)

    game = FallingBlockGame()
    game2 = FallingBlockGame()

    FALL_DELAY = datetime.timedelta(microseconds=250000)
    fall_time = datetime.datetime.now() + FALL_DELAY

    while True:
        redraw = False
        time.sleep(0.01)
        c = stdscr.getch()
        if c != -1:
            cmd = chr(c)
            if cmd == 'a':
                game.move(-1, 0)
            elif cmd == 'j':
                game2.move(-1, 0)
            elif cmd == 'd':
                game.move(1, 0)
            elif cmd == 'l':
                game2.move(1, 0)
            elif cmd == 's':
                game.move(0, 1)
            elif cmd == 'k':
                game2.move(0, 1)
            elif cmd == 'w':
                game.drop()
            elif cmd == 'i':
                game2.drop()
            elif cmd == 'q':
                game.rotate_left()
            elif cmd == 'u':
                game2.rotate_left()
            elif cmd == 'e':
                game.rotate_right()
            elif cmd == 'o':
                game2.rotate_right()
            redraw = True
        if datetime.datetime.now() > fall_time:
            game.fall()
            game2.fall()
            fall_time = datetime.datetime.now() + FALL_DELAY
            redraw = True
        for pending_score in game.get_pending_scores():
            game2.pending_lines += max(pending_score-1, 0)
        for pending_score in game2.get_pending_scores():
            game.pending_lines += max(pending_score-1, 0)
        if redraw:
            stdscr.clear()
            game.draw(stdscr, 0, 0)
            game2.draw(stdscr, 0, 50)
            stdscr.refresh()
        if game.game_over:
            stdscr.addstr(10, 10, 'Game over!')
            stdscr.refresh()
            time.sleep(3)
            return
        if game2.game_over:
            stdscr.addstr(10, 60, 'Game over!')
            stdscr.refresh()
            time.sleep(3)
            return


if __name__ == '__main__':
    curses.wrapper(main)
