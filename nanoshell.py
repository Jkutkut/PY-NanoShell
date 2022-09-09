# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    nanoshell.py                                       :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jre-gonz <jre-gonz@student.42madrid.com    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2022/08/24 07:53:46 by jre-gonz          #+#    #+#              #
#    Updated: 2022/09/09 18:45:13 by jre-gonz         ###   ########.fr        #
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

# ******* CONSTANTS *******
BLUE = "\033[38;5;33m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"

class NanoShell:
    CMDS = {
        "EXIT": ["exit", "quit", "q"],
        "CLEAR": ["clear", "cls"],
        "HISTORY": ["history", "h"],
        "HISTORY_CLEAR": ["history_clear", "hc"],
        "HELP": ["help"]
    }

    FLAGS = {
    }

    USAGE = {
        "EXIT": "",
        "CLEAR": "",
        "HISTORY": "",
        "HISTORY_CLEAR": "",
        "HELP": ""
    }

    DESCRIPTION = {
        "EXIT": "Exit the shell.",
        "CLEAR": "Clear the screen.",
        "HISTORY": "Show the history of commands.",
        "HISTORY_CLEAR": "Clear the history of commands and removes the log file.",
        "HELP": "Show the help menu."
    }

    SHELL_PROMPT = f"{BLUE}$> {NC}"
    CNF = f"{RED}Command not found{NC}. Maybe with the {YELLOW}{CMDS['HELP'][0]}{NC} command..."
    END_MSG = "Exiting shell"
    LOG_FILE = ".log.log"

    # ******* KEYS AND COMBINATIONS *******
    # ctrl-c and ctrl-d
    EXIT_COMBINATIONS = [bytes.fromhex(c).decode('utf-8') for c in ['03', '04']]
    ENTER = bytes.fromhex('0d').decode('utf-8')
    BACKSPACE = bytes.fromhex('7f').decode('utf-8')
    DELETE = "\x1b\x5b\x33\x7e"
    TAB = "\x09"

    # ******* CONSTRUCTOR *******
    def __init__(self, debug: bool = False):
        self.__debug = debug

        self.__inkey = _Getch()
        self.text = ""
        self.koffset = 0
        self.running = True
        self.hist_idx = 0
        self.history = []

    # ******* COMMANDS LOGIC *******
    def _history(self, cmd: list) -> None:
        '''
        Prints the current history of commands
        '''
        result = f"{YELLOW}\nHistory:{NC}\n"
        i = 0
        digits = int(math.log10(len(self.history)))+1
        for c in self.history:
            result = f"{result}\n{i}  {c}"
            i = i + 1
        self.print(result, end="\n\n")

    def _history_clear(self, cmd: list) -> None:
        '''
        Clears the history of commands and removes the log file.
        '''
        self.history = []
        self.hist_idx = 0
        os.remove(self.LOG_FILE)
        self.print("\nHistory cleared.\n")

    def _help(self, cmd: list) -> None:
        '''
        Shows the list of commands avalible to use.
        '''
        for c in self.CMDS:
            self._usage(self.CMDS[c], description=True)


    # ******* NANOSHELL LOGIC *******
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

    def _hexify(self, s): # TODO DEBUG
        return [hex(ord(i)) for i in list(str(s))]

    def _execute_cmd(self) -> None:
        '''
        Responsable of the execution of the command.
        Also adds the command to the history and executes it.
        If the command is not valid, it prints the usage.
        '''
        self.history.append(self.text) # Add cmd to history
        self.print()
        if self.__debug:
            self.print(f"-->'{self.text}'")
        c = self.text.strip().split(" ")
        try:
            if not self._handle_cmd(c):
                self.print(self.CNF)
        except Exception as e:
            self.print("\n" + str(e))

    def _handle_cmd(self, cmd: list) -> bool:
        '''
        Takes the command inputed and attempts to execute it.
        Returns True if command found. Else, False.
        '''
        self._log(f"{self.SHELL_PROMPT}{' '.join(cmd)}")

        if cmd[0] in self.CMDS['EXIT']:
            self.running = False
        elif cmd[0] in self.CMDS['CLEAR']:
            os.system("clear")
        elif cmd[0] in self.CMDS['HISTORY']:
            self._history(cmd)
        elif cmd[0] in self.CMDS['HISTORY_CLEAR']:
            self._history_clear(cmd)
        elif cmd[0] in self.CMDS['HELP']:
            self._help(cmd)
        else:
            return False
        return True

    def _usage(self, cmd: list, description: bool = False) -> None:
        '''
        Prints the usage of the given command.
        '''
        og_cmd = None
        for c in self.CMDS:
            if cmd[0] in self.CMDS[c]:
                og_cmd = c
                break
        if og_cmd is None:
            raise Exception(f"Command not found")
        usage = f"{YELLOW}{self.CMDS[og_cmd][0]}{NC}\n"
        if description:
            usage = f"{usage}  {self.DESCRIPTION[og_cmd]}\n"
            usage = f"{usage}  Aliases: {', '.join(self.CMDS[og_cmd])}\n\n"
        usage = f"{usage}  {self.SHELL_PROMPT}{self.CMDS[og_cmd][0]} {self.USAGE[og_cmd]}\n"
        self.print(usage)

    def _update(self) -> None:
        '''
        Updates the user's input.
        '''
        print(f"\33[2K\r{self.SHELL_PROMPT}" + self.text +\
            "".join(['\033[D' for _ in range(self.koffset)]),\
            end="")

    def print(self, content = "", end="\n") -> None:
        '''
        Prints the given content to the screen.
        Also adds the content to the log file.
        '''
        self._log(content, end)
        print(content, end=end)

    def _log(self, content: str, end: str = "") -> None:
        '''
        Logs the given text to the log file.
        '''
        f = open(self.LOG_FILE, "a")
        f.write(content if type(content) is str else json.dumps(content))
        f.write(end)
        f.close()

    def _handle_tab(self):
        current_pos = len(self.text) - self.koffset - 1
        if self.koffset > 0 and self.text[current_pos + 1] != " ":
            # Check not in middle of cmd-flag
            return
        cmd = self.text.split(' ')
        i = 0
        cmd_index = 0
        while i <= current_pos:
            if self.text[i] == " ":
                cmd_index = cmd_index + 1
            i = i + 1

        if cmd_index == 0: # Autocomplete cmd
            available = []
            for command in self.CMDS:
                for alias in self.CMDS[command]:
                    if alias.startswith(cmd[0]):
                        available.append(alias)
        else: # Autocomplete flag
            c = None
            for command in self.CMDS:
                if cmd[0] in self.CMDS[command]:
                    c = command
                    break
            if c == None: # If invalid command
                return
            available = []
            for flag in self.FLAGS:
                if c in flag:
                    if type(self.FLAGS[flag]) == str:
                        if cmd[cmd_index] == '' or self.FLAGS[flag].startswith(cmd[cmd_index]):
                            available.append(self.FLAGS[flag])
                    else:
                        for f in self.FLAGS[flag]:
                            if cmd[cmd_index] == '' or f.startswith(cmd[cmd_index]):
                                available.append(f)
        if len(available) == 0:
            return
        elif len(available) == 1:
            cmd[cmd_index] = available[0]
            self.text = " ".join(cmd)
        else:
            print(f"\n{' '.join(available)}")
            # Note: all available elements are longer than cmd[cmd_index]
            i = len(cmd[cmd_index])
            while all([i < len(e) and i < len(available[0]) and available[0][i] == e[i] for e in available]):
                i = i + 1
            cmd[cmd_index] = available[0][:i]
            self.text = " ".join(cmd)


    def run(self) -> None:
        '''
        Handles the input of the user.
        '''
        os.system("clear")
        self.print(self._title(), end="")
        while self.running:
            self._update()
            k = self._get_input()

            # ******* KEYS / COMBIANTIONS *******
            if k in self.EXIT_COMBINATIONS:
                self.running = False
            elif k == self.DELETE:
                if self.koffset == 0 or len(self.text) == 0:
                    continue
                current_pos = len(self.text) - self.koffset
                self.text = self.text = self.text[:current_pos] + self.text[current_pos + 1:]
                self.koffset = self.koffset - 1
            elif k == self.BACKSPACE:
                if len(self.text) == 0 or len(self.text) - self.koffset <= 0:
                    continue
                current_pos = len(self.text) - self.koffset
                self.text = self.text[:current_pos - 1] + self.text[current_pos:]
            elif k == self.ENTER:
                self._execute_cmd()
                self.text = ""
                self.koffset = 0
                self.hist_idx = 0
            elif k == self.TAB:
                self._handle_tab()

            # ******* ARROW KEYS *******
            elif k in ['\x1b[A', '\x1b[B']: # Up or down (History system)
                if k == '\x1b[A':
                    if len(self.history) > self.hist_idx:
                        self.hist_idx = self.hist_idx + 1
                else:
                    if self.hist_idx > 0:
                        self.hist_idx = self.hist_idx - 1
                self.text = self.history[-self.hist_idx] if self.hist_idx != 0 else ""
                pass
            elif k == '\x1b[D': # Left key
                if len(self.text) - self.koffset > 0: # If left and not on the begging
                    self.koffset = self.koffset + 1
            elif k == '\x1b[C': # Right key
                if self.koffset > 0: # If right and to on the end
                    self.koffset = self.koffset - 1

            # ******* Ascii input *******
            elif (len(k) == 1 and ord(k) >= 32 and ord(k) < 127):
                if self.koffset == 0:
                    self.text = self.text + k
                else:
                    current_pos = len(self.text) - self.koffset
                    self.text = self.text[:current_pos] + k + self.text[current_pos:]

            else:
                if self.__debug:
                    self.print(f"\n{self._hexify(k)}") # TODO debug
        self.print(self.END_MSG)

    def _title(self) -> str:
        '''
        Returns the title of the shell.
        '''
        return ""

if __name__=='__main__':
    m = NanoShell(debug=False)
    m.run()

