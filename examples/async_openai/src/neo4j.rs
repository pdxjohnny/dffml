use neo4rs::*;
use tokio::sync::Arc;
use tokio::sync::Mutex;

pub async fn create_relationship(session: &Session, node1: &str, node2: &str, relation: &str) -> Result<(), Box<dyn std::error::Error>> {
    let query = format!("MATCH (a {{name: '{}'}}), (b {{name: '{}'}}) CREATE (a)-[:{}]->(b)", node1, node2, relation);
    session.run(query).await?;
    Ok(())
}
