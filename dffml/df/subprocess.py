import copy
import asyncio
import itertools
import traceback
import subprocess
from typing import (
    Dict,
    Any,
)

from .types import (
    Operation,
    DataFlow,
)
from .base import (
    BaseConfig,
    OperationImplementation,
    OperationImplementationContext,
    OperationImplementationNotInstantiated,
    OperationImplementationNotInstantiable,
    BaseOperationImplementationNetworkContext,
    BaseOperationImplementationNetwork,
)
from .memory import (
    BaseMemoryDataFlowObject,
    MemoryOperationImplementationNetworkContext,
)

from ..base import config, field
from ..plugins import inpath
from ..util.entrypoint import entrypoint
from ..util.asynchelper import concurrently


@config
class SubprocessOperationImplementationNetworkConfig:
    operations: Dict[str, OperationImplementation] = field(
        "Operations to load on initialization", default_factory=lambda: {},
    )


class SubprocessOperationImplementationContext(OperationImplementationContext):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # TODO Support for daemons? How might we do that? Need to think on this.
        cmd = [
            # Operation name is the command to run
            self.parent.op.name,
        ] + list(
            # Create arguments based on inputs in standard format (standard is
            # debatable, - vs. --, but this is what we'll go with for now)
            itertools.chain(
                *[[f"--{key}", value] for key, value in inputs.items()]
            )
        )
        # TODO Implement configurable cwd
        kwargs = {
            "stdin": None,
            "stdout": asyncio.subprocess.PIPE,
            "stderr": asyncio.subprocess.PIPE,
            # TODO Configurability of start_new_session
            "start_new_session": True,
        }
        # Run command
        self.logger.debug(f"Running {cmd}, {kwargs}")
        proc = await asyncio.create_subprocess_exec(*cmd, **kwargs)
        # Capture stdout and stderr
        output = {
            "stdout": b"",
            "stderr": b"",
        }
        # Read output and watch for process return
        # TODO Configurability of readline vs. reading some number of bytes for
        # commands with binary outputs
        work = {
            asyncio.create_task(proc.stdout.readline()): "stdout.readline",
            asyncio.create_task(proc.stderr.readline()): "stderr.readline",
            asyncio.create_task(proc.wait()): "wait",
        }
        async for event, result in concurrently(work):
            if event.endswith("readline"):
                # Log line read on stderr output
                # TODO Make this configurable
                if event == "stderr.readline":
                    self.logger.debug(
                        f"{event}: {result.decode(errors='ignore').rstrip()}"
                    )
                # Split the event on ., index 0 will be "stdout" or "stderr".
                # See work dict values for event names.
                stdout_or_stderr = event.split(".")[0]
                # Append to output
                output[stdout_or_stderr] += result
                # If the child closes an fd, then output will empty. Do not
                # attempt to read if this is the case
                if result:
                    # Read another line if fd is not closed
                    coro = getattr(proc, stdout_or_stderr).readline()
                    task = asyncio.create_task(coro)
                    work[task] = event
            else:
                # When wait() returns process has exited
                break
        # TODO Add ability to treat non-zero return code as okay, i.e. don't
        # raise. An example of this is cve-bin-tool, which returns non-zero when
        # issues are found (as of 2.0 release). We should return the
        # proc.returncode when we do this too
        # Raise if the process exited with an error code (non-zero return code).
        self.logger.debug("proc.returncode: %s", proc.returncode)
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(
                proc.returncode,
                cmd,
                output=output["stdout"],
                stderr=output["stderr"],
            )
        # Return stdout of called process. Inspect the operation output to
        # determine what it should be called.
        return {list(self.parent.op.outputs.keys())[0]: output["stdout"]}


class SubprocessOperationImplementation(OperationImplementation):
    CONTEXT = SubprocessOperationImplementationContext


class SubprocessOperationImplementationNetworkContext(
    MemoryOperationImplementationNetworkContext
):
    async def instantiable(
        self, operation: Operation, *, opimp: OperationImplementation = None
    ) -> bool:
        """
        Looks for presence of binary on system
        """
        # This is pure Python, so if we're given an operation implementation we
        # will be able to instantiate it and use it instead of our default
        # subprocess operation implementation.
        if opimp is not None:
            return True
        # If the binary is on the system that's all we can do to check. If it
        # is, we'll try to create a SubprocessOperationImplementation to execute
        # it.
        return inpath(operation.name)

    async def instantiate(
        self,
        operation: Operation,
        config: BaseConfig,
        *,
        opimp: OperationImplementation = None,
    ) -> bool:
        """
        Instantiate instance of SubprocessOperationImplementation for the given
        operation if a special instance is not given via ``opimp`` keyword
        argument.
        """
        if opimp is None:
            if await self.instantiable(operation):
                opimp = SubprocessOperationImplementation
            else:
                raise OperationImplementationNotInstantiable(operation.name)
        # Set the correct instance_name
        opimp = copy.deepcopy(opimp)
        opimp.op = operation
        self.operations[
            operation.instance_name
        ] = await self._stack.enter_async_context(opimp(config))


@entrypoint("subprocess")
class SubprocessOperationImplementationNetwork(
    BaseOperationImplementationNetwork, BaseMemoryDataFlowObject
):
    """
    Instantiates instances of :py:class:`SubprocessOperationImplementation
    <dffml.df.subprocess.SubprocessOperationImplementation>` to handle the
    execution of operating system commands / binaries.

    Examples
    --------

    **run.py**

    .. code-block:: python
        :test:
        :filepath: run.py

        import dffml
        import dffml.noasync

        import logging
        logging.basicConfig(level=logging.DEBUG)

        echo_feed = dffml.Definition(name="echo.feed", primitive="string")
        echo_out = dffml.Definition(name="echo.out", primitive="bytes")

        dataflow = dffml.DataFlow(
            dffml.GetSingle,
            operations={
                "echo": dffml.Operation(
                    name="echo",
                    inputs={
                        "feed": echo_feed
                    },
                    outputs={
                        "out": echo_out
                    }
                )
            },
            seed=[
                dffml.Input(
                    value=[echo_out.name],
                    definition=dffml.GetSingle.op.inputs["spec"],
                ),
            ]
        )

        for _ctx, results in dffml.noasync.run(
            dataflow,
            [
                dffml.Input(
                    value="face",
                    definition=echo_feed,
                ),
            ],
            orchestrator=dffml.MemoryOrchestrator(
                opimp_network=dffml.SubprocessOperationImplementationNetwork(),
            ),
        ):
            print(results)

    .. code-block:: console
        :test:

        $ python run.py

    """

    CONTEXT = SubprocessOperationImplementationNetworkContext
    CONFIG = SubprocessOperationImplementationNetworkConfig
