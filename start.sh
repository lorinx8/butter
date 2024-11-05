#!/bin/bash
# Start the application with specified environment
ENV=${1:-local}  # Default to local if no environment specified
export ENV=$ENV
uvicorn main:app --host 0.0.0.0 --reload --no-access-log