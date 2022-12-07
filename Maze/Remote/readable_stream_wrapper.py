import io
from threading import RLock
from types import TracebackType
from typing import IO, Type, Iterator, Iterable, Optional, List

import select

from Maze.Remote.types import IOBytes


class ReadableStreamWrapper(IO[bytes]):
    """
    Wraps a file-like object that might need to be read from one thread and closed from another.
    """
    __lock: RLock
    __closed: bool
    __wrapped: IOBytes

    def __init__(self, real_file: IOBytes):
        self.__lock = RLock()
        self.__closed = False
        self.__wrapped = real_file

    def __enter__(self) -> IO[bytes]:
        return self

    def __exit__(self,
                 __t: Optional[Type[BaseException]],
                 __value: Optional[BaseException],
                 __traceback: Optional[TracebackType]) -> None:
        self.close()

    def close(self) -> None:
        """
        Close the IO object.

        Attempting any further operation after the object is closed will raise an OSError. This method has no
        effect if the file is already closed.
        """
        if self.__closed:
            return
        with self.__lock:
            self.__wrapped.close()
            self.__closed = True

    def fileno(self) -> int:
        """
        Returns the underlying file descriptor (an integer).
        """
        return self.__wrapped.fileno()

    def readable(self) -> bool:
        """
        Returns True if the IO object can be read.
        """
        return True

    def read(self, size: int = -1) -> bytes:
        """
        Read at most size bytes, returned as a bytes object.

        If the size argument is negative, read until EOF is reached.
        Return an empty bytes object at EOF.
        """
        if size < 0:
            result = self.__wrapped.read(size)
            assert result is not None, "ReadableStreamWrapper can not wrap a non-blocking IO object"
            return result
        received = 0
        buffer = bytes(size)
        while size < 0 or received < size:
            chunk_size = self.readinto(buffer[received:])
            received += chunk_size
            if chunk_size == 0:
                break
        return buffer

    def readinto(self, buffer: bytes) -> int:
        """
        Read bytes into buffer.

        Returns number of bytes read (0 for EOF), or None if the object
        is set not to block and has no data to read.
        """
        while not self.__closed:
            # select.select
            # Wait until one or more file descriptors are ready for some kind of I/O.
            #
            #     The first three arguments are iterables of file descriptors to be waited for:
            #     rlist -- wait until ready for reading
            #     wlist -- wait until ready for writing
            #     xlist -- wait for an "exceptional condition"
            #   ...
            # The optional 4th argument specifies a timeout in seconds; it may be
            #     a floating point number to specify fractions of seconds.  If it is absent
            #     or None, the call will never time out.
            with self.__lock:
                readable, _wr, _x = select.select([self.__wrapped], [], [], 0.01)
                if len(readable) > 0:
                    return readable[0].readinto(buffer)
        raise OSError("Can't read a closed file")

    def readline(self, __limit: int = -1) -> bytes:
        raise ValueError("Line-based methods are not available on ReadableStreamWrapper")

    def readlines(self, __hint: int = -1) -> List[bytes]:
        raise ValueError("Line-based methods are not available on ReadableStreamWrapper")

    def seekable(self) -> bool:
        return False

    def seek(self, __offset: int, __whence: int = io.SEEK_CUR) -> int:
        raise ValueError("Cannot seek")

    def tell(self) -> int:
        raise ValueError("Cannot tell")

    def writable(self) -> bool:
        return False

    def flush(self) -> None:
        raise ValueError("Cannot write")

    def truncate(self, __size: Optional[int] = None) -> int:
        raise ValueError("Cannot write")

    def write(self, __s: bytes) -> int:
        raise ValueError("Cannot write")

    def writelines(self, __lines: Iterable[bytes]) -> None:
        raise ValueError("Cannot write")

    def isatty(self) -> bool:
        return False

    def __next__(self) -> bytes:
        raise ValueError("Iterable methods are not available on ReadableStreamWrapper")

    def __iter__(self) -> Iterator[bytes]:
        raise ValueError("Iterable methods are not available on ReadableStreamWrapper")

