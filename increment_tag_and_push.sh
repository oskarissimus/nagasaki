#!/bin/bash
git fetch --tags
VERSION=$(git describe --tags `git rev-list --tags --max-count=1`) 
NEXTVERSION=$(echo ${VERSION} | awk -F. -v OFS=. '{$NF += 1 ; print}')
git tag $NEXTVERSION && git push origin $NEXTVERSION
