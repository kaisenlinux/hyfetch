import argparse
import hashlib
import io
from base64 import urlsafe_b64encode
from pathlib import Path
from typing import BinaryIO, Generator, Tuple, Any

"""
The read_chunks, hash_file, and rehash functions below comes from pip._internal
They are copied to ensure compatibility with future python versions.
https://github.com/pypa/pip/blob/612515d2e0a6ff8676c139c096a45bc28b3456f4/src/pip/_internal/operations/install/wheel.py#L80
"""


def read_chunks(file: BinaryIO, size: int = io.DEFAULT_BUFFER_SIZE) -> Generator[bytes, None, None]:
    """Yield pieces of data from a file-like object until EOF."""
    while True:
        chunk = file.read(size)
        if not chunk:
            break
        yield chunk


def hash_file(path: Path, blocksize: int = 1 << 20) -> Tuple[Any, int]:
    """Return (hash, length) for path using hashlib.sha256()"""

    h = hashlib.sha256()
    length = 0
    with open(path, "rb") as f:
        for block in read_chunks(f, size=blocksize):
            length += len(block)
            h.update(block)
    return h, length


def rehash(path: Path, blocksize: int = 1 << 20) -> Tuple[str, str]:
    """Return (encoded_digest, length) for path using hashlib.sha256()"""
    h, length = hash_file(path, blocksize)
    digest = "sha256=" + urlsafe_b64encode(h.digest()).decode("latin1").rstrip("=")
    return digest, str(length)


if __name__ == '__main__':
    agupa = argparse.ArgumentParser()
    agupa.add_argument("base_path", help="The path of the wheel")
    args = agupa.parse_args()

    base_path = Path(args.base_path)

    # Find the name of the dist-info path
    dist_info = next(base_path.rglob("*.dist-info"))

    # Delete dist_info / record
    record = dist_info / "RECORD"
    order = record.read_text().splitlines()
    record.unlink()

    # Rehash each file in the wheel
    processed = set()
    new_record = []
    for file in order:
        file = base_path / file.split(',')[0]
        if file.exists():
            digest, length = rehash(file)
            new_record.append(f"{str(file.relative_to(base_path)).replace("\\", "/")},{digest},{length}")
            processed.add(file)

    for file in base_path.rglob('*'):
        if file.is_file() and file not in processed:
            digest, length = rehash(file)
            new_record.append(f"{str(file.relative_to(base_path)).replace("\\", "/")},{digest},{length}")

    new_record.append(f"{str(dist_info.relative_to(base_path)).replace("\\", "/")}/RECORD,,")

    # Write the new record
    record.write_text('\n'.join(new_record))
    print("Rehashed successfully")

