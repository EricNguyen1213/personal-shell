import sys
import os
import subprocess
import threading
from app.redirection import Redirection
from typing import Any, NoReturn, Iterable, TextIO, Callable
from pathlib import Path


def find_which_path(fn: str) -> str | None:
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


class CommandResult:
    def __init__(
        self,
        stdout: Iterable[str] = [],
        stderr: Iterable[str] = [],
        process: subprocess.Popen | None = None,
        flush: bool = False,
    ) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.process = process
        self._write = self._write_and_flush if flush else self._write_only

    def _write_only(self, target: TextIO, data: str) -> None:
        target.write(data)

    def _write_and_flush(self, target: TextIO, data: str) -> None:
        target.write(data)
        target.flush()

    def consume(self, redirection: Redirection):
        def drain_stderr():
            for data in self.stderr:
                self._write(redirection.error_file, data)

        err_thread = threading.Thread(target=drain_stderr)
        err_thread.start()

        last_chunk = ""
        for data in self.stdout:
            if data:
                self._write(redirection.output_file, data)
                last_chunk = data

        if redirection.output_file == sys.stdout and not last_chunk.endswith("\n"):
            self._write(redirection.output_file, "\n")

        # 3. Cleanup
        err_thread.join()
        if self.process:
            self.process.wait()


class CommandLibrary:
    def __init__(self) -> None:
        self.command_lib = {
            "exit": self.handle_exit,
            "echo": self.handle_echo,
            "type": self.handle_type,
            "pwd": self.handle_pwd,
            "cd": self.handle_cd,
        }

    def find_command(
        self, cmd: str, user_input: str
    ) -> Callable[[list[str]], CommandResult]:
        command_func = self.command_lib.get(cmd, None)
        if command_func:
            return command_func

        file_path = find_which_path(cmd)
        if file_path:
            return self.handle_custom_exec(cmd)

        return self.not_found(user_input)

    # Command Not Found Case
    def not_found(self, user_input: str) -> Callable[[list[str]], CommandResult]:
        return lambda _: CommandResult(stderr=[f"{user_input}: command not found"])

    # exit Command case
    def handle_exit(self, _) -> NoReturn:
        sys.exit(0)
        return CommandResult()

    # echo Command Case
    def handle_echo(self, args: list[str]) -> CommandResult:
        return CommandResult(stdout=[" ".join(args)])

    # type Command Case
    def handle_type(self, args: list[str]) -> CommandResult:
        result = []
        for arg in args:
            # Argument is Actual Command
            if arg in self.command_lib:
                result.append(f"{arg} is a shell builtin")
                continue

            found_file_path = find_which_path(arg)
            if found_file_path:
                result.append(f"{arg} is {found_file_path}")
            else:
                result.append(f"{arg} not found")
        return CommandResult(stdout=result)

    # pwd Case
    def handle_pwd(self, _) -> CommandResult:
        return CommandResult(stdout=[os.getcwd()])

    # Custom Or Not Found Exec Case
    def handle_custom_exec(self, cmd: str) -> Callable[[list[str]], CommandResult]:
        def handler(args: list[str]) -> CommandResult:
            process = subprocess.Popen(
                [cmd, *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            return CommandResult(
                stdout=process.stdout,
                stderr=process.stderr,
                process=process,
                flush=True,
            )

        return handler

    # cd case
    def handle_cd(self, args: list[str]) -> CommandResult:
        if len(args) > 1:
            return CommandResult(stderr=["cd: too many arguments"])

        path_input = "~" if not args else args[0]
        cd_path = Path(path_input).expanduser().resolve()
        if cd_path.exists():
            return CommandResult(stdout=[os.chdir(cd_path)])

        return CommandResult(stderr=[f"cd: {path_input}: No such file or directory"])
