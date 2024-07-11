use crate::git::{get_all_branches, get_files_from_head};
use crate::neo4j::create_relationship;
use crate::openai::{generate_documentation, upload_file};
use neo4rs::Session;
use openai::Client;

pub async fn process_repo(client: &Client, session: &Session, repo_url: &str, repo_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    // Clone the repository
    clone_repo(repo_url, repo_path).await?;

    // Get all branches
    let branches = get_all_branches(repo_path).await?;

    for branch in branches {
        // Checkout branch and get files
        checkout_branch(repo_path, &branch).await?;
        let files = get_files_from_head(repo_path).await?;

        for file in files {
            // Upload files to OpenAI
            upload_file(client, &format!("{}/{}", repo_path, file)).await?;

            // Create relationships in Neo4j
            create_relationship(session, "repo", &file, "CONTAINS").await?;
        }
    }

    // Generate documentation
    let prompt = "Generate documentation based on the files in the repository.";
    let doc = generate_documentation(client, prompt).await?;
    println!("{}", doc);

    Ok(())
}
