mod git;
mod openai;
mod neo4j;
mod documentation;

use openai::Client;
use neo4rs::*;
use tokio::main;

#[main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize OpenAI client
    let openai_client = Client::new("your_openai_api_key");

    // Initialize Neo4j session
    let graph = Graph::new("neo4j://localhost:7687", "neo4j", "password").await?;
    let session = graph.session().await?;

    // Process the repository
    let repo_url = "https://github.com/user/repo.git";
    let repo_path = "/tmp/repo";
    documentation::process_repo(&openai_client, &session, repo_url, repo_path).await?;

    Ok(())
}
