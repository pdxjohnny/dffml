from .main import process_repo, Config, Neo4jConfig, RepoConfig, OpenAIConfig

def cli():
    config = Config(
        neo4j=Neo4jConfig(url="neo4j://localhost:7687", user="neo4j", password="password"),
        repo=RepoConfig(url="https://github.com/user/repo.git", path="/tmp/repo"),
        openai=OpenAIConfig(key="your_openai_api_key")
    )

    process_repo(config)
