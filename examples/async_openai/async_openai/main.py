# async_openai/main.py
from pydantic import BaseModel
from async_openai import process_repo_py
from .models import Neo4jConfig, RepoConfig, OpenAIConfig
from typing import Dict

class Config(BaseModel):
    neo4j: Neo4jConfig
    repo: RepoConfig
    openai: OpenAIConfig

def process_repo(config: Config):
    params: Dict[str, str] = {
        "openai_key": config.openai.key,
        "neo4j_url": config.neo4j.url,
        "neo4j_user": config.neo4j.user,
        "neo4j_pass": config.neo4j.password,
        "repo_url": config.repo.url,
        "repo_path": config.repo.path,
    }
    process_repo_py(params)
