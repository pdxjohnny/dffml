from typing import List, NamedTuple

from ..df.base import op
from ..df.types import Definition
from ..util.subprocess import Subprocess, exec_subprocess


class SubprocessOutputStringSpec(NamedTuple):
    stdout: str
    stderr: str
    returncode: int


SUBPROCESS_CMD = Definition(name="subprocess.cmd", primitive="List[str]")
SUBPROCESS_CWD = Definition(
    name="subprocess.cwd", primitive="str", default=None,
)
SUBPROCESS_OUTPUT_STRING = Definition(
    name="subprocess.output.str",
    primitive="object",
    spec=SubprocessOutputStringSpec,
)


@op(
    inputs={"cmd": SUBPROCESS_CMD, "cwd": SUBPROCESS_CWD},
    outputs={"result": SUBPROCESS_OUTPUT_STRING},
)
async def subprocess_line_by_line(self, cmd: List[str], cwd: str = None):
    output = SubprocessOutputStringSpec(stdout="", stderr="", returncode=-1)
    async for event, result in exec_subprocess(cmd, cwd=cwd):
        if event == Subprocess.STDOUT_READLINE:
            output.stdout += result.decode()
            result = result.decode().rstrip()
            self.logger.debug(result)
        elif event == Subprocess.STDERR_READLINE:
            output.stderr += result.decode()
            result = result.decode().rstrip()
            self.logger.debug(result)
        elif event == Subprocess.COMPLETED:
            output.returncode = result
    return {"result": output}


@op(
    inputs={"spec": SUBPROCESS_OUTPUT_STRING},
    outputs={
        "result": Definition(name="subprocess.output.nop", primitive="int")
    },
)
async def subprocess_ensure_return_code_exit_success(
    self, spec: SubprocessOutputStringSpec,
) -> None:
    breakpoint()
    if spec.returncode != 0:
        raise RuntimeError(spec.stderr)
    return {"result": spec}
