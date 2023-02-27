#!/usr/bin/bash

liveBranch=${1:-main}
baseUrl="https://openqasm.github.io"

echo "Live branch is ${liveBranch}"
echo "BaseURL is ${baseUrl}"

# initialize the destination folder
mkdir -p ./publish_build/versions

# Build the version links
unset linkList
for branch in `git for-each-ref --format='%(refname:short)' --sort=-refname refs/remotes/origin/stable/`; do
  versionNum=${branch/*stable\//}
  linkList="${linkList}  ${versionNum} <${baseUrl}/versions/${versionNum}/index.html>"$'\n'
done

# Remove trailing newline
linkList=${linkList::-1}

# Now substitute the links in index.rst
echo "Substituting %%VersionList with"
echo "${linkList}"
for branch in `git for-each-ref --format='%(refname:short)' --sort=-refname refs/remotes/origin/stable/`; do
  versionNum=${branch/*stable\//}

  echo "Checkout stable branch ${branch}"
  git checkout ${branch}
  echo "Updating with correct VersionList"
  awk -i inplace -v VersionList="${linkList}" '{gsub(/%%VersionList/,VersionList)}1' source/index.rst

  # build
  VERSION=${versionNum} make html

  echo "Copy to publish dir ./publish_build/versions/${versionNum}"
  cp -r build/html ./publish_build/versions/${versionNum}

  git restore source/index.rst
done

echo "Getting live branch ${liveBranch}"
git checkout ${liveBranch}

echo "Updating with correct VersionList"
awk -i inplace -v VersionList="${linkList}" '{gsub(/%%VersionList/,VersionList)}1' source/index.rst

# build
make html

echo "Copy to publish dir"
cp -r build/html/* ./publish_build

echo "Returning repo to default state"
git restore source/index.rst
