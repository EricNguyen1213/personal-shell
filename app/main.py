import sys


def not_found(cmd_line):
    return lambda _: print(f"{cmd_line}: command not found")


def handle_exit(_):
    return sys.exit(0)


def handle_echo(args):
    return print(" ".join(args))


command_lib = {"exit": handle_exit, "echo": handle_echo}


def main():

    while True:
        sys.stdout.write("$ ")
        user_input = input()
        cmd_line = user_input.split()

        if not cmd_line:
            continue

        cmd, *args = cmd_line

        command_func = command_lib.get(cmd, not_found(user_input))
        command_func(args)

    pass


if __name__ == "__main__":
    main()
