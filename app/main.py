import sys
import re
from app.cmd_lib import CommandLibrary


def main():
    cmd_lib = CommandLibrary()
    while True:
        sys.stdout.write("$ ")
        user_input = input()

        # Santize User Input (Splitting by Whitespace Outside Single Quotes)
        cmd_line = re.split(r"""\s+(?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", user_input)

        # User Input Does Not Exist Case
        if not cmd_line:
            continue

        cmd, *args = cmd_line
        # Removes Top-Most Quotes:  "'hello'"'"world"'  -> 'hello'"world"
        args = [re.sub(r"(\\'|\"|')(.*?)\1", r"\2", arg) for arg in args]

        # Search Command Library for Correct Function To Use
        command_func = cmd_lib.find_command(cmd, user_input)
        command_func(args)
    pass


if __name__ == "__main__":
    main()
