#!/bin/bash
# This script makes sure a reno has been updated in the PR.

git fetch origin main

CHANGED_FILES=$(git diff --name-only origin/main $GITHUB_SHA)
for file in $CHANGED_FILES
do
   root=$(echo "./$file" | cut -d / -f 3 )
   if [ "$root" = "notes" ]; then
       echo "Reno added or updated: $file"
       exit 0;
   fi
done

echo Please add or update a release note in ./releasenotes >&2
exit 1
