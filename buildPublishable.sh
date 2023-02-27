#!/usr/bin/bash

liveBranch=${1:-main}
baseUrl="https://openqasm.github.io"

# initialize the destination folder
mkdir -p ./publish_build/versions

# Build the version links
unset linkList
for branch in `git for-each-ref --format='%(refname:short)' --sort=-refname refs/heads/stable/`; do
  versionNum=${branch/stable\//}
  linkList="${linkList}  ${versionNum} <${baseUrl}/versions/${versionNum}/index.html>"$'\n'
done

# Remove trailing newline
linkList=${linkList::-1}

# Now substitute the links in index.rst
echo "Substituting %%VersionList with"
echo "${linkList}"
for branch in `git for-each-ref --format='%(refname:short)' --sort=-refname refs/heads/stable/`; do
  versionNum=${branch/stable\//}

  # checkout stable branch
  git checkout ${branch}
  # update with correct VersionList
  awk -i inplace -v VersionList="${linkList}" '{gsub(/%%VersionList/,VersionList)}1' source/index.rst

  # build
  VERSION=${versionNum} make html

  # copy to publish dir
  cp -r build/html ./publish_build/versions/${versionNum}

  git restore source/index.rst
done

# get live branch
git checkout ${liveBranch}

# update with correct VersionList
awk -i inplace -v VersionList="${linkList}" '{gsub(/%%VersionList/,VersionList)}1' source/index.rst

# build
make html

# copy to publish dir
cp -r build/html/* ./publish_build

# leave in default state
git restore source/index.rst
