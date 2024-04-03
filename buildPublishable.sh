#!/usr/bin/bash

set -eux -o pipefail

## This script builds the publishable version of the specification including
## all stable branches. Each is built successively in the normal way after
## a `git checkout` of the found stable branches. Each built stable version is
## placed into the `versions` folder of the top-level final build

liveBranch=${1:-main}
destDir=${2:-"./publish_build"}
repoPath=${3-"heads"} # only remotes/origin will work in CI

echo "Live branch is ${liveBranch}"
echo "Destination dir is ${destDir}"
echo "Searching for stable branches with repo path refs/${repoPath}/stable/"

origBranch=$(git symbolic-ref --short HEAD)

echo "Checking if the current branch ${origBranch} is clean"
if [ -n "$(git status --untracked-files=no --porcelain)" ]; then
  # Uncommitted changes in tracked files
  echo "  ERROR: Some files that have been changed are not committed!"
  echo "  This script will fail to generate a publishable build until everything has been committed"
  git status
  exit 1
fi

# initialize the destination folder
mkdir -p "${destDir}/versions"

# Build the stable version list
versionList=""
for branch in $(git for-each-ref --format='%(refname:short)' --sort=-refname "refs/${repoPath}/stable/"); do
  versionNum=${branch/*stable\//}

  if [ -z "${versionList}" ]
  then
    versionList="${versionNum}"
  else
    versionList="${versionList},${versionNum}"
  fi
done

# Now build each stable version and copy to destination folder
echo "VersionList is ${versionList}"
for branch in $(git for-each-ref --format='%(refname:short)' --sort=-refname "refs/${repoPath}/stable/"); do
  versionNum=${branch/*stable\//}
  
  echo "Checkout stable branch ${branch} with version number ${versionNum}"
  git checkout "${branch}"

  # build
  VERSION=${versionNum} VERSION_LIST=${versionList} make html

  echo "Copy to publish dir ${destDir}/versions/${versionNum}"
  mv build/html "${destDir}/versions/${versionNum}"
  rm -rf build
done

echo "Getting live branch ${liveBranch}"
git checkout "origin/${liveBranch}"

# build
VERSION_LIST=${versionList} make html

echo "Copy to publish dir"
cp -r build/html/* "${destDir}"

echo "Restoring to ${origBranch}"
git checkout "${origBranch}"
