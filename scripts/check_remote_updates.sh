#!/bin/bash
set -e

echo "Checking for updates from remote repository..."

# Get the current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Fetch the latest changes
git fetch origin

# Check if the local branch is behind the remote branch
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse origin/$BRANCH)
BASE=$(git merge-base @ origin/$BRANCH)

if [ $LOCAL = $REMOTE ]; then
    echo "Repository is up to date with origin/$BRANCH. Proceeding with push..."
    exit 0
elif [ $LOCAL = $BASE ]; then
    echo "ERROR: Local $BRANCH is behind origin/$BRANCH."
    echo "Please pull the latest changes before pushing:"
    echo "  git pull origin $BRANCH"
    exit 1
else
    echo "Local $BRANCH has diverged from origin/$BRANCH."
    echo "Checking if merging is possible..."

    # Try to merge without committing
    if git merge-tree $(git merge-base @ origin/$BRANCH) @ origin/$BRANCH | grep -q "^<<<<<<< "; then
        echo "ERROR: Merging would cause conflicts."
        echo "Please pull and resolve conflicts before pushing:"
        echo "  git pull origin $BRANCH"
        exit 1
    else
        echo "Merging is possible without conflicts."
        echo "Consider pulling changes before pushing:"
        echo "  git pull origin $BRANCH"
        # We can either force an exit here or allow the push
        # exit 1  # Uncomment to force pull before push
        exit 0
    fi
fi
