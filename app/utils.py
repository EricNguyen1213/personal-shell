import re


OUTSIDE_WHITESPACE = re.compile(r"""(?<!\\)\s+(?=(?:[^'"]|'[^']*'|"[^"]*")*$)""")
TOP_QUOTE_UNWRAPPER = re.compile(r"""((?<!\\)(\'|"|'))(.*?)\1""")
ESCAPE_BACKSLASH = re.compile(r"""\\(?=\\)|(?<!\\)\\""")


def sanitize(user_input):
    # Split by Whitespace Entirely Outside of Quotes (Avoiding Escaped Cases)
    cmd, *args = re.split(OUTSIDE_WHITESPACE, user_input)

    # Remove Top-Most Quotes (Avoiding Escaped Cases):  "'hello'"'"world"'  -> 'hello'"world"
    args = [re.sub(TOP_QUOTE_UNWRAPPER, r"\3", arg) for arg in args]

    # Remove Escape Backslashes
    args = [re.sub(ESCAPE_BACKSLASH, "", arg) for arg in args]

    return cmd, args
