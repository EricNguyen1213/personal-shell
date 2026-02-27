import sys
from pathlib import Path

OUTPUT_CH_KEY = "output_ch"
ERROR_CH_KEY = "error_ch"


class Redirection:
    def __init__(
        self, redirects: list[str], channels: dict[str, tuple[str, str]]
    ) -> None:
        self.output_file = sys.stdout
        self.error_file = sys.stderr
        self.output_close = lambda: None
        self.error_close = lambda: None

        # Redirect Output
        if output_ch := channels.get(OUTPUT_CH_KEY, None):
            self.output_file = open(output_ch[0], output_ch[1])
            self.output_close = self.output_file.close

        # Redirect Error
        if error_ch := channels.get(ERROR_CH_KEY, None):
            self.error_file = open(error_ch[0], error_ch[1])
            self.error_close = self.error_file.close

        for fn in redirects:
            Path(fn).touch()

    def close(self) -> None:
        self.output_close()
        self.error_close()

    def is_active(self) -> bool:
        return not (self.output_file.isatty() and self.error_file.isatty())
