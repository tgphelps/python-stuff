

"""
filter.py test the filter

Usage:
    filter.py [-d] [-n <count>] [<file>...]

Options:
    -h --help     Show this message.
    --version     Show version.
    -d            Enable debugging.
    -n <count>    Set count.
"""


from abc import ABC, abstractmethod
import docopt  # type: ignore
import sys
from typing import Generator, Tuple

VERSION = '0.0'


class filter(ABC):
    """Simple filter base class, to do some action with each input line,
    and optionally doing something before and after all the lines.
    """

    def __init__(self, doc: str, version: str) -> None:
        """Save the program arguments."""
        self.args = docopt.docopt(doc, version=version)
        # print(self.args)
        self.files = self.args['<file>']
        if self.files == []:
            self.files = ['-']
        # print('New filter:', self.files)

    def get_args(self):
        """Return all program arguments."""
        return self.args

    def run(self) -> None:
        """Run the filter."""
        self.first()
        for line in self.next_line():
            self.foreach(line)
        self.last()

    def first(self) -> None:
        """Code to execute before processing the lines."""
        pass

    def last(self) -> None:
        """Code to execute after processing the lines."""
        pass

    @abstractmethod
    def foreach(self, info: Tuple[str, int, str]) -> None:
        """Code to process an input line. Must be overridden."""
        pass

    def next_line(self, rstrip=True) \
            -> Generator[Tuple[str, int, str], None, None]:
        """Read lines from all files in a list, and yield each line.

        We return a tuple: (filename, relative-line-number, line)

        The line is rstripped by default. We return the filename
        and line number within that file, because the caller might
        care about that.
        """
        for f in self.files:
            file = f
            line_num = 0
            if f == '-':
                for line in sys.stdin:
                    line_num += 1
                    if rstrip:
                        line = line.rstrip()
                    yield file, line_num, line
            else:
                with open(f, 'rt') as fd:
                    for line in fd:
                        line_num += 1
                        if rstrip:
                            line = line.rstrip()
                        yield file, line_num, line


class myfilter(filter):
    def foreach(self, info: Tuple[str, int, str]) -> None:
        print(info)


def main() -> None:
    f = myfilter(__doc__, VERSION)
    print(f.get_args())
    f.run()


if __name__ == '__main__':
    main()
