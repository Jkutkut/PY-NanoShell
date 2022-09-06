from nanoshell import NanoShell

# ******* CONSTANTS *******
BLUE = "\033[38;5;33m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"

class MyShell(NanoShell):

    CMDS = NanoShell.CMDS | {
        "AA": ["aa"],
    }

    FLAGS = NanoShell.FLAGS | {
        # AA
        "AA_FLAG": "-h"
    }

    USAGE = NanoShell.USAGE | {
        "AA": f"<n> [{FLAGS['AA_FLAG']}]"
    }

    DESCRIPTION = NanoShell.DESCRIPTION | {
        "AA": "This is an example command to show how to implement a new command."
    }

    def __init__(self, debug: bool = False):
        super().__init__(debug = debug)

    def _handle_cmd(self, cmd: list) -> bool:
        if super()._handle_cmd(cmd):
            return True
        elif cmd[0] in self.CMDS['AA']:
            self.aa(cmd)
        else:
            return False
        return True

    # ******* COMMANDS LOGIC *******
    def aa(self, cmd: list):
        if len(cmd) == 1 or len(cmd) > 3:
            return self._usage(cmd)
        if len(cmd) == 3:
            if cmd[2] == self.FLAGS['AA_FLAG']:
                self.print("The flag is present")
            else:
                return self._usage(cmd)
        if cmd[1].isdigit():
            self.print("The argument is a number")
        else:
            self.print("The argument is not a number")


    # ******* NANOSHELL LOGIC *******
    def _title(self):
        return f"""{NC}
███    ███
████  ████
██ ████ ██
██  ██  ██
██      ██
{NC}
"""

if __name__=='__main__':
    m = MyShell(debug=False)
    m.run()
