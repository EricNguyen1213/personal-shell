import sys
import os
from pathlib import Path


def not_found(cmd_line):
    return lambda _: print(f"{cmd_line}: command not found")


# exit command case
def handle_exit(_):
    return sys.exit(0)


# echo command case
def handle_echo(args):
    return print(" ".join(args))


# type command case
def handle_type(args):
    for arg in args:
        # Argument is Actual Command
        if arg in command_lib:
            print(f"{arg} is a shell builtin")
            continue

        # Construct Path to Possible File Input
        file_paths = [
            Path(f"{path}/{arg}") for path in os.getenv("PATH").split(os.pathsep)
        ]

        # Checks if File Exists or Is Executable
        found_file_path = next(
            (
                file_path
                for file_path in file_paths
                if file_path.exists()
                and file_path.is_file()
                and os.access(file_path, os.X_OK)
            ),
            None,
        )
        if found_file_path:
            print(f"{arg} is {found_file_path}")
        else:
            print(f"{arg} not found")


command_lib = {"exit": handle_exit, "echo": handle_echo, "type": handle_type}


def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        cmd_line = user_input.split()

        # User Input Does Not Exist Case
        if not cmd_line:
            continue

        cmd, *args = cmd_line

        # Search Command Library for Correct Function To Use
        command_func = command_lib.get(cmd, not_found(user_input))
        command_func(args)

    pass


if __name__ == "__main__":
    main()
