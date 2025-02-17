# Use the official Kaldi image as the base
FROM alphacep/kaldi-de:latest

# Expose the port that Vosk uses
EXPOSE 2700

# Install dependencies (like websockets)
RUN pip install --no-cache-dir websockets vosk

# Start the Vosk ASR server with the model and allow WebSocket origin for Hugging Face 
# ENSURE YOUR HUGGINGSPACE URL IS FILLED IN!
CMD ["python3", "/opt/vosk-server/websocket/asr_server.py", "/opt/vosk-model-de/model", "--allow-websocket-origin", "{YOUR HF SPACE URL}"]
