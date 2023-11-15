# Useful Git Commands (terminal)
### Remove file
    git rm --cached filename.txt

### Remove directory
    git rm --cached -r directory_to_remove

### list git files
    git ls-files -c

### List conflicted files
    git diff --name-only --diff-filter=U --relative


### Merge repo into currnet repo
    git remote add REPO_NAME https://username:<ACCESS_TOKEN>@github.com/path-to-repo.git
    git fetch REPO_NAME --tags
    git merge --allow-unrelated-histories REPO_NAME/main # or whichever branch you want to merge
    git remote remove REPO_NAME