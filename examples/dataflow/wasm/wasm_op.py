import sys
import pathlib

from dffml import (
    Input,
    DataFlow,
    opimp_in,
    run,
    GetSingle,
    AsyncTestCase,
    Operation,
    Definition,
)


import contextlib

from wasmer import engine, Store, Module, Instance
from wasmer_compiler_cranelift import Compiler

from dffml import (
    config,
    field,
    op,
    OperationImplementationContext,
    cached_download,
)


@config
class WASMOperationImplementationConfig:
    function: str = field("Exported function within wasm binary to run")
    binary: bytes = field("Binary WASM")


@contextlib.asynccontextmanager
async def wasm_op_setup_module(self):
    # Let's define the store, that holds the engine, that holds the compiler.
    self.store = Store(engine.JIT(Compiler))
    # Let's compile the module to be able to execute it!
    self.module = Module(self.store, self.config.binary)
    yield self.module


@op(
    name="wasm",
    # Inputs and outputs are meant to be overridden when actual values
    inputs={},
    outputs={},
    imp_enter={"module": lambda self: wasm_op_setup_module(self),},
    config_cls=WASMOperationImplementationConfig,
)
class WASMOperationImplementationContext(OperationImplementationContext):
    async def run(self, inputs):
        # Build the arguments using the order they were defined in the
        # operation's inputs dictionary
        args = {
            key: inputs[key] for key in self.parent.op.inputs.keys()
        }.values()
        # Get the key we will be using for the output dictionary
        ouput_dict_key = list(self.parent.op.outputs.keys())[0]
        # Now the module is compiled, we can instantiate it.
        instance = Instance(self.parent.module)
        # Get the function to call within the instance of the wasm code
        func = getattr(instance.exports, self.parent.config.function)
        # Call the function
        return {ouput_dict_key: func(*args)}


# When we wrap an OperationImplementationContext the implementation becomes
# accessable via .imp
WASMOperationImplementation = WASMOperationImplementationContext.imp


class TestOperations(AsyncTestCase):
    @cached_download(
        "https://github.com/wasmerio/wasmer-python/raw/b7003a54b64b38dbc5c7fbab3dae0bb5f54e6886/examples/appendices/simple.wasm",
        pathlib.Path(__file__).parent / "simple.wasm",
        "003e87d2a1292ae4c5e945aa847ed39b38a724cb657c1cb898a81b1dd7b99e4204cb09232153e447c63aa6ad282636b2",
    )
    async def test_wasmer_example_sum(self, simple_wasm_path):
        # Create an operation specific to the sum function
        wasm_sum = Operation(
            # The name of the operation implementation that this operation is
            # assoctiated with
            name=WASMOperationImplementation.op.name,
            inputs={
                "first_number": Definition(
                    name="wasm_sum.first_number", primitive="int"
                ),
                "second_number": Definition(
                    name="wasm_sum.second_number", primitive="int"
                ),
            },
            outputs={"sum": Definition(name="wasm_sum.sum", primitive="int"),},
        )
        # Run the DataFlow
        async for _ctx, results in run(
            DataFlow(
                # We pass the output operation with an auto generated instance
                # name
                GetSingle,
                # We specify an instance_name for the wasm_sum operation. This
                # allows us to use the same operation implementaiton multiple
                operations={"wasm_sum": wasm_sum},
                implementations={"wasm": WASMOperationImplementation},
                configs={
                    "wasm_sum": {
                        "function": "sum",
                        "binary": simple_wasm_path.read_bytes(),
                    },
                },
                seed=[
                    # The get_single output operation takes a single input.
                    Input(
                        # A list of definition names to inlucde in the results
                        # for each context
                        value=[wasm_sum.outputs["sum"].name],
                        definition=GetSingle.op.inputs["spec"],
                    ),
                ],
            ),
            [
                Input(value=40, definition=wasm_sum.inputs["first_number"]),
                Input(value=2, definition=wasm_sum.inputs["second_number"]),
            ],
        ):
            self.assertEqual(results[wasm_sum.outputs["sum"].name], 42)
