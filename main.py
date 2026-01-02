import threading
import sounddevice as sd
import numpy as np
import effects as e
import gui

INPUT_DEV = 43
OUTPUT_DEV = 40
BLOCK = 512
SAMPLE_RATE = int(sd.query_devices(OUTPUT_DEV, 'output')['default_samplerate'])

def audio_thread():
    with sd.Stream(
        device=(INPUT_DEV, OUTPUT_DEV),
        channels=(1, 2),
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK,
        dtype="float32",
        callback=callback,
    ):
        threading.Event().wait()  # keep thread alive

def callback(indata, outdata, frames, time, status):
    mono = indata[:, 0]
    processed = mono

    if gui.state.get("distortion"):
        processed = e.distortion_effect(processed, gui.state["distortion amount"])

    if gui.state.get("volume"):
        processed = e.volume_effect(processed, gui.state["volume amount"])

    processed = np.clip(processed, -1.0, 1.0)
    outdata[:] = processed[:, None]

def main():
    gui.add_toggle("distortion")
    gui.add_entry("distortion amount", 2)
    
    gui.add_toggle("volume")
    gui.add_entry("volume amount", 1)

    gui.add_toggle("reverb")
    gui.add_entry("reverb amount", 1)

    threading.Thread(target=audio_thread, daemon=True).start()

    gui.app.mainloop()

if __name__ == "__main__":
    main()
