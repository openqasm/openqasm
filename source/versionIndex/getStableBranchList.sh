#!/usr/bin/bash

git branch --list 'stable/*' `# list all stable branches` |
sort -r `# sort in reverse order so most recent is first` |
sed 's/\*//' `# remove the * before the current branch` |
sed 's/^\s*stable\///g' `# remove leading spaces and stable/` |
awk '{print "\n`" $0 " <versions/" $0 "/index.html>`__"}' # convert to link
