#!/bin/bash
# Start the application with specified environment
ENV=${1:-local}  # Default to local if no environment specified
export ENV=$ENV
python main.py