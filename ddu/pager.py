
"""Simple pager to display text, one screen at a time."""

import shutil

class Pager:
    def __init__(self):
        self.max_lines = (shutil.get_terminal_size()).lines - 1
        self.num_lines = 0

    def print(self, text) -> bool:
        """Print the text. When screen is full, ask user if he wants more.
        
        If the user answers 'q', return False, else True.
        """
        print(text)
        self.num_lines += 1
        if self.num_lines >= self.max_lines:
            ans = input('more? (q -> quit) ')
            if ans == 'q':
                return False
            else:
                self.num_lines = 0
                return True
        else:
            return True


def main() -> None:
    p = Pager()
    for n in range(200):
        if not p.print(f'hello {n}'):
            break

if __name__ == '__main__':
    main()
