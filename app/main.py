import sys
import os
from pathlib import Path
import subprocess


def find_which_path(fn):
    # Construct And Check Validity of Path to Possible File Input
    paths = os.getenv("PATH", "").split(os.pathsep)
    valid_file_path = next(
        (
            file_path
            for file_path in (Path(f"{path}/{fn}") for path in paths)
            if file_path.exists()
            and file_path.is_file()
            and os.access(file_path, os.X_OK)
        ),
        None,
    )
    return valid_file_path


def not_found(user_input):
    return lambda _: print(f"{user_input}: command not found")


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

        found_file_path = find_which_path(arg)
        if found_file_path:
            print(f"{arg} is {found_file_path}")
        else:
            print(f"{arg} not found")


def handle_custom_exec(cmd_line, user_input):
    file_path = find_which_path(cmd_line[0])
    if file_path:
        return lambda _: subprocess.run(cmd_line)
    return not_found(user_input)


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
        command_func = command_lib.get(cmd, None)

        # Non Built In Case
        if not command_func:
            command_func = handle_custom_exec(cmd_line, user_input)

        command_func(args)
    pass


if __name__ == "__main__":
    main()
