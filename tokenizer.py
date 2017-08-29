"""
Functionality to tokenize a file

:Contains: `Tokenizer`, `Token`
"""

from typing import NamedTuple
import re


class Token(NamedTuple):
    """
    Represents individual token from `Tokenizer`

    :extends: `NamedTuple`

    :Attributes:
       - value: Value of token as a string
       - line: Line number token is from as an int
    """
    value: str
    line: int


def tokenize(file_name: str, keywords: list, match_case: bool):
    """
    Tokenize a file

    Takes a file name and a list of keywords, and produces the contents
     of the file as list of tokens mathcing the keywords. This tokenizer
     uses whitespace and newlines to separate tokens. Keywords to match must
     only be alphanumeric - A-Z + a-z + 0-9.

    :Args:
      - `file_name`: Name of the file to tokenize as string
      - `keywords`: List of keywords to find. Keywords must be entirely alphanumeric strings.
      - `match_case`: Boolean option for whether tokens must match keyword case.

    :Returns: List of all tokens

    :Raises:
       - FileNotFoundError: The file specified by `file_name` must exist and be accessible.
       - RuntimeError: Illegal tokens will cause a RuntimeError with
     the line number and offending token.
    """

    try:
        with open(file_name, 'r') as code_file:
            code = code_file.read()
            if not match_case:
                code = code.upper()
    except FileNotFoundError:
        raise FileNotFoundError("Could not tokenize given file.")

    # List of all tokens
    tokens = []

    # Regex literals
    token_specification = [
        ('ALPHANUMERIC', r'[A-Z0-9]+'),    # Alphanumeric - keywords
        ('NEWLINE',      r'\n'),           # Line endings
        ('WHITESPACE',   r'[ \t]+'),       # Whitespace
        ('MISMATCH',     r'.'),            # Any other character
    ]

    # Full regex - named groups separated by the '|' operator
    regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    # Line number counter
    line_num = 1
    # Iterate over non-overlapping sections of the data
    for match in re.finditer(regex, code):
        # The name of the matched group ('ID', 'NEWLINE', 'SKIP', 'MISMATCH')
        kind = match.lastgroup
        # The section of the data that was matched
        value = match.group(kind)

        if kind == 'NEWLINE':
            line_num += 1
        # Whitespace is skipped over
        elif kind == 'WHITESPACE':
            pass
        elif kind == 'MISMATCH':
            raise RuntimeError(line_num)
        else:
            # If the token is alphanumeric, check if it is a keyword
            if not value in keywords:
                # If not, it's an illegal token
                raise RuntimeError(line_num)
            # If so, return a Token with the value and current line number
            tokens.append(Token(value, line_num))
    return tokens
