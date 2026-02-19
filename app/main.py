import sys
import os
from pathlib import Path
from app.cmd_lib import CommandLibrary


def main():

    cmd_lib = CommandLibrary()
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        cmd_line = user_input.split()

        # User Input Does Not Exist Case
        if not cmd_line:
            continue

        cmd, *args = cmd_line

        # Search Command Library for Correct Function To Use
        command_func = cmd_lib.find_command(cmd, user_input)
        command_func(args)
    pass


if __name__ == "__main__":
    main()
