# NOTE To accept inputs coming from 'seed' origin with definition 'URL'
#   '[{"seed": ["URL"]}]'=repos:create_new_name.inputs.old_name  \
dffml dataflow create \
  -configloader json \
  -flow \
    '[{"seed": ["URL"]}]'=dffml_feature_git.repos:create_new_name.inputs.old_name \
    '[{"repos:repos": "result"}]'=print_output.inputs.data \
  -inputs \
    'dffml'=github.owner \
    'False'=github.repo.public \
  -- \
    check_if_valid_git_repository_URL \
    clone_git_repo \
    git_repo_default_branch \
    dffml_feature_git.repos:create_new_name \
    dffml_feature_git.repos:push_to_github_new_repo \
    print_output \
  | tee "export.json"
# 
# 
# 
# dffml dataflow diagram export.json | tee mermaid.txt
# exit 0
# https://mermaid-js.github.io/mermaid-live-editor/edit
#   -inputs \
#     true=no_git_branch_given \
dffml dataflow run records all \
  -inputs \
    true=no_git_branch_given \
  -log debug \
  -no-echo \
  -record-def URL \
  -dataflow "export.json" \
  -sources inputs=memory \
  -source-records \
    https://github.com/pdxjohnny/httptest \
    /home/pdxjohnny/Documents/python/active-directory-verifiable-credentials-python
