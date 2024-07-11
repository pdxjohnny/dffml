use openai::Client;
use std::fs::File;
use std::io::Read;

pub async fn upload_file(client: &Client, file_path: &str) -> Result<(), openai::Error> {
    let mut file = File::open(file_path)?;
    let mut contents = vec![];
    file.read_to_end(&mut contents)?;

    client.upload_file("file", &contents).await?;
    Ok(())
}

pub async fn generate_documentation(client: &Client, prompt: &str) -> Result<String, openai::Error> {
    let response = client.completion()
        .prompt(prompt)
        .max_tokens(1024)
        .send()
        .await?;
    Ok(response.choices[0].text.clone())
}
