#!/bin/bash

# Build and push docker images to Docker Hub

USERNAME=mrgreen1337

set -e  # exit on any command failure

echo "Building linux/amd64 images in parallel..."

# Start builds in background and capture PIDs directly
docker build --platform=linux/amd64 -t $USERNAME/agentcosm-web:latest ./web &
web_pid=$!

docker build --platform=linux/amd64 -t $USERNAME/agentcosm-backend:latest ./backend &
backend_pid=$!

docker build --platform=linux/amd64 -t   $USERNAME/agentcosm-renderer:latest ./renderer &
renderer_pid=$!

# Store PIDs in array
build_pids=($web_pid $backend_pid $renderer_pid)

# Wait for builds and check status
for pid in "${build_pids[@]}"; do
  if ! wait "$pid"; then
    echo "Build failed for PID $pid"
    exit 1
  fi
done

echo "Building finished successfully."

echo "Pushing images to Docker Hub in parallel..."

# Start pushes in background and capture PIDs directly
docker push $USERNAME/agentcosm-web:latest &
web_push_pid=$!

docker push $USERNAME/agentcosm-backend:latest &
backend_push_pid=$!

docker push $USERNAME/agentcosm-renderer:latest &
renderer_push_pid=$!

# Store PIDs in array
push_pids=($web_push_pid $backend_push_pid $renderer_push_pid)

# Wait for pushes and check status
for pid in "${push_pids[@]}"; do
  if ! wait "$pid"; then
    echo "Push failed for PID $pid"
    exit 1
  fi
done

echo "All images pushed successfully."
