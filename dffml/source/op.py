from typing import List

from ..record import Record
from ..high_level import run
from .source import BaseSource
from ..base import config, field
from ..df.types import DataFlow, Input
from ..util.entrypoint import entrypoint
from ..operation.output import GetSingle
from ..df.base import OperationImplementation
from .memory import MemorySource, MemorySourceContext


class OnlyOneOutputAllowedError(Exception):
    """
    Raised when the opimp given has more than one output
    """


class EmptyError(Exception):
    """
    Raised when the source is still empty after running the opimp
    """


class NotEnoughArgs(Exception):
    """
    Raised when the source was not given an arg for each operation input
    """


@config
class OpSourceConfig:
    opimp: OperationImplementation
    args: List[str] = field(
        "Arguments to operation in input order", default_factory=lambda: [],
    )
    allowempty: bool = field(
        "Raise an error if the source is empty after running the loading operation",
        default=False,
    )


@entrypoint("op")
class OpSource(MemorySource):
    """
    Use an abitrary function as a datasource. Backed by memory.

    Write a function, have it return whatever data you want to have as records
    via a ``dict``. Each key of the ``dict`` should be the record key. The value
    should be a ``dict`` where one key should be ``"features"`` which should
    have the feature data for the record. If you want to load any predictions
    then set ``"predictions"`` to a ``dict`` where each key is the name of the
    feature that was predicted. The value should be a ``dict`` with a
    ``"value"`` key that contains the predicted value, and a ``"confidence"``
    key with it's value being the 0.0 to 1.0 confidence level in that
    prediction.

    Examples
    --------

    If we had the following json file and wanted to use it as a data source

    .. literalinclude:: /../tests/source/op/data.json

    We could write the following function

    .. literalinclude:: /../tests/source/op/parser.py

    Then we can use the op source in the same way we'd use any other source

    .. literalinclude:: /../tests/source/op/list.sh

    You should see the following output

    .. literalinclude:: /../tests/source/op/correct.json
    """

    CONTEXT = MemorySourceContext
    CONFIG = OpSourceConfig

    async def __aenter__(self):
        await super().__aenter__()
        # Ensure the opimp only has one output
        if len(self.config.opimp.op.outputs) != 1:
            raise OnlyOneOutputAllowedError(self.config.opimp.op.outputs)
        # Make a DataFlow
        dataflow = DataFlow.auto(self.config.opimp.__class__, GetSingle)
        # Make get_single output operation grab the output we care about
        dataflow.seed.append(
            Input(
                value=[list(self.config.opimp.op.outputs.values())[0].name],
                definition=GetSingle.op.inputs["spec"],
            )
        )
        # Ensure we have enough inputs
        if len(self.config.args) != len(self.config.opimp.op.inputs):
            raise NotEnoughArgs(
                f"Args: {self.config.args}, Inputs: {self.config.opimp.op.inputs}"
            )
        # Add inputs for operation
        for value, definition in zip(
            self.config.args, self.config.opimp.op.inputs.values()
        ):
            dataflow.seed.append(Input(value=value, definition=definition))
        # Run the DataFlow
        async for _ctx, result in run(dataflow):
            # Grab output definition from result of get_single
            result = result[
                list(self.config.opimp.op.outputs.values())[0].name
            ]
            # Convert to record objects if dict's
            for key, value in result.items():
                if not isinstance(value, Record):
                    result[key] = Record(key, data=value)
            # Set mem to result of operation
            self.mem = result
        # Ensure the source isn't empty
        if not self.mem and not self.config.allowempty:
            raise EmptyError()
