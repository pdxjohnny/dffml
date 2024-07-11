# python -m async_openai --neo4j-url neo4j://localhost:7687 --neo4j-user neo4j --neo4j-password password --repo-url https://github.com/user/repo.git --repo-path /tmp/repo --openai-key your_openai_api_key
import argparse
from pydantic import BaseModel

from .main import process_repo, Config, Neo4jConfig, RepoConfig, OpenAIConfig


def add_arguments_from_model(parser, model, prefix=""):
    for field in model.__fields__.values():
        name = f"{prefix}-{field.name.replace('_', '-')}"
        parser.add_argument(
            name,
            dest=f"{prefix}_{field.name}",
            required=True,
            help=f"{field.name} ({field.type_})",
        )


def make_parser():
    parser = argparse.ArgumentParser(description="Query from all notes")

    add_arguments_from_model(parser, Neo4jConfig, prefix="neo4j")
    add_arguments_from_model(parser, RepoConfig, prefix="repo")
    add_arguments_from_model(parser, OpenAIConfig, prefix="openai")


def cli(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = make_parser()
    args = parser.parse_args(argv)

    neo4j_config = Neo4jConfig(
        url=args.neo4j_url,
        user=args.neo4j_user,
        password=args.neo4j_password,
    )

    repo_config = RepoConfig(
        url=args.repo_url,
        path=args.repo_path,
    )

    openai_config = OpenAIConfig(
        key=args.openai_key,
    )

    config = Config(
        neo4j=neo4j_config,
        repo=repo_config,
        openai=openai_config,
    )

    process_repo(config)


if __name__ == "__main__":
    main()
