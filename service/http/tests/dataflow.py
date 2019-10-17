import copy
from typing import NamedTuple, Dict, List

from dffml.df.base import op, OperationImplementationContext
from dffml.df.types import Input, Stage, Definition, DataFlow
from dffml.operation.output import GetSingle
from dffml.util.data import traverse_get


class FormatterConfig(NamedTuple):
    formatting: str


@op(
    inputs={"data": Definition(name="format_data", primitive="string")},
    outputs={"string": Definition(name="message", primitive="string")},
    config_cls=FormatterConfig,
)
def formatter(data: str, op_config: FormatterConfig):
    return {"string": op_config.formatting.format(data)}


# TODO Make it so that operations with no arguments get called at least once
# until then this config will go unused in favor of an input parameter
class RemapConfig(NamedTuple):
    dataflow: DataFlow

    @classmethod
    def _fromdict(cls, **kwargs):
        kwargs["dataflow"] = DataFlow._fromdict(**kwargs["dataflow"])
        return cls(**kwargs)


class RemapFailure(Exception):
    """
    Raised whem results of a dataflow could not be remapped.
    """


# TODO Make it so that only one output operation gets run, the result of that
# operation is the result of the dataflow
@op(
    inputs={"spec": Definition(name="remap_spec", primitive="map")},
    outputs={"response": Definition(name="message", primitive="string")},
    stage=Stage.OUTPUT,
    config_cls=RemapConfig,
)
async def remap(
    self: OperationImplementationContext, spec: Dict[str, List[str]]
):
    # Create a new orchestrator context. Specify that it should use the existing
    # input set context, this way the output operations we'll be running have
    # access to the data from this data flow rather than a new sub flow.
    async with self.octx.parent(ictx=self.octx.ictx) as octx:
        result = await octx.run_dataflow(self.config.dataflow, ctx=self.ctx)
    # Remap the output operations to their feature (copied logic
    # from CLI)
    remap = {}
    for (feature_name, traverse) in spec.items():
        try:
            remap[feature_name] = traverse_get(result, *traverse)
        except KeyError:
            raise RemapFailure(
                "failed to remap %r. Results do not contain %r: %s"
                % (feature_name, ".".join(traverse), result)
            )
    # Results have been remapped
    return remap


HELLO_BLANK_DATAFLOW = DataFlow(
    operations={"hello_blank": formatter.op, "remap_to_response": remap.op},
    configs={
        "hello_blank": {"formatting": "Hello {}"},
        "remap_to_response": {
            "dataflow": DataFlow(
                operations={"get_formatted_message": GetSingle.op},
                seed=[
                    Input(
                        value=[formatter.op.outputs["string"].name],
                        definition=GetSingle.op.inputs["spec"],
                    )
                ],
            )
        },
    },
    seed=[
        Input(
            value={"response": [formatter.op.outputs["string"].name]},
            definition=remap.op.inputs["spec"],
        )
    ],
)

HELLO_WORLD_DATAFLOW = copy.deepcopy(HELLO_BLANK_DATAFLOW)
HELLO_WORLD_DATAFLOW.seed.append(
    Input(value="World", definition=formatter.op.inputs["data"])
)
