#!/bin/bash
set -e

# --- Configuration ---
PROJECT_DIR="/app/vscode-llm-integrator"
LOG_FILE="/app/build_log.txt"

# --- Redirect all output to a log file for better debugging ---
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "--- Starting build and package process at $(date) ---"

# --- Step 1: Navigate to the project directory ---
echo "Changing directory to ${PROJECT_DIR}..."
cd "${PROJECT_DIR}"

# --- Step 2: Install npm dependencies (including @vscode/vsce) ---
echo "Installing npm dependencies..."
npm install

# --- Step 3: Compile TypeScript code ---
echo "Compiling TypeScript source..."
npm run compile

# --- Step 4: Package the extension using the local vsce ---
echo "Packaging the extension with local vsce..."
./node_modules/.bin/vsce package --out llm-integrator-0.0.1.vsix

echo "--- Build and package process completed successfully at $(date) ---"
echo "The packaged extension can be found at ${PROJECT_DIR}/llm-integrator-0.0.1.vsix"