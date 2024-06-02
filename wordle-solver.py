import re
import string
from typing import List
from pathlib import Path

import log21


def main(
    word_lists: List[Path],
    /,
    include: str = None,
    exclude: str = None,
    wordle_pattern: str = None,
    length: int = 5,
    *patterns: str
):
    """Solve a Wordle.

    :param word_lists: Paths to the word lists.
    :param include: Include these characters in the word.
    :param exclude: Exclude these characters in the word.
    :param patterns: Custom RegEx pattern to match the word.
    :param wordle_pattern: Custom Wordle Pattern to specify if some character is or is
        not somewhere. You could use custom RegEx patterns instead. E.g. Imagine a
        situation where we figured out that the first character of the target word is is
        "w", and the third character is not "o" or "d"(but it l contains them). We could
        use the script like this:
        > `python3 wordle-solver.py -w /path/to/wordlist -i od -W "(w).[od].."`
    :param length: Length of the word.
    """
    # Prepare the patterns to match the words
    patterns_ = [re.compile(r'^\w{' + str(length) + '}$')]
    if include is not None:
        for char in include:
            patterns_.append(re.compile(rf'^.*{char}.*$'))
    if exclude is not None:
        patterns_.append(re.compile(rf'^[^{exclude}]+$'))
    if patterns is not None:
        for pattern in patterns:
            patterns_.append(re.compile(pattern))
    if wordle_pattern is not None:
        wordle_pattern = wordle_pattern.lower()
        pattern = "^"
        bracket_opened = False
        i = 0
        while i < len(wordle_pattern):
            char = wordle_pattern[i]
            if bracket_opened:
                pattern += char
                if char == ']':
                    bracket_opened = False
                elif char not in string.ascii_lowercase:
                    log21.warning(f'Character `{char}` is not an English letter!')
                i += 1
                continue
            if char == '.':
                pattern += char
            elif char == '(':
                if i + 2 >= len(wordle_pattern) or wordle_pattern[i + 2] != ')':
                    raise log21.ArgumentError(
                        message=
                        "In a wordle-pattern, when you use an opening parenthesis, it "
                        "must be followed by a character and then a closing parenthesis"
                    )
                char = wordle_pattern[i + 1]
                if char not in string.ascii_lowercase:
                    log21.warning(f'Character `{char}` is not an English letter!')
                if char in '.\\[]{}()+*$^':
                    pattern += '\\'
                pattern += char
                i += 2
            elif char == '[':
                if i + 2 >= len(wordle_pattern):
                    raise log21.ArgumentError(
                        message=
                        "In a wordle-pattern, when you use an opening square bracket, "
                        "it must be followed by one or more characters and then a "
                        "closing square bracket."
                    )
                bracket_opened = True
                pattern += '[^'
            else:
                raise log21.ArgumentError(
                    message=f'Unexpected token in wordle-pattern at position {i}:\n\t' +
                    wordle_pattern + '\n\t' + ' ' * i + '^'
                )
            i += 1
        if bracket_opened:
            raise log21.ArgumentError(
                message="In a wordle-pattern, when you use an opening square bracket, "
                "it must be followed by one or more characters and then a "
                "closing square bracket."
            )
        patterns_.append(re.compile(pattern))

    good_words = {}
    for word_list in word_lists:
        if not word_list.is_file():
            log21.error(word_list, 'is not a valid file!')
            continue
        for line in word_list.open('r'):
            line = line[:-1].lower()
            for pattern in patterns_:
                if not pattern.match(line):
                    break
            else:
                if line in good_words:
                    good_words[line] += 1
                else:
                    good_words[line] = 1

    for word, count in sorted(good_words.items(), key=lambda item: item[1]):
        print(count, word)


if __name__ == '__main__':
    log21.argumentify(main)
