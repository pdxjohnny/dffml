from ..wrapper import (
    context_managed_wrapper_source,
    ContextManagedWrapperSource,
)


def dataset_source(entrypoint_name) -> ContextManagedWrapperSource:
    r"""
    Allows us to quickly programmatically provide access to existing datasets
    via existing or custom sources.

    Under the hood this is an alias for
    :py:func:`dffml.source.wrapper.context_managed_wrapper_source`
    with ``qualname_suffix`` set to "DatasetSource".

    Examples
    --------

    Say we have the following dataset hosted at
    http://download.example.com/data/my_training.csv

    .. code-block::
        :filepath: my_training.csv

        feed,face,dead,beef
        0.0,0,0,0
        0.1,1,10,100
        0.2,2,20,200
        0.3,3,30,300
        0.4,4,40,400

    We could write a dataset source to download and cache the contents locally
    as follows. We want to make sure that we validate the contents of datasets
    using SHA 384 hashes (see
    :py:func:`cached_download <dffml.util.net.cached_download>` for more
    details). Without hash validation we risk downloading the wrong file or
    potentially malicious files.

    >>> import pathlib
    >>> import urllib.request
    >>>
    >>> from dffml.noasync import load
    >>> from dffml.source.csv import CSVSource
    >>> from dffml.source.dataset import dataset_source
    >>> from dffml.util.file import validate_file_hash
    >>>
    >>> @dataset_source("my.training")
    ... def my_training_dataset(
    ...     url: str = "http://download.example.com/data/my_training.csv",
    ...     expected_sha384_hash: str = "2e7f15ea48da79e35d7ea4aa7c37b2359cda06c38f9d0e3b08c5f0a2db0289158a4d17d06f5a0a538e1a449ece0c6cfc",
    ... ):
    ...
    ...     # Create a pathlib.Path object for where the contents will be stored
    ...     filepath = (
    ...         pathlib.Path(
    ...             "~", ".cache", "dffml", "datasets", "my_training.csv"
    ...         )
    ...         .expanduser()
    ...         .resolve()
    ...     )
    ...     # Create parent directories if they don't exist
    ...     if not filepath.parent.is_dir():
    ...         filepath.parent.mkdir(parents=True)
    ...
    ...     # Download the file if it doesn't exist
    ...     if not filepath.is_file():
    ...         urllib.request.urlretrieve(url, filename=str(filepath))
    ...     # Validate the contents
    ...     validate_file_hash(filepath, expected_sha384_hash=expected_sha384_hash)
    ...
    ...     # Create a source using downloaded file
    ...     yield CSVSource(filename=str(filepath))
    >>>
    >>> records = list(load(my_training_dataset.source()))
    >>> print(len(records))
    5
    >>> print(records[0].export())
    {'key': '0', 'features': {'feed': 0.0, 'face': 0, 'dead': 0, 'beef': 0}, 'extra': {}}
    >>>
    >>> with my_training_dataset() as source:
    ...     records = list(load(source))
    ...     print(len(records))
    ...     print(records[2].export())
    5
    {'key': '2', 'features': {'feed': 0.2, 'face': 2, 'dead': 20, 'beef': 200}, 'extra': {}}
    """
    return context_managed_wrapper_source(
        entrypoint_name, qualname_suffix="DatasetSource"
    )
