# async_openai/models.py
from pydantic import BaseModel

class Neo4jConfig(BaseModel):
    url: str
    user: str
    password: str

class RepoConfig(BaseModel):
    url: str
    path: str

class OpenAIConfig(BaseModel):
    key: str
