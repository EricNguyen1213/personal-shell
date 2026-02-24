import sys
from app.redirection import Redirection
from app.cmd_lib import CommandLibrary, CommandResult
from app.utils import parse_tokens


class PersonalShell:
    def __init__(self) -> None:
        self.cmd_lib = CommandLibrary()

    def run(self) -> None:
        while True:
            try:
                sys.stdout.write("$ ")
                user_input = input().strip()

                # User Input Does Not Exist Case
                if not user_input:
                    continue

                cmd, args, redirection = parse_tokens(user_input)

                try:
                    # Search Command Library for Correct Function To Use
                    command_func = self.cmd_lib.find_command(cmd, user_input)
                    result = command_func(args)
                    result.consume(redirection)
                finally:
                    redirection.close()

            except KeyboardInterrupt:
                break
