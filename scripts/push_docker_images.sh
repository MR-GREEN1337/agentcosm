#!/bin/bash

USERNAME=mrgreen1337

set -e  # exit on any command failure

# Helper function to run commands in background and track their PIDs
run_in_bg() {
  "$@" &
  echo $!
}

echo "Building linux/amd64 images in parallel..."

# Start builds in background
build_pids=()
build_pids+=($(run_in_bg docker build --platform=linux/amd64 -t $USERNAME/agentcosm-web:latest ./web))
build_pids+=($(run_in_bg docker build --platform=linux/amd64 -t $USERNAME/agentcosm-backend:latest ./backend))
build_pids+=($(run_in_bg docker build --platform=linux/amd64 -t $USERNAME/agentcosm-renderer:latest ./renderer))

# Wait for builds and check status
for pid in "${build_pids[@]}"; do
  if ! wait "$pid"; then
    echo "Build failed for PID $pid"
    exit 1
  fi
done

echo "Building finished successfully."

echo "Pushing images to Docker Hub in parallel..."

# Start pushes in background
push_pids=()
push_pids+=($(run_in_bg docker push $USERNAME/agentcosm-web:latest))
push_pids+=($(run_in_bg docker push $USERNAME/agentcosm-backend:latest))
push_pids+=($(run_in_bg docker push $USERNAME/agentcosm-renderer:latest))

# Wait for pushes and check status
for pid in "${push_pids[@]}"; do
  if ! wait "$pid"; then
    echo "Push failed for PID $pid"
    exit 1
  fi
done

echo "All images pushed successfully."
