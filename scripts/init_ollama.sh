#!/bin/bash
# Initialize Ollama and pull the specified model

MODEL=${OLLAMA_MODEL:-llama3}

echo "Starting Ollama service..."
ollama serve &

echo "Waiting for Ollama to be ready..."
sleep 10

echo "Pulling model: $MODEL"
ollama pull $MODEL

echo "Ollama initialized with model: $MODEL"
wait

