import sys
import shlex
import io
import re
from typing import Iterator
from app.redirection import Redirection


OPERATORS = {
    ">": ("output_ch", "w"),
    "1>": ("output_ch", "w"),
    "2>": ("error_ch", "w"),
    ">>": ("output_ch", "a"),
    "1>>": ("output_ch", "a"),
    "2>>": ("error_ch", "a"),
}

OP_PATTERN = re.compile(r"(1>>|2>>|1>|2>|>>|>)")


def operator_finder(tokenizer: shlex.shlex) -> Iterator[str]:
    for token in tokenizer:
        if ">" in token:
            parts = re.split(OP_PATTERN, token)
            yield from (p for p in parts if p)
        else:
            yield token


def parse_tokens(user_input: str) -> tuple[str, list[str], Redirection]:
    input_stream = io.StringIO(user_input)
    tokenizer = shlex.shlex(input_stream, posix=True)
    tokenizer.whitespace_split = True
    final_tokenizer = operator_finder(tokenizer)

    cmd_line = []
    redirects = []
    channels: dict[str, tuple[str, str]] = {}

    while token := next(final_tokenizer, ""):
        op_configs = OPERATORS.get(token, None)
        if not op_configs:
            cmd_line.append(token)
            continue

        channel_name = tokenizer.get_token()
        if not channel_name:
            sys.stdout.write("parse error near `\\n'\n")
            sys.exit(0)

        if channel := channels.get(op_configs[0], None):
            redirects.append(channel[0])
        channels[op_configs[0]] = (channel_name, op_configs[1])

    cmd, *args = cmd_line
    return cmd, args, Redirection(redirects, channels)
