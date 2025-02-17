<p align="center">
  <img src="https://media-hosting.imagekit.io//a5117eeb1f1f4c0c/title.png?Expires=1834422837&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=eNbTQXI0qOAvW8W3qCedYF0tW2yv2AMKFBAiiwgVDGGaDmrZWV2JD-oiXmn-sYoYFNyUWoyOwvmxqCbPMFUWJ2nBPCss7~qXg9BjTU1IU-WCDXuH20jmSXgen7hyiqVSzeeXG0tYhz1qrt0foxgPPmYi777GicatXklTh2YyFgw3yTQC4sQKLF3wplSBU5WrlFRH9hYME1dzdyxMGLkcIYp9wl9184lLFexp10kqGMAXYmZD4YIw0oybfk1valnxaHxOHacNskGHQvcl0ZYx7bPitTipXO16UxUx24NXpaSLeRB6TRp2XGpHRZDThGre0RNq7FdPIF9pfrZjjqxRNg__" width="600">
</p>



## Introduction
In this guide, I will walk you through the setup and usage of a Vosk realtime speech transcription docker server, completely hosted on Huggingface Spaces.  <br>

This allows you to build custom speech to text applications **without worrying** about computing power of local devices (eg. Raspberry Pi). 
The system uses a constant websocket connection between server and client to ensure **rapid fast transcription**.

## Setup
### Requirements
This API server runs smoothly and with minimal to no latency on a **standart free Huggingface space with 16gb RAM and 2vCPU** cores for one user.

### The easy way
If you are only interested in using the API as fast as possible, you can clone the already existing Huggingface space of mine.<br>
This will setup the whole API for you but you need to **change the space URL** in the Dockerfile, then you can skip to the Usage part.

[clone the Huggingface space here](https://huggingface.co/spaces/DrDemon/Vosk-EN)

### The custom way
Before you begin, make sure you have a working Huggingface account.
This tutorial uses [the official vosk server image](https://github.com/alphacep/vosk-server), to learn more, follow the link.

To set it up for english speech, follow these steps:

1. Create a Huggingface space, give it a fitting name and select the docker blank preset. 

2. Navigate to the files of the space
   
4. Create a file named "Dockerfile" (no extension!) and paste in the following:  
```dockerfile
FROM alphacep/kaldi-de:latest
EXPOSE 2700
RUN pip install --no-cache-dir websockets vosk
CMD ["python3", "/opt/vosk-server/websocket/asr_server.py", "/opt/vosk-model-de/model", "--allow-websocket-origin", "{YOUR SPACE URL}"]
```
**NOTE: you need to fill in your spaces url in the defined placeholder!** <br>

Your spaces open url is constructed as follows:
- take your Huggingface username (eg. "drdemon")
- take your spaces name as in the url (eg. "DrDemon/Vosk-EN")
- combine it with a dash instead of a slash and add ".hf.space:
```url
drdemon-vosk-EN.hf.space
```
- fill this url in the {YOUR SPACE URL} placeholder.

Once you have created your Dockerfile, you need to edit the already existing Readme.md of the space.
- Add the following line to your Readme.md of your space:
```readme
app_port: 2700 
```
- wait for the build process to finish and...
```error
Failed to open a WebSocket connection: empty Connection header.

You cannot access a WebSocket server directly with a browser. You need a WebSocket client.
```
- **Don't worry! That is intended!**
- Your space will now be accessible through your open space URL and ready to transcribe! 


## Usage
Once everything is set up, you can start using the transcribtion api by writing a simple script, it will stream your microphone input realtime to your transcription API and print the results.
First install the required packages from PyPi:
```bash
pip install websockets sounddevice 
```
Then stream the audio in chunks to the API server:

```python
import json
import sounddevice as sd
import websockets
import asyncio

# Global state
audio_queue = None  # Holds incoming audio data

def callback(indata, frames, time, status):
    """Audio callback to collect incoming data."""
    # Put the incoming audio data into the queue
    loop.call_soon_threadsafe(audio_queue.put_nowait, bytes(indata))

async def transcribe_audio():
    """Continuously listens and detects user speech."""
    # Open an audio input stream
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback) as device:
        # Connect to the WebSocket server
        async with websockets.connect('wss://{YOUR SPACE URL}') as websocket: 
            # Send the configuration to the server
            await websocket.send('{ "config" : { "sample_rate" : %d } }' % (device.samplerate))

            last_partial_text = ""
            partial_count = 0

            while True:
                # Get audio data from the queue
                data = await audio_queue.get()
                # Send audio data to the server
                await websocket.send(data)
                # Receive the transcription result
                response = await websocket.recv()
                
                response_json = json.loads(response)

                if "partial" in response_json:
                    # Handle partial transcription results
                    new_partial_text = response_json["partial"]
                    print(f"Partial: {new_partial_text}")

                    if new_partial_text != last_partial_text:
                        partial_count += 1
                        last_partial_text = new_partial_text

                if "result" in response_json:
                    # Handle final transcription results
                    result_text = response_json["text"]
                    print(f"User said: {result_text}")
                    partial_count = 0

            # Signal the end of the audio stream
            await websocket.send('{"eof" : 1}')
            print(await websocket.recv())

async def main():
    global loop, audio_queue

    loop = asyncio.get_running_loop()
    audio_queue = asyncio.Queue()  # For raw audio data

    # Run transcription
    await transcribe_audio()

if __name__ == '__main__':
    asyncio.run(main())

```
For more examples, check out the documentation or reach out with any questions! 🚀  
[Official Vosk Documentation](https://alphacephei.com/vosk/server) 

*I am not affiliated with Vosk or Huggingface.*
