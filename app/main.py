import sys
import app.utils as utils
from app.cmd_lib import CommandLibrary


def sanitize(m):
    # Escaped Quote Match Foundex
    if m.group(1):

        return f"{m.group(2)}{m.group(3)}{m.group(2)}"
    return m.group(6)


def main():
    cmd_lib = CommandLibrary()
    while True:
        sys.stdout.write("$ ")
        user_input = input().strip()

        # User Input Does Not Exist Case
        if not user_input:
            continue

        cmd, args = utils.sanitize(user_input)

        # Search Command Library for Correct Function To Use
        command_func = cmd_lib.find_command(cmd, user_input)
        command_func(args)
    pass


if __name__ == "__main__":
    main()
