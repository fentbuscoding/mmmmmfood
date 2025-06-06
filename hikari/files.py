# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Utilities and classes for interacting with files and web resources."""

from __future__ import annotations

__all__: typing.Sequence[str] = (
    "URL",
    "AsyncReader",
    "AsyncReaderContextManager",
    "Bytes",
    "File",
    "IteratorReader",
    "LazyByteIteratorish",
    "Pathish",
    "Rawish",
    "Resource",
    "Resourceish",
    "WebReader",
    "WebResource",
    "ensure_path",
    "ensure_resource",
    "unwrap_bytes",
)

import abc
import asyncio
import base64
import concurrent.futures
import inspect
import io
import mimetypes
import os
import pathlib
import shutil
import typing
import urllib.parse
import urllib.request

import aiohttp
import attrs

from hikari.internal import net
from hikari.internal import time

if not typing.TYPE_CHECKING:
    # This is insanely hacky, but it is needed for ruff to not complain until it gets type inference
    from hikari.internal import typing_extensions

if typing.TYPE_CHECKING:
    import types

    import typing_extensions  # noqa: TC004

_MAGIC: typing.Final[int] = 50 * 1024
SPOILER_TAG: typing.Final[str] = "SPOILER_"

ReaderImplT = typing.TypeVar("ReaderImplT", bound="AsyncReader")
ReaderImplT_co = typing.TypeVar("ReaderImplT_co", bound="AsyncReader", covariant=True)

Pathish = typing.Union["os.PathLike[str]", str]
"""Type hint representing a literal file or path.

This may be one of:

- [`str`][] path.
- [`os.PathLike`][] derivative, such as [`pathlib.PurePath`][] and [`pathlib.Path`][].
"""

RAWISH_TYPES = (bytes, bytearray, memoryview, io.BytesIO, io.StringIO)

Rawish = typing.Union[bytes, bytearray, memoryview, io.BytesIO, io.StringIO]
"""Type hint representing valid raw data types.

This may be one of:

- [`bytes`][]
- [`bytearray`][]
- [`memoryview`][]
- [`io.BytesIO`][]
- [`io.StringIO`][] (assuming UTF-8 encoding).
"""

LazyByteIteratorish = typing.Union[
    typing.AsyncIterator[bytes],
    typing.AsyncIterable[bytes],
    typing.Iterator[bytes],
    typing.Iterable[bytes],
    typing.AsyncIterator[str],
    typing.AsyncIterable[str],
    typing.Iterator[str],
    typing.Iterable[str],
    typing.AsyncGenerator[bytes, typing.Any],
    typing.Generator[bytes, typing.Any, typing.Any],
    typing.AsyncGenerator[str, typing.Any],
    typing.Generator[str, typing.Any, typing.Any],
    asyncio.StreamReader,
    aiohttp.StreamReader,
]
"""Type hint representing an iterator/iterable of bytes.

This may be one of:

- [`typing.AsyncIterator`][][[`bytes`][]]
- [`typing.AsyncIterable`][][[`bytes`][]]
- [`typing.Iterator`][][[`bytes`][]]
- [`typing.Iterator`][][[`bytes`][]]
- [`typing.AsyncIterator`][][[`str`][]] (assuming UTF-8 encoding).
- [`typing.AsyncIterable`][][[`str`][]] (assuming UTF-8 encoding).
- [`typing.Iterator`][][[`str`][]] (assuming UTF-8 encoding).
- [`typing.Iterable`][][[`str`][]] (assuming UTF-8 encoding).
- [`asyncio.StreamReader`][]
- [`aiohttp.StreamReader`][]
"""

Resourceish = typing.Union["Resource[typing.Any]", Pathish, Rawish]
"""Type hint representing a file or path to a file/URL/data URI.

This may be one of:

- [`hikari.files.Resource`][] or a derivative.
- [`str`][] path.
- [`os.PathLike`][] derivative, such as [`pathlib.PurePath`][] and [`pathlib.Path`][].
- [`bytes`][]
- [`bytearray`][]
- [`memoryview`][]
- [`io.BytesIO`][]
- [`io.StringIO`][] (assuming UTF-8 encoding).
"""


def ensure_path(pathish: Pathish) -> pathlib.Path:
    """Convert a path-like object to a [`pathlib.Path`][] instance."""
    return pathlib.Path(pathish)


def unwrap_bytes(data: Rawish) -> bytes:
    """Convert a byte-like object to bytes."""
    if isinstance(data, bytearray):
        data = bytes(data)
    elif isinstance(data, memoryview):
        data = data.tobytes()
    elif isinstance(data, io.StringIO):
        data = bytes(data.read(), "utf-8")
    elif isinstance(data, io.BytesIO):
        data = data.read()

    return data


def ensure_resource(url_or_resource: Resourceish, /) -> Resource[AsyncReader]:
    """Given a resource or string, convert it to a valid resource as needed.

    Parameters
    ----------
    url_or_resource
        The item to convert. If a [`hikari.files.Resource`][] is passed, it is
        simply returned again. Anything else is converted to a [`hikari.files.Resource`][] first.

    Returns
    -------
    Resource
        The resource to use.
    """
    if isinstance(url_or_resource, Resource):
        return url_or_resource

    if isinstance(url_or_resource, RAWISH_TYPES):
        data = unwrap_bytes(url_or_resource)
        filename = generate_filename_from_details(mimetype=None, extension=None, data=data)
        return typing.cast("Resource[AsyncReader]", Bytes(data, filename))

    url_or_resource = str(url_or_resource)

    if url_or_resource.startswith(("https://", "http://")):
        return typing.cast("Resource[AsyncReader]", URL(url_or_resource))
    if url_or_resource.startswith("data:"):
        try:
            return typing.cast("Resource[AsyncReader]", Bytes.from_data_uri(url_or_resource))
        except ValueError:
            # If we cannot parse it, maybe it is some malformed file?
            pass

    path = pathlib.Path(url_or_resource)
    return typing.cast("Resource[AsyncReader]", File(path, path.name))


def guess_mimetype_from_filename(name: str, /) -> str | None:
    """Guess the mimetype of an object given a filename.

    Parameters
    ----------
    name
        The filename to inspect.

    Returns
    -------
    typing.Optional[str]
        The closest guess to the given filename. May be [`None`][] if
        no match was found.
    """
    guess, _ = mimetypes.guess_type(name)
    return guess


def guess_mimetype_from_data(data: bytes, /) -> str | None:
    """Guess the mimetype of some data from the header.

    !!! warning
        This function only detects valid image headers that Discord allows
        the use of. Anything else will go undetected.

    Parameters
    ----------
    data
        The byte content to inspect.

    Returns
    -------
    typing.Optional[str]
        The mimetype, if it was found. If the header is unrecognised, then
        [`None`][] is returned.
    """
    if data.startswith(b"\211PNG\r\n\032\n"):
        return "image/png"
    if data[6:].startswith((b"Exif", b"JFIF")):
        return "image/jpeg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if data.startswith(b"RIFF") and data[8:].startswith(b"WEBP"):
        return "image/webp"
    return None


def guess_file_extension(mimetype: str) -> str | None:
    """Guess the file extension for a given mimetype.

    Parameters
    ----------
    mimetype
        The mimetype to guess the extension for.

    Examples
    --------
    ```py
    >>> guess_file_extension("image/png")
    ".png"
    ```

    Returns
    -------
    typing.Optional[str]
        The file extension, prepended with a `.`. If no match was found,
        return [`None`][].
    """
    return mimetypes.guess_extension(mimetype)


def generate_filename_from_details(
    *, mimetype: str | None = None, extension: str | None = None, data: bytes | None = None
) -> str:
    """Given optional information about a resource, generate a filename.

    Parameters
    ----------
    mimetype
        The mimetype of the content, or [`None`][] if not known.
    extension
        The file extension to use, or [`None`][] if not known.
    data
        The data to inspect, or [`None`][] if not known.

    Returns
    -------
    str
        A generated quasi-unique filename.
    """
    if data is not None and mimetype is None:
        mimetype = guess_mimetype_from_data(data)

    if extension is None and mimetype is not None:
        extension = guess_file_extension(mimetype)

    if not extension:
        extension = ""
    elif not extension.startswith("."):
        extension = f".{extension}"

    # Nanosecond precision will be less likely to collide.
    return time.uuid() + extension


def to_data_uri(data: bytes, mimetype: str | None) -> str:
    """Convert the data and mimetype to a data URI.

    Parameters
    ----------
    data
        The data to encode as base64.
    mimetype
        The mimetype, or [`None`][] if we should attempt to guess it.

    Returns
    -------
    str
        A data URI string.
    """
    if mimetype is None:
        mimetype = guess_mimetype_from_data(data)

        if mimetype is None:
            msg = "Cannot infer mimetype from input data, specify it manually."
            raise TypeError(msg)

    b64 = base64.b64encode(data).decode()
    return f"data:{mimetype};base64,{b64}"


@attrs.define(weakref_slot=False)
class AsyncReader(typing.AsyncIterable[bytes], abc.ABC):
    """Protocol for reading a resource asynchronously using bit inception.

    This supports being used as an async iterable, although the implementation
    detail is left to each implementation of this class to define.
    """

    filename: str = attrs.field(repr=True)
    """The filename of the resource."""

    mimetype: str | None = attrs.field(repr=True)
    """The mimetype of the resource. May be [`None`][] if not known."""

    async def data_uri(self) -> str:
        """Fetch the data URI.

        This reads the entire resource.
        """
        return to_data_uri(await self.read(), self.mimetype)

    async def read(self) -> bytes:
        """Read the rest of the resource and return it in a [`bytes`][] object."""
        buff = bytearray()
        async for chunk in self:
            buff.extend(chunk)
        return bytes(buff)


class AsyncReaderContextManager(abc.ABC, typing.Generic[ReaderImplT]):
    """Context manager that returns a reader."""

    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    async def __aenter__(self) -> ReaderImplT: ...

    @abc.abstractmethod
    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: types.TracebackType | None
    ) -> None: ...

    # These are only included at runtime in-order to avoid the model being typed as a synchronous context manager.
    if not typing.TYPE_CHECKING:

        def __enter__(self) -> typing.NoReturn:
            # This is async only.
            cls = type(self)
            msg = f"{cls.__module__}.{cls.__qualname__} is async-only, did you mean 'async with'?"
            raise TypeError(msg) from None

        def __exit__(self, exc_type: type[Exception], exc_val: Exception, exc_tb: types.TracebackType) -> None:
            return None


@attrs.define(weakref_slot=False)
@typing.final
class _NoOpAsyncReaderContextManagerImpl(AsyncReaderContextManager[ReaderImplT]):
    impl: ReaderImplT = attrs.field()

    @typing_extensions.override
    async def __aenter__(self) -> ReaderImplT:
        return self.impl

    @typing_extensions.override
    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: types.TracebackType | None
    ) -> None:
        pass


def _to_write_path(path: Pathish, default_filename: str, *, force: bool) -> pathlib.Path:
    path = ensure_path(path)
    if path.is_dir():
        path = path.joinpath(default_filename)

    if not force and path.exists():
        msg = f"file {path!r} already exists; use [force=True][] to overwrite"
        raise FileExistsError(msg)

    return path.expanduser()


def _open_write_path(path: Pathish, default_filename: str, force: bool) -> typing.BinaryIO:  # noqa: FBT001
    path = _to_write_path(path, default_filename, force=force)
    return path.open("wb")


class Resource(typing.Generic[ReaderImplT], abc.ABC):
    """Base for any uploadable or downloadable representation of information.

    These representations can be streamed using bit inception for performance,
    which may result in significant decrease in memory usage for larger
    resources.
    """

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def url(self) -> str:
        """URL of the resource."""

    @property
    @abc.abstractmethod
    def filename(self) -> str:
        """Filename of the resource."""

    @property
    def extension(self) -> str | None:
        """File extension, if there is one."""
        _, _, ext = self.filename.rpartition(".")
        return ext if ext != self.filename else None

    async def read(self, *, executor: concurrent.futures.Executor | None = None) -> bytes:
        """Read the entire resource at once into memory.

        ```py
        data = await resource.read(...)
        # ^-- This is a shortcut for the following --v
        async with resource.stream(...) as reader:
            data = await reader.read()
        ```

        !!! warning
            If you simply wish to re-upload this resource to Discord via
            any endpoint in Hikari, you should opt to just pass this
            resource object directly. This way, Hikari can perform byte
            inception, which significantly reduces the memory usage for
            your bot as it grows larger.

        Parameters
        ----------
        executor
            The executor to run in for blocking operations.
            If [`None`][], then the default executor is used for the
            current event loop.

        Returns
        -------
        bytes
            The entire resource.
        """
        async with self.stream(executor=executor) as reader:
            return await reader.read()

    async def save(
        self, path: Pathish, *, executor: concurrent.futures.Executor | None = None, force: bool = False
    ) -> None:
        """Save this resource to disk.

        This writes the resource file in chunks, and so does not load
        the entire resource into memory.

        Parameters
        ----------
        path
            The path to save this resource to. If this is a string, the
            path will be relative to the current working directory.
        executor
            The executor to run in for blocking operations.
            If [`None`][], then the default executor is used for
            the current event loop.
        force
            Whether to overwrite an existing file.
        """
        loop = asyncio.get_running_loop()
        file = await loop.run_in_executor(executor, _open_write_path, path, self.filename, force)

        try:
            async with self.stream(executor=executor) as reader:
                async for chunk in reader:
                    await loop.run_in_executor(executor, file.write, chunk)
        finally:
            await loop.run_in_executor(executor, file.close)

    @abc.abstractmethod
    def stream(
        self, *, executor: concurrent.futures.Executor | None = None, head_only: bool = False
    ) -> AsyncReaderContextManager[ReaderImplT]:
        """Produce a stream of data for the resource.

        Parameters
        ----------
        executor
            The executor to run in for blocking operations.
            If [`None`][], then the default executor is used for the
            current event loop.
        head_only
            If [`True`][], then only the headers for the HTTP resource this
            object points to will be fetched without downloading the entire
            content, which can be significantly faster if you are scanning
            file types in messages, for example.

        Returns
        -------
        AsyncReaderContextManager[AsyncReader]
            An async iterable of bytes to stream.

            This will error on enter if the target resource doesn't exist.
        """

    @typing_extensions.override
    def __str__(self) -> str:
        return self.url

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"{type(self).__name__}(url={self.url!r}, filename={self.filename!r})"

    @typing_extensions.override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Resource):
            return self.url == other.url
        return False

    @typing_extensions.override
    def __hash__(self) -> int:
        return hash((self.__class__, self.url))


###################
# WEBSITE STREAMS #
###################


@attrs.define(weakref_slot=False)
class WebReader(AsyncReader):
    """Asynchronous reader to use to read data from a web resource."""

    stream: aiohttp.StreamReader = attrs.field(repr=False)
    """The [`aiohttp.StreamReader`][] to read the content from."""

    url: str = attrs.field(repr=False)
    """The URL being read from."""

    status: int = attrs.field()
    """The initial HTTP response status."""

    reason: str = attrs.field()
    """The HTTP response status reason."""

    charset: str | None = attrs.field()
    """Optional character set information, if known."""

    size: int | None = attrs.field()
    """The size of the resource, if known."""

    head_only: bool = attrs.field()
    """If [`True`][], then only the HEAD was requested.

    In this case, reading data off the object will return an empty
    byte string
    """

    @typing_extensions.override
    async def read(self) -> bytes:
        return b"" if self.head_only else await self.stream.read()

    @typing_extensions.override
    async def __aiter__(self) -> typing.AsyncGenerator[typing.Any, bytes]:
        if self.head_only:
            yield b""
        else:
            while not self.stream.at_eof():
                chunk, _ = await self.stream.readchunk()
                yield chunk


@typing.final
class _WebReaderAsyncReaderContextManagerImpl(AsyncReaderContextManager[WebReader]):
    __slots__: typing.Sequence[str] = ("_client_response_ctx", "_client_session", "_head_only", "_web_resource")

    def __init__(self, web_resource: WebResource, *, head_only: bool) -> None:
        self._web_resource = web_resource
        self._head_only = head_only
        self._client_session: aiohttp.ClientSession = NotImplemented
        self._client_response_ctx: typing.AsyncContextManager[aiohttp.ClientResponse] = NotImplemented

    @typing_extensions.override
    async def __aenter__(self) -> WebReader:
        method = "HEAD" if self._head_only else "GET"

        ctx = None
        client_session = aiohttp.ClientSession()

        try:
            ctx = client_session.request(method, self._web_resource.url, raise_for_status=False)
            resp: aiohttp.ClientResponse = await ctx.__aenter__()

            if not (200 <= resp.status < 400):
                raise await net.generate_error_response(resp)  # noqa: TRY301 - We need the traceback to be set

            filename = self._web_resource.filename

            mimetype = None
            if resp.content_disposition is not None:
                mimetype = resp.content_disposition.type

            if mimetype is None:
                mimetype = resp.content_type

            self._client_response_ctx = ctx
            self._client_session = client_session

            return WebReader(
                stream=resp.content,
                url=str(resp.real_url),
                status=resp.status,
                reason=str(resp.reason),
                filename=filename,
                charset=resp.charset,
                mimetype=mimetype,
                size=resp.content_length,
                head_only=self._head_only,
            )

        except Exception as ex:
            if ctx is not None:
                await ctx.__aexit__(type(ex), ex, ex.__traceback__)

            await client_session.close()
            raise

    @typing_extensions.override
    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: types.TracebackType | None
    ) -> None:
        await self._client_response_ctx.__aexit__(exc_type, exc, exc_tb)
        await self._client_session.close()


class WebResource(Resource[WebReader], abc.ABC):
    """Base class for a resource that resides on the internet.

    The logic for identifying this resource is left to each implementation
    to define.

    For a usable concrete implementation, use [`hikari.files.URL`][] instead.

        Some components may choose to not upload this resource directly and
        instead simply refer to the URL as needed. The main place this will
        occur is within embeds. If you need to re-upload the resource, you
        should download it into a [`bytes`][] and pass that instead in these cases.
    """

    __slots__: typing.Sequence[str] = ()

    @typing_extensions.override
    def stream(
        self, *, executor: concurrent.futures.Executor | None = None, head_only: bool = False
    ) -> AsyncReaderContextManager[WebReader]:
        """Start streaming the content into memory by downloading it.

        You can use this to fetch the entire resource, parts of the resource,
        or just to view any metadata that may be provided.

        Parameters
        ----------
        executor
            Not used. Provided only to match the underlying interface.
        head_only
            If [`True`][], then the implementation may only retrieve HEAD
            information if supported. This currently only has any
            effect for web requests.

        Examples
        --------
        Downloading an entire resource at once into memory:

        ```py
        async with obj.stream() as stream:
            data = await stream.read()
        ```

        Checking the metadata:

        ```py
        async with obj.stream() as stream:
            mimetype = stream.mimetype

        if mimetype is None:
            ...
        elif mimetype not in whitelisted_mimetypes:
            ...
        else:
            ...
        ```

        Fetching the data-uri of a resource:

        ```py
        async with obj.stream() as stream:
            data_uri = await stream.data_uri()
        ```

        Returns
        -------
        AsyncReaderContextManager[WebReader]
            An async context manager that when entered, produces the
            data stream.

        Raises
        ------
        hikari.errors.BadRequestError
            If a 400 is returned.
        hikari.errors.UnauthorizedError
            If a 401 is returned.
        hikari.errors.ForbiddenError
            If a 403 is returned.
        hikari.errors.NotFoundError
            If a 404 is returned.
        hikari.errors.ClientHTTPResponseError
            If any other 4xx is returned.
        hikari.errors.InternalServerError
            If any other 5xx is returned.
        hikari.errors.HTTPResponseError
            If any other unexpected response code is returned.
        """
        return _WebReaderAsyncReaderContextManagerImpl(self, head_only=head_only)


@typing.final
class URL(WebResource):
    """A URL that represents a web resource.

    !!! note
        Some components may choose to not upload this resource directly and
        instead simply refer to the URL as needed. The main place this will
        occur is within embeds.

        If you need to re-upload the resource, you should download it into
        a [`bytes`][] and pass that instead in these cases.

    Parameters
    ----------
    url
        The URL of the resource.
    filename
        The filename for the resource.

        If not specified, it will be obtained from the url.
    """

    __slots__: typing.Sequence[str] = ("_filename", "_url")

    def __init__(self, url: str, filename: str | None = None) -> None:
        self._url = url
        self._filename = filename

    @property
    @typing_extensions.override
    def url(self) -> str:
        return self._url

    @property
    @typing_extensions.override
    def filename(self) -> str:
        if self._filename:
            return self._filename

        url = urllib.parse.urlparse(self._url)
        return os.path.basename(url.path)  # noqa: PTH119 - Use `Path.name`


########################################
# ON-DISK FILESYSTEM RESOURCE READERS. #
########################################


@attrs.define(weakref_slot=False)
class ThreadedFileReader(AsyncReader):
    """Asynchronous file reader that reads a resource from local storage.

    This implementation works with pools that exist in the same interpreter
    instance as the caller, namely thread pool executors, where objects
    do not need to be pickled to be communicated.
    """

    _executor: concurrent.futures.ThreadPoolExecutor | None = attrs.field(alias="executor")
    _pointer: typing.BinaryIO = attrs.field(alias="pointer")

    @typing_extensions.override
    async def __aiter__(self) -> typing.AsyncGenerator[typing.Any, bytes]:
        loop = asyncio.get_running_loop()

        while True:
            chunk = await loop.run_in_executor(self._executor, self._pointer.read, _MAGIC)
            yield chunk
            if len(chunk) < _MAGIC:
                break


def _open_read_path(path: pathlib.Path) -> typing.BinaryIO:
    return path.expanduser().open("rb")


@attrs.define(weakref_slot=False)
@typing.final
class _ThreadedFileReaderContextManagerImpl(AsyncReaderContextManager[ThreadedFileReader]):
    executor: concurrent.futures.ThreadPoolExecutor | None = attrs.field()
    file: typing.BinaryIO | None = attrs.field(default=None, init=False)
    filename: str = attrs.field()
    path: pathlib.Path = attrs.field()

    @typing_extensions.override
    async def __aenter__(self) -> ThreadedFileReader:
        if self.file:
            msg = "File is already open"
            raise RuntimeError(msg)

        loop = asyncio.get_running_loop()
        file = await loop.run_in_executor(self.executor, _open_read_path, self.path)
        self.file = file
        return ThreadedFileReader(self.filename, None, self.executor, file)

    @typing_extensions.override
    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: types.TracebackType | None
    ) -> None:
        if not self.file:
            msg = "File isn't open"
            raise RuntimeError(msg)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self.executor, self.file.close)
        self.file = None


def _copy_to_path(current_path: pathlib.Path, copy_to_path: Pathish, default_filename: str, force: bool) -> None:  # noqa: FBT001
    copy_to_path = _to_write_path(copy_to_path, default_filename, force=force)
    shutil.copy2(current_path, copy_to_path)


class File(Resource[ThreadedFileReader]):
    """A resource that exists on the local machine's storage to be uploaded.

    Parameters
    ----------
    path
        The path to use.

        If passing a [`pathlib.Path`][], this must not be a [`pathlib.PurePath`][]
        directly, as it will be used to expand tokens such as `~` that
        denote the home directory, and `..` for relative paths.

        This will all be performed as required in an executor to prevent
        blocking the event loop.
    filename
        The filename to use. If this is [`None`][], the name of the file is taken
        from the path instead.
    spoiler
        Whether to mark the file as a spoiler in Discord.
    """

    __slots__: typing.Sequence[str] = ("_filename", "is_spoiler", "path")

    path: pathlib.Path
    """The path to the file."""

    is_spoiler: bool
    """Whether the file will be marked as a spoiler."""

    _filename: str | None

    def __init__(self, path: Pathish, /, filename: str | None = None, *, spoiler: bool = False) -> None:
        self.path = ensure_path(path)
        self.is_spoiler = spoiler
        self._filename = filename

    @property
    @typing.final
    @typing_extensions.override
    def url(self) -> str:
        return f"attachment://{self.filename}"

    @property
    @typing_extensions.override
    def filename(self) -> str:
        filename = self._filename if self._filename else self.path.name

        if self.is_spoiler:
            return SPOILER_TAG + filename

        return filename

    @typing_extensions.override
    def stream(
        self, *, executor: concurrent.futures.Executor | None = None, head_only: bool = False
    ) -> AsyncReaderContextManager[ThreadedFileReader]:
        """Start streaming the resource using a thread pool executor.

        Parameters
        ----------
        executor
            The thread executor to run the blocking read operations in. If
            [`None`][], the default executor for the running event loop
            will be used instead.

            Only [`concurrent.futures.ThreadPoolExecutor`][] is supported.
        head_only
            Not used. Provided only to match the underlying interface.

        Returns
        -------
        AsyncReaderContextManager[ThreadedFileReader]
            An async context manager that when entered, produces the
            data stream.

        Raises
        ------
        IsADirectoryError
            If the file's path leads to a directory.
        FileNotFoundError
            If the file doesn't exist.
        """
        if executor is None or isinstance(executor, concurrent.futures.ThreadPoolExecutor):
            # asyncio forces the default executor when this is None to always be a thread pool executor anyway,
            # so this is safe enough to do:
            return _ThreadedFileReaderContextManagerImpl(executor, self.filename, self.path)

        msg = "The executor must be a ThreadPoolExecutor or None"
        raise TypeError(msg)

    @typing_extensions.override
    async def save(
        self, path: Pathish, *, executor: concurrent.futures.Executor | None = None, force: bool = False
    ) -> None:
        # An optimization can be done here to avoid a lot of thread calls and streaming
        # by just copying the file
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(executor, _copy_to_path, self.path, path, self.filename, force)


########################################################################
# RAW BYTE, ASYNC ITERATOR, ASYNC ITERABLE, ITERATOR, ITERABLE READERS #
########################################################################


@attrs.define(weakref_slot=False)
class IteratorReader(AsyncReader):
    """Asynchronous file reader that operates on in-memory data."""

    data: bytes | LazyByteIteratorish = attrs.field()
    """The data that will be yielded in chunks."""

    @typing_extensions.override
    async def __aiter__(self) -> typing.AsyncGenerator[typing.Any, bytes]:
        buff = bytearray()
        iterator = self._wrap_iter()

        try:
            while True:
                while len(buff) < _MAGIC:
                    chunk = await iterator.__anext__()
                    buff.extend(chunk)
                yield bytes(buff)
                buff.clear()
        except StopAsyncIteration:
            pass

        if buff:
            yield bytes(buff)

    # We rather keep everything we can here inline.
    async def _wrap_iter(self) -> typing.AsyncGenerator[typing.Any, bytes]:  # noqa: PLR0912
        if isinstance(self.data, bytes):
            for i in range(0, len(self.data), _MAGIC):
                yield self.data[i : i + _MAGIC]

        elif isinstance(self.data, typing.AsyncIterator) or inspect.isasyncgen(self.data):
            try:
                while True:
                    yield self._assert_bytes(await self.data.__anext__())
            except StopAsyncIteration:
                pass

        elif isinstance(self.data, typing.Iterator):
            try:
                while True:
                    yield self._assert_bytes(next(self.data))
            except StopIteration:
                pass

        elif inspect.isgenerator(self.data):
            try:
                while True:
                    yield self._assert_bytes(self.data.send(None))
            except StopIteration:
                pass

        elif isinstance(self.data, typing.Iterable):
            for chunk in self.data:
                yield self._assert_bytes(chunk)

        elif isinstance(self.data, typing.AsyncIterable):
            async for chunk in self.data:
                yield self._assert_bytes(chunk)

        else:
            # Will always fail.
            #
            # This code, typing wise, is expected to be unreachable
            self._assert_bytes(self.data)  # type: ignore[unreachable]

    @staticmethod
    def _assert_bytes(data: object) -> bytes:
        if isinstance(data, str):
            return bytes(data, "utf-8")

        if not isinstance(data, bytes):
            msg = f"Expected bytes but received {type(data).__name__}"
            raise TypeError(msg)
        return data


def _write_bytes(
    path: Pathish,
    default_filename: str,
    data: bytearray | bytes | memoryview,
    force: bool,  # noqa: FBT001
) -> None:
    path = _to_write_path(path, default_filename, force=force)
    path.write_bytes(data)


class Bytes(Resource[IteratorReader]):
    """Representation of in-memory data to upload.

    Parameters
    ----------
    data
        The raw data.
    filename
        The filename to use.
    mimetype
        The mimetype, or [`None`][] if you do not wish to specify this.
        If not provided, then this will be generated from the file extension
        of the filename instead.
    spoiler
        Whether to mark the file as a spoiler in Discord.
    """

    __slots__: typing.Sequence[str] = ("_filename", "data", "is_spoiler", "mimetype")

    data: bytes | LazyByteIteratorish
    """The raw data/provider of raw data to upload."""

    mimetype: str | None
    """The provided mimetype, if provided. Otherwise [`None`][]."""

    is_spoiler: bool
    """Whether the file will be marked as a spoiler."""

    def __init__(
        self,
        data: Rawish | LazyByteIteratorish,
        filename: str,
        /,
        mimetype: str | None = None,
        *,
        spoiler: bool = False,
    ) -> None:
        if isinstance(data, RAWISH_TYPES):
            data = unwrap_bytes(data)

        self.data = data

        if mimetype is None:
            mimetype = guess_mimetype_from_filename(filename) or "text/plain;charset=UTF-8"

        self._filename = filename
        self.mimetype = mimetype
        self.is_spoiler = spoiler

    @property
    @typing_extensions.override
    def url(self) -> str:
        return f"attachment://{self.filename}"

    @property
    @typing_extensions.override
    def filename(self) -> str:
        if self.is_spoiler:
            return SPOILER_TAG + self._filename

        return self._filename

    @typing_extensions.override
    def stream(
        self, *, executor: concurrent.futures.Executor | None = None, head_only: bool = False
    ) -> AsyncReaderContextManager[IteratorReader]:
        """Start streaming the content in chunks.

        Parameters
        ----------
        executor
            Not used. Provided only to match the underlying interface.
        head_only
            Not used. Provided only to match the underlying interface.

        Returns
        -------
        AsyncReaderContextManager[IteratorReader]
            An async context manager that when entered, produces the
            data stream.
        """
        return _NoOpAsyncReaderContextManagerImpl(IteratorReader(self.filename, self.mimetype, self.data))

    @typing_extensions.override
    async def save(
        self, path: Pathish, *, executor: concurrent.futures.Executor | None = None, force: bool = False
    ) -> None:
        if not isinstance(self.data, (bytes, bytearray, memoryview)):
            await super().save(path, executor=executor, force=force)
            return

        # An optimization can be done here to avoid a lot of thread calls and streaming
        # by just writing the whole data at once
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(executor, _write_bytes, path, self.filename, self.data, force)

    @staticmethod
    def from_data_uri(data_uri: str, filename: str | None = None) -> Bytes:
        """Parse a given data URI.

        Parameters
        ----------
        data_uri
            The data URI to parse.
        filename
            Filename to use. If this is not provided, then this is generated
            instead.

        Returns
        -------
        Bytes
            The parsed data URI as a [`hikari.files.Bytes`][] object.

        Raises
        ------
        ValueError
            If the parsed argument is not a data URI.
        """
        if not data_uri.startswith("data:"):
            msg = "Invalid data URI passed"
            raise ValueError(msg)

        # This will not block for a data URI; if it was a URL, it would block, so
        # we guard against this with the check above.
        try:
            with urllib.request.urlopen(data_uri) as response:  # noqa: S310 - audit url open for permitted schemes
                mimetype, _ = mimetypes.guess_type(data_uri)
                data = response.read()
        except Exception as ex:
            msg = "Failed to decode data URI"
            raise ValueError(msg) from ex

        if filename is None:
            filename = generate_filename_from_details(mimetype=mimetype, data=data)

        return Bytes(data, filename, mimetype=mimetype)
