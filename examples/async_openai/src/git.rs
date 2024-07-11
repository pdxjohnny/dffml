use git2::Repository;
use std::fs;

pub async fn clone_repo(url: &str, path: &str) -> Result<(), git2::Error> {
    let _repo = Repository::clone(url, path)?;
    Ok(())
}

pub async fn get_all_branches(repo_path: &str) -> Result<Vec<String>, git2::Error> {
    let repo = Repository::open(repo_path)?;
    let branches = repo.branches(None)?
        .map(|branch| branch.map(|(branch, _)| branch.name().unwrap().unwrap().to_string()))
        .collect::<Result<Vec<_>, _>>()?;
    Ok(branches)
}

pub async fn get_files_from_head(repo_path: &str) -> Result<Vec<String>, git2::Error> {
    let repo = Repository::open(repo_path)?;
    let head = repo.head()?;
    let tree = head.peel_to_tree()?;
    let mut files = vec![];
    tree.walk(git2::TreeWalkMode::PreOrder, |_, entry| {
        if let Some(name) = entry.name() {
            files.push(name.to_string());
        }
        git2::TreeWalkResult::Ok
    })?;
    Ok(files)
}
