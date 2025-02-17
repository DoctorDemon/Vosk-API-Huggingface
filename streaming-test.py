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
        async with websockets.connect('wss://{YOUR HF SPACE URL}/') as websocket: 
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
