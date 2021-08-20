import pathlib

from ...source.file import FileSourceConfig
from ...source.json import MemorySource
from ...source.source import Sources
from ...base import field


FIELD_SOURCES = field(
    "Sources for loading and saving",
    default_factory=lambda: Sources(MemorySource(records=[])),
    labeled=True,
    required=True,
)
