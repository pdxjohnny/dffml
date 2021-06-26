export default {
    "definitions": {
        "URL": {
            "name": "URL",
            "primitive": "string"
        },
        "author_count": {
            "name": "author_count",
            "primitive": "int"
        },
        "author_line_count": {
            "name": "author_line_count",
            "primitive": "Dict[str, int]"
        },
        "commit_count": {
            "name": "commit_count",
            "primitive": "int"
        },
        "date": {
            "name": "date",
            "primitive": "string"
        },
        "date_pair": {
            "name": "date_pair",
            "primitive": "List[date]"
        },
        "git_branch": {
            "name": "git_branch",
            "primitive": "str"
        },
        "git_commit": {
            "name": "git_commit",
            "primitive": "string"
        },
        "git_repository": {
            "lock": true,
            "name": "git_repository",
            "primitive": "Dict[str, str]",
            "spec": {
                "defaults": {
                    "URL": null
                },
                "name": "GitRepoSpec",
                "types": {
                    "URL": "str",
                    "directory": "str"
                }
            },
            "subspec": false
        },
        "group_by_output": {
            "name": "group_by_output",
            "primitive": "Dict[str, List[Any]]"
        },
        "group_by_spec": {
            "name": "group_by_spec",
            "primitive": "Dict[str, Any]"
        },
        "no_git_branch_given": {
            "name": "no_git_branch_given",
            "primitive": "boolean"
        },
        "quarter": {
            "name": "quarter",
            "primitive": "int"
        },
        "quarter_start_date": {
            "name": "quarter_start_date",
            "primitive": "int"
        },
        "quarters": {
            "name": "quarters",
            "primitive": "int"
        },
        "valid_git_repository_URL": {
            "name": "valid_git_repository_URL",
            "primitive": "boolean"
        },
        "work_spread": {
            "name": "work_spread",
            "primitive": "int"
        }
    },
    "flow": {
        "check_if_valid_git_repository_URL": {
            "inputs": {
                "URL": [
                    "seed"
                ]
            }
        },
        "cleanup_git_repo": {
            "inputs": {
                "repo": [
                    {
                        "clone_git_repo": "repo"
                    }
                ]
            }
        },
        "clone_git_repo": {
            "conditions": [
                {
                    "check_if_valid_git_repository_URL": "valid"
                }
            ],
            "inputs": {
                "URL": [
                    "seed"
                ]
            }
        },
        "count_authors": {
            "inputs": {
                "author_lines": [
                    {
                        "git_repo_author_lines_for_dates": "author_lines"
                    }
                ]
            }
        },
        "git_commits": {
            "inputs": {
                "branch": [
                    {
                        "git_repo_default_branch": "branch"
                    }
                ],
                "repo": [
                    {
                        "clone_git_repo": "repo"
                    }
                ],
                "start_end": [
                    {
                        "quarters_back_to_date": "start_end"
                    }
                ]
            }
        },
        "git_repo_author_lines_for_dates": {
            "inputs": {
                "branch": [
                    {
                        "git_repo_default_branch": "branch"
                    }
                ],
                "repo": [
                    {
                        "clone_git_repo": "repo"
                    }
                ],
                "start_end": [
                    {
                        "quarters_back_to_date": "start_end"
                    }
                ]
            }
        },
        "git_repo_commit_from_date": {
            "inputs": {
                "branch": [
                    {
                        "git_repo_default_branch": "branch"
                    }
                ],
                "date": [
                    {
                        "quarters_back_to_date": "date"
                    }
                ],
                "repo": [
                    {
                        "clone_git_repo": "repo"
                    }
                ]
            }
        },
        "git_repo_default_branch": {
            "conditions": [
                "seed"
            ],
            "inputs": {
                "repo": [
                    {
                        "clone_git_repo": "repo"
                    }
                ]
            }
        },
        "group_by": {
            "inputs": {
                "spec": [
                    "seed"
                ]
            }
        },
        "make_quarters": {
            "inputs": {
                "number": [
                    "seed"
                ]
            }
        },
        "quarters_back_to_date": {
            "inputs": {
                "date": [
                    "seed"
                ],
                "number": [
                    {
                        "make_quarters": "quarters"
                    }
                ]
            }
        },
        "work": {
            "inputs": {
                "author_lines": [
                    {
                        "git_repo_author_lines_for_dates": "author_lines"
                    }
                ]
            }
        }
    },
    "linked": true,
    "operations": {
        "check_if_valid_git_repository_URL": {
            "inputs": {
                "URL": "URL"
            },
            "name": "check_if_valid_git_repository_URL",
            "outputs": {
                "valid": "valid_git_repository_URL"
            },
            "retry": 0,
            "stage": "processing"
        },
        "cleanup_git_repo": {
            "inputs": {
                "repo": "git_repository"
            },
            "name": "cleanup_git_repo",
            "outputs": {},
            "retry": 0,
            "stage": "cleanup"
        },
        "clone_git_repo": {
            "conditions": [
                "valid_git_repository_URL"
            ],
            "inputs": {
                "URL": "URL"
            },
            "name": "clone_git_repo",
            "outputs": {
                "repo": "git_repository"
            },
            "retry": 0,
            "stage": "processing"
        },
        "count_authors": {
            "inputs": {
                "author_lines": "author_line_count"
            },
            "name": "count_authors",
            "outputs": {
                "authors": "author_count"
            },
            "retry": 0,
            "stage": "processing"
        },
        "git_commits": {
            "inputs": {
                "branch": "git_branch",
                "repo": "git_repository",
                "start_end": "date_pair"
            },
            "name": "git_commits",
            "outputs": {
                "commits": "commit_count"
            },
            "retry": 0,
            "stage": "processing"
        },
        "git_repo_author_lines_for_dates": {
            "inputs": {
                "branch": "git_branch",
                "repo": "git_repository",
                "start_end": "date_pair"
            },
            "name": "git_repo_author_lines_for_dates",
            "outputs": {
                "author_lines": "author_line_count"
            },
            "retry": 0,
            "stage": "processing"
        },
        "git_repo_commit_from_date": {
            "inputs": {
                "branch": "git_branch",
                "date": "date",
                "repo": "git_repository"
            },
            "name": "git_repo_commit_from_date",
            "outputs": {
                "commit": "git_commit"
            },
            "retry": 0,
            "stage": "processing"
        },
        "git_repo_default_branch": {
            "conditions": [
                "no_git_branch_given"
            ],
            "inputs": {
                "repo": "git_repository"
            },
            "name": "git_repo_default_branch",
            "outputs": {
                "branch": "git_branch"
            },
            "retry": 0,
            "stage": "processing"
        },
        "group_by": {
            "inputs": {
                "spec": "group_by_spec"
            },
            "name": "group_by",
            "outputs": {
                "output": "group_by_output"
            },
            "retry": 0,
            "stage": "output"
        },
        "make_quarters": {
            "expand": [
                "quarters"
            ],
            "inputs": {
                "number": "quarters"
            },
            "name": "make_quarters",
            "outputs": {
                "quarters": "quarter"
            },
            "retry": 0,
            "stage": "processing"
        },
        "quarters_back_to_date": {
            "expand": [
                "date",
                "start_end"
            ],
            "inputs": {
                "date": "quarter_start_date",
                "number": "quarter"
            },
            "name": "quarters_back_to_date",
            "outputs": {
                "date": "date",
                "start_end": "date_pair"
            },
            "retry": 0,
            "stage": "processing"
        },
        "work": {
            "inputs": {
                "author_lines": "author_line_count"
            },
            "name": "work",
            "outputs": {
                "work": "work_spread"
            },
            "retry": 0,
            "stage": "processing"
        }
    },
    "seed": [
        {
            "definition": "quarters",
            "value": 10
        },
        {
            "definition": "no_git_branch_given",
            "value": true
        },
        {
            "definition": "group_by_spec",
            "value": {
                "authors": {
                    "by": "quarter",
                    "group": "author_count"
                },
                "commits": {
                    "by": "quarter",
                    "group": "commit_count"
                },
                "work": {
                    "by": "quarter",
                    "group": "work_spread"
                }
            }
        }
    ]
};
