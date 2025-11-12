#!/bin/bash
# This script makes sure a reno has been updated in the PR.

git fetch origin main

# We only require release notes for changes in the `source` directory.
# Other stuff (governance info, github actions, etc) can be ignored.
CHANGED_SOURCE_FILES=$(git diff --name-only origin/main $GITHUB_SHA -- source)
if [ -z "$CHANGED_SOURCE_FILES" ]; then
    echo "No changes to `source` detected"
    exit 0;
fi;

CHANGED_RELEASE_NOTES=$(git diff --name-only origin/main $GITHUB_SHA -- spec_releasenotes)
CHANGED_RELEASE_NOTES+=$(git diff --name-only origin/main $GITHUB_SHA -- ast_releasenotes)
for file in $CHANGED_RELEASE_NOTES
do
   root=$(echo "./$file" | cut -d / -f 4 )
   if [ "$root" = "notes" ]; then
       echo "Reno added or updated: $file"
       exit 0;
   fi
done

echo Please add or update a release note in ./spec_releasenotes or ./ast_releasenotes >&2
exit 1
