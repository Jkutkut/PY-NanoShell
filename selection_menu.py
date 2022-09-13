# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    selection_menu.py                                  :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jre-gonz <jre-gonz@student.42madrid.com    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2022/09/11 22:51:00 by jre-gonz          #+#    #+#              #
#    Updated: 2022/09/13 11:25:42 by jre-gonz         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os,sys,tty,termios
import math
import json


class _Getch:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class SelectionMenu():
    # ******* KEYS AND COMBINATIONS *******
    # ctrl-c and ctrl-d
    EXIT_COMBINATIONS = [bytes.fromhex(c).decode('utf-8') for c in ['03', '04']]
    ENTER = bytes.fromhex('0d').decode('utf-8')
    BACKSPACE = bytes.fromhex('7f').decode('utf-8')
    DELETE = "\x1b\x5b\x33\x7e"
    TAB = "\x09"


    def __init__(self, options: list) -> None:
        self.__inkey = _Getch()
        self.running = True

        self.options = options
        self.noptions = len(options)

        self.index = 0

    def _get_input(self):
        while(1):
            k = self.__inkey()
            if ord(k[0]) == 0x1b:
                k = k + self.__inkey() + self.__inkey()
                if ord(k[2]) == 0x33: # DELETE key: 0x1b5b337e
                    k = k + self.__inkey()
            if k != '':
                return k
        return k

    def _hide_cursor(self):
        # https://stackoverflow.com/questions/5174810/how-to-turn-off-blinking-cursor-in-command-window#:~:text=Just%20use%20print('%5C033,%2C%20end%3D%22%22)%20.
        if os.name == 'nt':
            ci = _CursorInfo()
            handle = ctypes.windll.kernel32.GetStdHandle(-11)
            ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
            ci.visible = False
            ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
        elif os.name == 'posix':
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()

    def _show_cursor(self):
        if os.name == 'nt':
            ci = _CursorInfo()
            handle = ctypes.windll.kernel32.GetStdHandle(-11)
            ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
            ci.visible = True
            ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
        elif os.name == 'posix':
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

    def print(self, text: str, end: str = "\n"):
        '''
        Prints text on the screen.
        '''
        print(text, end=end)

    def _selected_input(self) -> str:
        pass

    def _hexify(self, s): # TODO DEBUG
        return [hex(ord(i)) for i in list(str(s))]

    def _update(self, first_time: bool = False) -> None:
        '''
        Updates the screen.
        '''
        if first_time:
            print("\r")
            for _ in range(self.noptions):
                print(f"\033[A", end="")
        for o in options:
            print(f" - {o}")

    def run(self) -> None:
        '''
        Handles the input of the user.
        '''
        os.system("clear")
        self._hide_cursor()
        while self.running:
            self._update()
            k = self._get_input()

            # ******* KEYS / COMBIANTIONS *******
            if k in self.EXIT_COMBINATIONS:
                self.running = False
            elif k == self.ENTER:
                pass
            elif k == self.ENTER:
                return self._selected_input()
                # self.running = False
            # ******* ARROW KEYS *******
            elif k == '\x1b[A': # up
                self.index = (self.index - 1)
                if self.index < 0:
                    self.index = self.noptions - 1
            elif k == '\x1b[B': # down (History system)
                self.index = (self.index + 1) % self.noptions
            elif k == '\x1b[D': # Left key
                return self._selected_input()
            elif k == '\x1b[C': # Right key
                pass

            else:
                if self.__debug:
                    self.print(f"\n{self._hexify(k)}") # TODO debug
        self._show_cursor()

if __name__ == "__main__":
    options = [
        "Option 1",
        "Option 2",
        "Option 3",
        "Option 4",
        "Option 5",
        "Option 6",
    ]
    sm = SelectionMenu(options)
    sm.run()