import hashlib
from pathlib import Path

import log21


def _hash(text: bytes, func, save_path: Path):
    hash_ = func(text).hexdigest()
    for i in range(0, len(hash_) - 12, 2):
        # the byte is two hex characters like 'ff' or '1a'
        byte = hash_[i:i + 2]
        save_path /= byte
    save_path /= hash_[-12:]
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_bytes(text)


def hash(
    passwords_file: Path,
    /,
    md5: bool = False,
    sha1: bool = False,
    sha224: bool = False,
    sha256: bool = False,
    sha384: bool = False,
    sha512: bool = False,
    all_algorithms: bool = False,
    capitalize: bool = False,
    upper: bool = False,
    lower: bool = False,
    save_directory: Path = Path('./.hashes')
):
    """Hash passwords in a password list and add them to the local database.

    :param md5: Use MD5 algorithm.
    :param sha1: Use SHA1 algorithm.
    :param sha224: Use SHA224 algorithm.
    :param sha256: Use SHA256 algorithm.
    :param sha384: Use SHA384 algorithm.
    :param sha512: Use SHA512 algorithm.
    :param all_algorithms: Use all of the supported algorithms.
    :param capitalize: Also hash the capitalized version of the password.
    :param upper: Also hash the upper cased version of the password.
    :param lower: Also hash the lower cased version of the password.
    :param save_directory: The directory to use as the local hash storage.
    """
    if not passwords_file.is_file():
        raise log21.ArgumentError("passwords_file must be an existing text file!")

    if all_algorithms:
        hash_functions = (
            hashlib.md5, hashlib.sha1, hashlib.sha224, hashlib.sha256, hashlib.sha384,
            hashlib.sha512
        )
    else:
        hash_functions = []
        if md5:
            hash_functions.append(hashlib.md5)
        if sha1:
            hash_functions.append(hashlib.sha1)
        if sha224:
            hash_functions.append(hashlib.sha224)
        if sha256:
            hash_functions.append(hashlib.sha256)
        if sha384:
            hash_functions.append(hashlib.sha384)
        if sha512:
            hash_functions.append(hashlib.sha512)

    if len(hash_functions) < 1:
        raise log21.TooFewArguments(
            "You need to specify at least one one hash algorithm to use!"
        )

    i = 1
    for line in passwords_file.open('rb'):
        line = line.rstrip(b'\r\n')
        if i % 121 == 0:
            log21.info(f"\rHashing[{i}]:", repr(line)[1:], end='')
        i += 1
        for func in hash_functions:
            _hash(line, func, save_directory)
            if capitalize and line.capitalize() != line:
                _hash(line.capitalize(), func, save_directory)
            if upper and line.upper() != line:
                _hash(line.upper(), func, save_directory)
            if lower and line.lower() != line:
                _hash(line.lower(), func, save_directory)
    log21.info(f"\rHashing[{i}]:", repr(line)[1:])
    log21.info("Done!")


def crack(hash_text: str, /, hashes_directory: Path = Path('./.hashes')):
    """Search for the given hash in the local hash storage.

    :param hash_text: The hash text to look for.
    :param hashes_directory: Path to the directory containing hashes and their text
        values.
    """
    if len(hash_text) < 32:
        raise log21.ArgumentError(
            f"I do not seem to know this hash algorithm: `{hash_text}`"
        )
    path = hashes_directory
    for i in range(0, len(hash_text) - 12, 2):
        # the byte is two hex characters like 'ff' or '1a'
        byte = hash_text[i:i + 2]
        path /= byte
    path /= hash_text[-12:]

    if path.is_file():
        print(path.read_text(encoding='utf-8'))
    else:
        print("Sorry... Failed to find the corresponding password.")


if __name__ == '__main__':
    try:
        log21.argumentify([hash, crack])
    except KeyboardInterrupt:
        log21.fatal("\rKeyboardInterrupt: Exiting...")
