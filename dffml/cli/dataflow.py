import sys
import pathlib
import hashlib
import contextlib

from ..base import BaseConfig
from ..df.types import DataFlow, Stage, Operation
from ..config.config import BaseConfigLoader
from ..config.json import JSONConfigLoader
from ..util.data import merge
from ..util.entrypoint import load
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD
from ..util.cli.cmds import (
    SourcesCMD,
    KeysCMD,
    OrchestratorCMD,
)


class Merge(CMD):
    arg_dataflows = Arg(
        "dataflows", help="DataFlows to merge", nargs="+", type=pathlib.Path
    )
    arg_config = Arg(
        "-config",
        help="ConfigLoader to use for exporting",
        type=BaseConfigLoader.load,
        default=JSONConfigLoader,
    )
    arg_not_linked = Arg(
        "-not-linked",
        dest="not_linked",
        help="Do not export dataflows as linked",
        default=False,
        action="store_true",
    )

    async def run(self):
        # The merged dataflow
        merged: Dict[str, Any] = {}
        # For entering ConfigLoader contexts
        async with contextlib.AsyncExitStack() as exit_stack:
            # Load config loaders we'll need as we see their file types
            parsers: Dict[str, BaseConfigLoader] = {}
            for path in self.dataflows:
                _, exported = await BaseConfigLoader.load_file(
                    parsers, exit_stack, path
                )
                merge(merged, exported)
        # Export the dataflow
        dataflow = DataFlow._fromdict(**merged)
        async with self.config(BaseConfig()) as configloader:
            async with configloader() as loader:
                exported = dataflow.export(linked=not self.not_linked)
                sys.stdout.buffer.write(await loader.dumpb(exported))


class Create(CMD):
    arg_operations = Arg(
        "operations", nargs="+", help="Operations to create a dataflow for"
    )
    arg_config = Arg(
        "-config",
        help="ConfigLoader to use",
        type=BaseConfigLoader.load,
        default=JSONConfigLoader,
    )
    arg_not_linked = Arg(
        "-not-linked",
        dest="not_linked",
        help="Do not export dataflows as linked",
        default=False,
        action="store_true",
    )

    async def run(self):
        operations = []
        for load_operation in self.operations:
            if ":" in load_operation:
                operations += list(load(load_operation))
            else:
                operations += [Operation.load(load_operation)]
        async with self.config(BaseConfig()) as configloader:
            async with configloader() as loader:
                dataflow = DataFlow.auto(*operations)
                exported = dataflow.export(linked=not self.not_linked)
                sys.stdout.buffer.write(await loader.dumpb(exported))


class RunCMD(OrchestratorCMD, SourcesCMD):

    arg_sources = SourcesCMD.arg_sources.modify(required=False)
    arg_caching = Arg(
        "-caching",
        help="Skip running DataFlow if a repo already contains these features",
        nargs="+",
        required=False,
        default=[],
    )
    arg_no_update = Arg(
        "-no-update",
        help="Update repo with sources",
        required=False,
        default=True,
        action="store_true",
    )
    arg_no_strict = Arg(
        "-no-strict",
        help="Do not exit on operation exceptions, just log errors",
        dest="no_strict",
        required=False,
        default=False,
        action="store_true",
    )


class RunAllRepos(RunCMD):
    """Run dataflow for all repos in sources"""

    async def repos(self, sctx):
        """
        This method exists so that it can be overriden by RunSingleRepo
        """
        async for repo in sctx.repos():
            yield repo

    async def run_dataflow(self, orchestrator, sources):
        # Orchestrate the running of these operations
        async with orchestrator() as octx, sources() as sctx:
            # Add our inputs to the input network with the context being the
            # repo src_url
            async for repo in self.repos(sctx):
                # Skip running DataFlow if repo already has features
                existing_features = repo.features()
                if self.caching and all(map(
                        lambda cached: cached in existing_features,
                        self.caching)):
                    break

                inputs = []
                for value, def_name in self.inputs:
                    inputs.append(
                        Input(
                            value=value,
                            definition=datafow.definitions[def_name],
                        )
                    )
                if self.repo_def:
                    inputs.append(
                        Input(
                            value=repo.src_url,
                            definition=datafow.definitions[self.repo_def],
                        )
                    )

                await octx.ictx.add(
                    MemoryInputSet(
                        MemoryInputSetConfig(
                            ctx=StringInputSetContext(repo.src_url),
                            inputs=inputs,
                        )
                    )
                )

            async for ctx, results in octx.run(dataflow, strict=not self.no_strict):
                ctx_str = (await ctx.handle()).as_string()
                # TODO Make a RepoInputSetContext which would let us store the
                # repo instead of recalling it by the URL
                repo = await sctx.repo(ctx_str)
                # Store the results
                repo.evaluated(results)
                yield repo
                if self.update:
                    await sctx.update(repo)

    async def run(self):
        async with self.dff as dff, self.sources as sources:
            async for repo in self.run_dataflow(dff, sources):
                yield repo


class RunSingleRepo(RunAllRepos, KeysCMD):
    """Run dataflow for single repo or set of repos"""

    async def repos(self, sctx):
        for src_url in self.keys:
            yield await sctx.repo(src_url)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = SubsetSources(*self.sources, keys=self.keys)


class RunRepos(CMD):
    """Run DataFlow and assign output to a repo"""

    single = RunSingleRepo
    _all = RunAllRepos


class Run(CMD):
    """Run dataflow"""

    repos = RunRepos


class Diagram(CMD):

    arg_stages = Arg(
        "-stages",
        help="Which stages to display: (processing, cleanup, output)",
        nargs="+",
        default=[],
        required=False,
    )
    arg_simple = Arg(
        "-simple",
        help="Don't display input and output names",
        default=False,
        action="store_true",
        required=False,
    )
    arg_display = Arg(
        "-display",
        help="How to display (TD: top down, LR, RL, BT)",
        default="TD",
        required=False,
    )
    arg_dataflow = Arg("dataflow", help="File containing exported DataFlow")
    arg_config = Arg(
        "-config",
        help="ConfigLoader to use for importing",
        type=BaseConfigLoader.load,
        default=None,
    )

    async def run(self):
        dataflow_path = pathlib.Path(self.dataflow)
        config_cls = self.config
        if config_cls is None:
            config_type = dataflow_path.suffix.replace(".", "")
            config_cls = BaseConfigLoader.load(config_type)
        async with config_cls.withconfig(self.extra_config) as configloader:
            async with configloader() as loader:
                exported = await loader.loadb(dataflow_path.read_bytes())
                dataflow = DataFlow._fromdict(**exported)
        print(f"graph {self.display}")
        for stage in Stage:
            # Skip stage if not wanted
            if self.stages and stage.value not in self.stages:
                continue
            stage_node = hashlib.md5(
                ("stage." + stage.value).encode()
            ).hexdigest()
            if len(self.stages) != 1:
                print(f"subgraph {stage_node}[{stage.value.title()} Stage]")
                print(f"style {stage_node} fill:#afd388b5,stroke:#a4ca7a")
            for instance_name, operation in dataflow.operations.items():
                if operation.stage != stage:
                    continue
                subgraph_node = hashlib.md5(
                    ("subgraph." + instance_name).encode()
                ).hexdigest()
                node = hashlib.md5(instance_name.encode()).hexdigest()
                if not self.simple:
                    print(f"subgraph {subgraph_node}[{instance_name}]")
                    print(f"style {subgraph_node} fill:#fff4de,stroke:#cece71")
                print(f"{node}[{operation.instance_name}]")
                for input_name in operation.inputs.keys():
                    input_node = hashlib.md5(
                        ("input." + instance_name + "." + input_name).encode()
                    ).hexdigest()
                    if not self.simple:
                        print(f"{input_node}({input_name})")
                        print(f"{input_node} --> {node}")
                for output_name in operation.outputs.keys():
                    output_node = hashlib.md5(
                        (
                            "output." + instance_name + "." + output_name
                        ).encode()
                    ).hexdigest()
                    if not self.simple:
                        print(f"{output_node}({output_name})")
                        print(f"{node} --> {output_node}")
                if not self.simple:
                    print(f"end")
            if len(self.stages) != 1:
                print(f"end")
        if len(self.stages) != 1:
            print(f"subgraph inputs[Inputs]")
            print(f"style inputs fill:#f6dbf9,stroke:#a178ca")
        for instance_name, input_flow in dataflow.flow.items():
            operation = dataflow.operations[instance_name]
            if self.stages and not operation.stage.value in self.stages:
                continue
            node = hashlib.md5(instance_name.encode()).hexdigest()
            for input_name, sources in input_flow.inputs.items():
                for source in sources:
                    # TODO Put various sources in their own "Inputs" subgraphs
                    if isinstance(source, str):
                        input_definition = operation.inputs[input_name]
                        seed_input_node = hashlib.md5(
                            (source + "." + input_definition.name).encode()
                        ).hexdigest()
                        print(f"{seed_input_node}({input_definition.name})")
                        if len(self.stages) == 1:
                            print(
                                f"style {seed_input_node} fill:#f6dbf9,stroke:#a178ca"
                            )
                        if not self.simple:
                            input_node = hashlib.md5(
                                (
                                    "input." + instance_name + "." + input_name
                                ).encode()
                            ).hexdigest()
                            print(f"{seed_input_node} --> {input_node}")
                        else:
                            print(f"{seed_input_node} --> {node}")
                    else:
                        if not self.simple:
                            source_output_node = hashlib.md5(
                                (
                                    "output."
                                    + ".".join(list(source.items())[0])
                                ).encode()
                            ).hexdigest()
                            input_node = hashlib.md5(
                                (
                                    "input." + instance_name + "." + input_name
                                ).encode()
                            ).hexdigest()
                            print(f"{source_output_node} --> {input_node}")
                        else:
                            source_operation_node = hashlib.md5(
                                list(source.keys())[0].encode()
                            ).hexdigest()
                            print(f"{source_operation_node} --> {node}")
        if len(self.stages) != 1:
            print(f"end")


# Name collision
class Dataflow(CMD):

    merge = Merge
    create = Create
    run = Run
    diagram = Diagram
