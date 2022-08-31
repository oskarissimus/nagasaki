#!/bin/bash

MAJOR=0
MINOR=0
PATCH=1

while [[ $# -gt 0 ]]; do
  case $1 in
    --major)
        MAJOR=1
        MINOR=0
        PATCH=0
        shift # past value
        ;;
    --minor)
        MAJOR=0
        MINOR=1
        PATCH=0
        shift # past value
        ;;
    --patch)
        MAJOR=0
        MINOR=0
        PATCH=1
        shift # past value
        ;;
  esac
done

git fetch --tags
VERSION=$(git describe --tags `git rev-list --tags --max-count=1`)
if [ $PATCH -eq 1 ]; then
    NEXTVERSION=$(echo ${VERSION} | awk -F. -v OFS=. '{$3 += 1 ; print}')
fi
if [ $MINOR -eq 1 ]; then
    NEXTVERSION=$(echo ${VERSION} | awk -F. -v OFS=. '{$2 += 1 ; $3 = 0 ; print}')
fi
if [ $MAJOR -eq 1 ]; then
    NEXTVERSION=$(echo ${VERSION} | awk -F. -v OFS=. '{$1 += 1 ; $2 = 0 ; $3 = 0 ; print}')
fi
# echo $NEXTVERSION
git tag $NEXTVERSION && git push origin $NEXTVERSION
