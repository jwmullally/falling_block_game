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
    }


pieces = {
    'I': [
        [' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' '],
        ['I', 'I', 'I', 'I'],
        [' ', ' ', ' ', ' ']],
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




class BlockBoard:

    WIDTH = 12
    HEIGHT = 24

    def __init__(self):
        self.board = [[' ' for x in range(self.WIDTH)] for y in range(self.HEIGHT)]
        self.scores = {1: 0, 2: 0, 3: 0, 4: 0}
        self.next_piece = random.choice(list(pieces.keys()))
        self.get_next_piece()

    def get_next_piece(self):
        self.piece_name = self.next_piece
        self.next_piece = random.choice(list(pieces.keys()))
        self.piece = deepcopy(pieces[self.piece_name])
        self.x = self.WIDTH//2 - len(self.piece[0])//2
        self.y = 0

    def draw_border(self, scr):
        scr.addstr(0, 0, '*'*(2*self.WIDTH+2))
        scr.addstr(self.HEIGHT+1, 0, '*'*(2*self.WIDTH+2))
        for y in range(1, self.HEIGHT+1):
            scr.addstr(y, 0, '*')
            scr.addstr(y, self.WIDTH*2+1, '*')
        scr.addstr(self.HEIGHT+3, 0, 'Score: {}'.format(str(self.scores)))

    def draw(self, scr):
        for y in range(self.HEIGHT):
            py = y - self.y
            for x in range(self.WIDTH):
                px = x - self.x
                if py >= 0 and py < len(self.piece) and px >= 0 and px < len(self.piece[py]) and self.piece[py][px] != ' ':
                    block = self.piece[py][px]
                else:
                    block = self.board[y][x]
                if block != ' ':
                    color = colors[block]
                    scr.addstr(y+1, x*2+1, '[]', curses.color_pair(color))
        self.draw_border(scr)
        return

    def fall(self):
        if is_collision(self.board, self.piece, self.x, self.y+1):
            self.board = merge_piece(self.board, self.piece, self.x, self.y)
            lines, self.board = handle_scores(self.board)
            if lines:
                self.scores[lines] += 1
            self.get_next_piece()
            return True
        else:
            self.y += 1
            return False

    def move(self, dx, dy):
        if not is_collision(self.board, self.piece, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def rotate_left(self):
        self.piece = rotate_left(self.piece)

    def rotate_right(self):
        self.piece = rotate_right(self.piece)

    def drop(self):
        while not is_collision(self.board, self.piece, self.x, self.y+1):
            self.fall()

   
def main(stdscr):
    stdscr.nodelay(1)
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, 8):
        curses.init_pair(i, 0, i)

    game = BlockBoard()

    FALL_DELAY = 250000 # microseconds

    fall_time = datetime.datetime.now() + datetime.timedelta(microseconds=FALL_DELAY)

    while True:
        redraw = False
        time.sleep(0.01)
        c = stdscr.getch()
        if c != -1:
            cmd = chr(c)
            if cmd == 'a':
                game.move(-1, 0)
            elif cmd == 'd':
                game.move(1, 0)
            elif cmd == 's':
                game.move(0, 1)
            elif cmd == 'w':
                game.drop()
                fall_time = datetime.datetime.now() + datetime.timedelta(microseconds=FALL_DELAY)
            elif cmd == 'z':
                game.rotate_left()
            elif cmd == 'x':
                game.rotate_right()
            elif cmd == 'p':
                return
            redraw = True
        if datetime.datetime.now() > fall_time:
            game.fall()
            fall_time = datetime.datetime.now() + datetime.timedelta(microseconds=FALL_DELAY)
            redraw = True
        if redraw:
            stdscr.clear()
            game.draw(stdscr)
            stdscr.refresh()

if __name__ == '__main__':
    curses.wrapper(main)
