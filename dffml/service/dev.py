import os
import getpass
import configparser
import pkg_resources
from pathlib import Path

from ..util.skel import Skel
from ..util.cli.cmd import CMD

from ..version import VERSION
from ..util.skel import Skel, SkelTemplateConfig
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD

config = configparser.ConfigParser()
config.read(Path("~", ".gitconfig").expanduser())

USER = getpass.getuser()
NAME = config.get("user", "name", fallback="Unknown")
EMAIL = config.get("user", "email", fallback="unknown@example.com")


def create_from_skel(name):
    """
    Copies samples out of skel/ and does re-naming.
    """

    class CreateCMD(CMD):

        skel = Skel()

        arg_user = Arg(
            "-user",
            help=f"Your username (default: {USER})",
            default=USER,
            required=False,
        )
        arg_name = Arg(
            "-name",
            help=f"Your name (default: {NAME})",
            default=NAME,
            required=False,
        )
        arg_email = Arg(
            "-email",
            help=f"Your email (default: {EMAIL})",
            default=EMAIL,
            required=False,
        )
        arg_description = Arg(
            "-description",
            help=f"Description of python package (default: DFFML {name} {{package name}})",
            default=None,
            required=False,
        )
        arg_target = Arg(
            "-target",
            help=f"Directory to put code in (default: same as package name)",
            default=None,
            required=False,
        )
        arg_package = Arg("package", help="Name of python package to create")

        async def run(self):
            # Set description if None
            if not self.description:
                self.description = f"DFFML {name} {self.package}"
            # Set target directory to package name if not given
            if not self.target:
                self.target = self.package
            # Extract
            self.skel.from_template(
                name,
                self.target,
                SkelTemplateConfig(
                    org=self.user,
                    package=self.package,
                    description=self.description,
                    name=self.name,
                    email=self.email,
                    dffml_version=VERSION,
                ),
            )

    return CreateCMD


class Create(CMD):
    """
    Create new models, operations, etc.
    """

    model = create_from_skel("model")
    operations = create_from_skel("operations")
    service = create_from_skel("service")
    source = create_from_skel("source")


class Link(CMD):
    """
    Create required symlinks from skel/common to the other template directories
    """

    skel = Skel()

    async def run(self):
        for plugin in self.skel.plugins():
            self.skel.create_symlinks(plugin)


class Skeleton(CMD):
    """
    Work with the skeleton directories (create service templates)
    """

    link = Link


class ListEntrypoints(CMD):

    arg_entrypoint = Arg(
        "entrypoint", help="Entrypoint to list, example: dffml.model"
    )

    async def run(self):
        for entrypoint in pkg_resources.iter_entry_points(self.entrypoint):
            print(f"{entrypoint} -> {entrypoint.dist!r}")


class Entrypoints(CMD):

    _list = ListEntrypoints


import sys
import subprocess

from ..df.types import Input, Definition
from ..df.base import operation_in, opimp_in, Operation, op
from ..df.memory import MemoryOrchestrator
from ..operation.output import Associate
from ..util.cli.cmd import CMD
from ..util.cli.arg import Arg


@op(
    inputs={
        "repo": Definition(name="repo", primitive="str", lock=True),
        "user": Definition(name="user", primitive="str"),
    },
    outputs={"commits": Definition(name="commit", primitive="str")},
    expand=["commits"],
)
async def select_commits(repo: str, user: str):
    return {
        "commits": subprocess.check_output(
            ["git", "log", f"--author={user}", "--pretty=format:%H"], cwd=repo
        )
        .decode()
        .split("\n")
    }


@op(
    inputs={
        "repo": select_commits.op.inputs["repo"],
        "commit": select_commits.op.outputs["commits"],
    },
    outputs={"description": Definition(name="description", primitive="str")},
)
async def commit_description(commit: str, repo: str):
    changelog = subprocess.check_output(
        ["git", "diff", f"{commit}~1", commit, "--", "CHANGELOG.md"], cwd=repo
    ).decode()
    if not "@@" in changelog:
        changelog = " ".join(
            subprocess.check_output(
                ["git", "log", f"{commit}", "-1", "--oneline"], cwd=repo
            )
            .decode()
            .split("\n")[0]
            .split()[1:]
        )
    else:
        changelog = changelog[changelog.index("@@") :]
        changelog = ". ".join(
            [
                line[3:]
                for line in changelog.split("\n")
                if line.startswith("+")
            ]
        )
    return {"description": changelog}


OPIMPS = opimp_in(sys.modules[__name__])


class Commits(CMD):
    """
    List a users commits with ether the message or the contribution to the
    changelog.
    """

    arg_repo = Arg(
        "-repo",
        help="Repo to list",
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        ),
    )
    arg_user = Arg("user", help="User to query")

    async def run(self):
        async with MemoryOrchestrator.basic_config(*OPIMPS) as orchestrator:
            async with orchestrator() as octx:
                await octx.ictx.sadd(
                    self.user,
                    Input(
                        value=self.user,
                        definition=select_commits.op.inputs["user"],
                    ),
                    Input(
                        value=self.repo,
                        definition=select_commits.op.inputs["repo"],
                    ),
                    Input(
                        value=[
                            select_commits.op.outputs["commits"].name,
                            commit_description.op.outputs["description"].name,
                        ],
                        definition=Associate.op.inputs["spec"],
                    ),
                )
                async for ctx, results in octx.run_operations():
                    yield results[Associate.op.name]


class Develop(CMD):
    """
    Development utilities for hacking on DFFML itself
    """

    create = Create
    skel = Skeleton
    entrypoints = Entrypoints
    commits = Commits
