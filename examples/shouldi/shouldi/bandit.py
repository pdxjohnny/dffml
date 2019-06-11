import json
import asyncio
from typing import Dict, Any

from dffml.df.types import Definition
from dffml.df.base import op

from .download import source_directory

bandit_issues_by_confidence = Definition(
    name="bandit_issues_by_confidence", primitive="Dict[str, int]"
)


@op(
    inputs={"source": source_directory},
    outputs={"confidence": bandit_issues_by_confidence},
    conditions=[],
)
async def bandit_issues(source: str) -> Dict[str, Any]:
    proc = await asyncio.create_subprocess_exec(
        "bandit",
        "-r",
        source,
        "-f",
        "json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, _stderr = await proc.communicate()

    output = json.loads(stdout)

    base = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNDEFINED": 0}
    confidence = base.copy()
    for key in confidence.keys():
        confidence[key] = base.copy()
    for finding in output["results"]:
        confidence[finding["issue_confidence"]][finding["issue_severity"]] += 1

    return {"confidence": confidence}
