import io
from typing import List, Any, IO, TYPE_CHECKING

from .ansi import AnsiDecoder
from .text import Text

if TYPE_CHECKING:
    from .console import Console


class FileProxy(io.TextIOBase):
    """Wraps a file (e.g. sys.stdout) and redirects writes to a console."""

    def __init__(self, console: "Console", file: IO[str]) -> None:
        self.__console = console
        self.__file = file
        self.__buffer: List[str] = []
        self.__ansi_decoder = AnsiDecoder()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__file, name)

    def write(self, text: str) -> int:
        buffer = self.__buffer
        lines: List[str] = []
        while text:
            line, new_line, text = text.partition("\n")
            if new_line:
                lines.append("".join(buffer) + line)
                del buffer[:]
            else:
                buffer.append(line)
                break
        if lines:
            console = self.__console
            with console:
                output = Text("\n").join(
                    self.__ansi_decoder.decode_line(line) for line in lines
                )
                console.print(output, markup=False, emoji=False, highlight=False)
        return len(text)

    def flush(self) -> None:
        buffer = self.__buffer
        if buffer:
            self.__console.print("".join(buffer))
            del buffer[:]