import asyncio

import dffml

import dffml_feature_git.feature.operations


COLLECTOR_DATAFLOW = dffml.DataFlow(
    dffml.GroupBy,
    dffml_feature_git.feature.operations.make_quarters,
    dffml_feature_git.feature.operations.quarters_back_to_date,
    dffml_feature_git.feature.operations.check_if_valid_git_repository_URL,
    dffml_feature_git.feature.operations.clone_git_repo,
    dffml_feature_git.feature.operations.git_repo_default_branch,
    dffml_feature_git.feature.operations.git_repo_commit_from_date,
    dffml_feature_git.feature.operations.git_repo_author_lines_for_dates,
    dffml_feature_git.feature.operations.work,
    dffml_feature_git.feature.operations.git_commits,
    dffml_feature_git.feature.operations.count_authors,
    dffml_feature_git.feature.operations.cleanup_git_repo,
)
COLLECTOR_DATAFLOW.seed = [
    dffml.Input(
        value=10,
        definition=COLLECTOR_DATAFLOW.definitions['quarters'],
    ),
    dffml.Input(
        value=True,
        definition=COLLECTOR_DATAFLOW.definitions['no_git_branch_given'],
    ),
    dffml.Input(
        value={
            "authors": {
                "group": "author_count",
                "by": "quarter",
            },
            "commits": {
                "group": "commit_count",
                "by": "quarter",
            },
            "work": {
                "group": "work_spread",
                "by": "quarter",
            },
        },
        definition=COLLECTOR_DATAFLOW.definitions['group_by_spec'],
    ),
]

"""
DATAFLOW = DataFlow(
    operations={"hello_blank": formatter.op, "remap_to_response": remap.op},
    configs={
        "hello_blank": {"formatting": "Hello {}"},
        "remap_to_response": {
            "dataflow": COLLECTOR_DATAFLOW,
        },
    },
    seed=[
        Input(
            value={"response": [formatter.op.outputs["string"].name]},
            definition=dffml.remap.op.inputs["spec"],
        )
    ],
)
"""

# HELLO_WORLD_DATAFLOW = copy.deepcopy(DATAFLOW)
# HELLO_WORLD_DATAFLOW.seed.append(
#     Input(value="World", definition=formatter.op.inputs["data"])
# )


async def main():
    # Gross, hardcoded inputs and definitions.
    # TODO Convert this service to make it run via dataflows run
    # from the HTTP service once the HTTP service is refactored.
    async for ctx, results in dffml.run(
        self.dataflow,
        [
            dffml.Input(
                value=url,
                definition=self.dataflow.definitions["URL"],
            ),
            dffml.Input(
                # "$(date +'%Y-%m-%d %H:%M')=quarter_start_date" \
                value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                definition=self.dataflow.definitions["quarter_start_date"],
            ),

        ],
    ):
        # TODO Add events and publish changes to clients via data.set as we
        # iterate over data moving between operations here and run output
        # operations as soon as their dependency trees are satisified.
        if task is not None:
            for key, value in results.items():
                await task.data.set(key, value)
        return results

if __name__ == "__main__":
    asyncio.run(main())
