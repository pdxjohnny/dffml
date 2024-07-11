use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::types::PyDict;
use pyo3::types::PyModule;
use neo4rs::Graph;
use openai::Client;
use tokio::runtime::Runtime;

mod git;
mod openai;
mod neo4j;
mod documentation;

#[pyfunction]
fn process_repo_py(params: &PyDict) -> PyResult<()> {
    let openai_key: String = params.get_item("openai_key").unwrap().extract().unwrap();
    let neo4j_url: String = params.get_item("neo4j_url").unwrap().extract().unwrap();
    let neo4j_user: String = params.get_item("neo4j_user").unwrap().extract().unwrap();
    let neo4j_pass: String = params.get_item("neo4j_pass").unwrap().extract().unwrap();
    let repo_url: String = params.get_item("repo_url").unwrap().extract().unwrap();
    let repo_path: String = params.get_item("repo_path").unwrap().extract().unwrap();

    let runtime = Runtime::new().unwrap();

    runtime.block_on(async move {
        let openai_client = Client::new(&openai_key);
        let graph = Graph::new(&neo4j_url, &neo4j_user, &neo4j_pass).await.unwrap();
        let session = graph.session().await.unwrap();

        documentation::process_repo(&openai_client, &session, &repo_url, &repo_path)
            .await
            .unwrap();
    });

    Ok(())
}

#[pymodule]
fn async_openai(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_repo_py, m)?)?;
    Ok(())
}
