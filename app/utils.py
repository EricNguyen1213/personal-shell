import re


# OUTSIDE_WHITESPACE = re.compile(
#     r"""(?<!\\)\s+(?=(?:\\'|\\"|[^'"]|'[^']*'|"[^"]*")*$)"""
# )
OUTSIDE_WHITESPACE_EXCLUDER = re.compile(
    r"""((\\\s)|\\"|\\'|(\'((?!\').)*\')|('((?!').)*')|("(\\"|[^"])*")|([^\s]))+"""
)
TOP_QUOTE_UNWRAPPER = r"""(?s)(((?<!\\)(\'|"|'))((\\"|[^"])*?)\3)"""
ESCAPE_BACKSLASH = r"""\\(?=\\)|(?<!\\)\\"""
COMBINED_PATTERN = re.compile(f"{TOP_QUOTE_UNWRAPPER}|{ESCAPE_BACKSLASH}")


def resolve_escapes_and_quotes(m):
    # If Top-Most Quotes (Avoiding Escaped Quotes Case) Found -> Return Its Body Unchanged
    if m.group(1):
        string_body = m.group(4)
        # Handle Escaped Characters in Double Quotes
        if m.group(3) == '"':
            string_body = string_body.replace("\\\\", "\\")
            string_body = string_body.replace('\\"', '"')
        return string_body

    # Remove Escape Backslashes
    return ""


def sanitize(user_input):
    # Split by Whitespace Entirely Outside of Quotes (Avoiding Escaped Cases)
    cmd, *args = [m.group(0) for m in OUTSIDE_WHITESPACE_EXCLUDER.finditer(user_input)]
    args = [re.sub(COMBINED_PATTERN, resolve_escapes_and_quotes, arg) for arg in args]
    return cmd, args
