import sys
import os
import subprocess
import threading
from app.redirection import Redirection
from typing import NoReturn, Iterable, TextIO, Callable
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
    _write_lock = threading.Lock()

    def __init__(
        self,
        context: Redirection,
        stdout: Iterable[str] = [],
        stderr: Iterable[str] = [],
        process: subprocess.Popen | None = None,
        flush: bool = False,
    ) -> None:
        self.context = context
        self.stdout = stdout
        self.stderr = stderr
        self.process = process
        self._write = self._write_and_flush if flush else self._write_only

    def _write_only(self, target: TextIO, data: str) -> None:
        with self._write_lock:
            target.write(data)

    def _write_and_flush(self, target: TextIO, data: str) -> None:
        with self._write_lock:
            target.write(data)
            target.flush()

    def consume(self) -> None:
        def drain(input: Iterable[str], file: TextIO) -> None:
            last_chunk = ""
            for data in input:
                if data:
                    self._write(file, data)
                    last_chunk = data
            if (
                file in (sys.stdout, sys.stderr)
                and last_chunk
                and not last_chunk.endswith("\n")
            ):
                self._write(file, "\n")

        err_thread = threading.Thread(
            target=lambda: drain(self.stderr, self.context.error_file)
        )
        err_thread.start()
        drain(self.stdout, self.context.output_file)

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
        self, context: Redirection, cmd: str, user_input: str
    ) -> Callable[[list[str]], CommandResult]:

        if command_func := self.command_lib.get(cmd, None):
            return lambda args: command_func(context, args)

        # Search for Custom Command Case
        if not find_which_path(cmd):
            return self.not_found(context, user_input)

        return self.handle_custom_exec(context, cmd)

    # Command Not Found Case
    def not_found(
        self, context: Redirection, user_input: str
    ) -> Callable[[list[str]], CommandResult]:
        return lambda _: CommandResult(
            context, stderr=[f"{user_input}: command not found"]
        )

    # exit Command case
    def handle_exit(self, context: Redirection, _) -> NoReturn:
        sys.exit(0)
        return CommandResult(context)

    # echo Command Case
    def handle_echo(self, context: Redirection, args: list[str]) -> CommandResult:
        return CommandResult(context, stdout=[" ".join(args)])

    # type Command Case
    def handle_type(self, context: Redirection, args: list[str]) -> CommandResult:
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
        return CommandResult(context, stdout=result)

    # pwd Case
    def handle_pwd(self, context: Redirection, _) -> CommandResult:
        return CommandResult(context, stdout=[os.getcwd()])

    # Custom Or Not Found Exec Case
    def handle_custom_exec(
        self, context: Redirection, cmd: str
    ) -> Callable[[list[str]], CommandResult]:

        # Default & Redirection to different file case, Use different pipes for output and error stream of process
        def handler(args: list[str]) -> CommandResult:
            process = subprocess.Popen(
                [cmd, *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            return CommandResult(
                context,
                stdout=process.stdout,
                stderr=process.stderr,
                process=process,
                flush=True,
            )

        return handler

    # cd case
    def handle_cd(self, context: Redirection, args: list[str]) -> CommandResult:
        if len(args) > 1:
            return CommandResult(context, stderr=["cd: too many arguments"])

        # Default to Home, Allow and Resolve Absolute and Relative Paths
        path_input = "~" if not args else args[0]
        cd_path = Path(path_input).expanduser().resolve()
        if cd_path.exists():
            os.chdir(cd_path)
            return CommandResult(context)

        return CommandResult(
            context, stderr=[f"cd: {path_input}: No such file or directory"]
        )
