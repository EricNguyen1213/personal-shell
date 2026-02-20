import re


OUTSIDE_WHITESPACE = re.compile(r"""(?<!\\)\s+(?=(?:[^'"]|'[^']*'|"[^"]*")*$)""")
TOP_QUOTE_UNWRAPPER = r"""(?s)(((?<!\\)(\'|"|'))(.*?)\3)"""
ESCAPE_BACKSLASH = r"""\\(?=\\)|(?<!\\)\\"""
COMBINED_PATTERN = re.compile(f"{TOP_QUOTE_UNWRAPPER}|{ESCAPE_BACKSLASH}")


def resolve_escapes_and_quotes(m):
    # If Top-Most Quotes (Avoiding Escaped Quotes Case) Found -> Return Its Body Unchanged
    if m.group(1):
        return m.group(4)

    # Remove Backslashes signifying Escapedness
    return ""


def sanitize(user_input):
    # Split by Whitespace Entirely Outside of Quotes (Avoiding Escaped Cases)
    cmd, *args = re.split(OUTSIDE_WHITESPACE, user_input)

    args = [re.sub(COMBINED_PATTERN, resolve_escapes_and_quotes, arg) for arg in args]
    return cmd, args
