"""
Extracted and modified from `py_essentials` from Phyyyl
and modified by Erkan Demiralay

MIT License

Copyright (c) 2017 Phyyyl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import argparse
import hashlib
import json
from pathlib import Path
from typing import Union

ALGO_DICT = {
 'sha256': hashlib.sha256(),
 'sha512': hashlib.sha512(),
}
SUPPORTED_ALGOS = list(ALGO_DICT)
CHUNK_SIZE = 64 * 1024


def fileChecksum(
        file_path: Union[str, Path],
        algorithm: str = 'sha256',
        printing: bool = False
):
    """generates any checksum of a file"""
    if type(file_path) is str:
        file_path = Path(file_path)
    if algorithm in SUPPORTED_ALGOS:
        hasher = ALGO_DICT[algorithm]
    else:
        errorMsg = f'Received: `{algorithm}`. Expected one of {", ".join(SUPPORTED_ALGOS)}'
        raise ValueError(errorMsg)
    try:
        with open(file_path, 'rb') as file:
            buf = file.read(CHUNK_SIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = file.read(CHUNK_SIZE)
        checksum = hasher.hexdigest()
    except Exception as e:
        checksum = type(e).__name__
    if printing:
        print(f'{file.name} - {checksum}')
    return checksum


def createHashtree(
        directory: Union[str, Path],
        algorithm: str = 'sha256'
):
    """creates a tree view of a directory with the file hashes"""
    if type(directory) is str:
        directory = Path(directory)
    objects = [obj for obj in directory.iterdir()]
    hashTree = {
        obj.name: fileChecksum(obj, algorithm)
        if obj.is_file()
        else createHashtree(obj, algorithm)
        for obj in objects
    }
    return hashTree

def main(args: argparse.Namespace):
    directory = Path(args.directory)
    if not directory.exists():
        raise FileExistsError(f'{directory} does not seem to exist')
    data = createHashtree(directory, 'sha256')
    print(json.dumps(data, sort_keys=True, indent=4))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('directory')
    a = p.parse_args()
    main(a)
