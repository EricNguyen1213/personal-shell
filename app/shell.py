from app.cmd_lib import CommandLibrary
from app.utils import Prompt, parse_tokens


class PersonalShell:
    def __init__(self) -> None:
        self.cmd_lib = CommandLibrary()
        self.prompter = Prompt()

    def run(self) -> None:

        while True:
            try:
                user_input = self.prompter.ask()

                # User Input Does Not Exist Case
                if not user_input:
                    continue

                cmd, args, context = parse_tokens(user_input)

                # Allow The Closing of Output Files Even With Crashes
                try:
                    # Search Command Library for Correct Function To Use
                    command_func = self.cmd_lib.find_command(context, cmd, user_input)
                    result = command_func(args)
                    result.output()
                finally:
                    context.close()

            except KeyboardInterrupt:
                break
