import sys
import os
import subprocess
from pathlib import Path


def find_which_path(fn):
    # Construct And Check Validity of Path to Possible File Input
    paths = os.getenv("PATH", "").split(os.pathsep)
    valid_file_path = next(
        (
            file_path
            for file_path in (Path(path) / fn for path in paths)
            if file_path.exists()
            and file_path.is_file()
            and os.access(file_path, os.X_OK)
        ),
        None,
    )
    return valid_file_path


class CommandLibrary:
    def __init__(self):
        self.command_lib = {
            "exit": self.handle_exit,
            "echo": self.handle_echo,
            "type": self.handle_type,
            "pwd": self.handle_pwd,
            "cd": self.handle_cd,
        }

    def find_command(self, cmd, user_input):
        command_func = self.command_lib.get(cmd, None)
        if command_func:
            return command_func

        file_path = find_which_path(cmd)
        if file_path:
            return self.handle_custom_exec(cmd)

        return self.not_found(user_input)

    # Command Not Found Case
    def not_found(self, user_input):
        return lambda _: print(f"{user_input}: command not found")

    # exit Command case
    def handle_exit(self, _):
        return sys.exit(0)

    # echo Command Case
    def handle_echo(self, args):
        return print(" ".join(args))

    # type Command Case
    def handle_type(self, args):
        for arg in args:
            # Argument is Actual Command
            if arg in self.command_lib:
                print(f"{arg} is a shell builtin")
                continue

            found_file_path = find_which_path(arg)
            if found_file_path:
                print(f"{arg} is {found_file_path}")
            else:
                print(f"{arg} not found")

    # pwd Case
    def handle_pwd(self, _):
        return print(os.getcwd())

    # Custom Or Not Found Exec Case
    def handle_custom_exec(self, cmd):
        return lambda args: subprocess.run([cmd, *args])

    # cd case
    def handle_cd(self, args):
        if len(args) > 1:
            print("cd: too many arguments")

        path_input = "~" if not args else args[0]
        cd_path = Path(path_input).expanduser().resolve()
        if cd_path.exists():
            return os.chdir(cd_path)

        return print(f"cd: {path_input}: No such file or directory")
