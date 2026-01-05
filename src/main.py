import threading
import sounddevice as sd
import numpy as np
import effects as e
import gui

INPUT_DEV = 43
OUTPUT_DEV = 40
BLOCK = 2048
SAMPLE_RATE = int(sd.query_devices(OUTPUT_DEV, 'output')['default_samplerate'])

# this function is bitchy and wants to be called first
e.setup(SAMPLE_RATE)

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
    
    if gui.get_state("distortion"):
        processed = e.distortion_effect(processed, gui.get_state("distortion amount"))
    if gui.get_state("volume"):
        processed = e.volume_effect(processed, gui.get_state("volume amount"))
    if gui.get_state("reverb"):
        processed = e.simple_reverb(processed, gui.get_state("reverb amount"))
    if gui.get_state("pitch"):
        processed = e.pitch_shift_phase_vocoder(processed, gui.get_state("pitch value"))
    if gui.get_state("wacky (kinda like an enderman)"):
        buffer_time = gui.get_state("buffer time")
        if buffer_time > 0:
            processed = e.wacky(processed, buffer_time)
        else:
            buffer_time = 0.1
            processed = e.wacky(processed, buffer_time)

    processed = np.clip(processed, -1.0, 1.0)
    outdata[:] = processed[:, None]

def main():
    inputs = []
    outputs = []

    
    for i, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] > 0:
            inputs.append(f"{i}: {dev['name']}")

        if dev["max_output_channels"] > 0:
            outputs.append(f"{i}: {dev['name']}")

    gui.add_dropdown("inputs", inputs)
    gui.add_dropdown("outputs", outputs)

    gui.add_toggle("distortion")
    gui.add_entry("distortion amount", 2)
    
    gui.add_toggle("volume")
    gui.add_entry("volume amount", 1)
    
    gui.add_toggle("reverb")
    gui.add_entry("reverb amount", 1)

    gui.add_toggle("pitch")
    gui.add_entry("pitch value", 1)

    gui.add_toggle("wacky (kinda like an enderman)")
    gui.add_entry("buffer time", 1)

    threading.Thread(target=audio_thread, daemon=True).start()
    gui.app.mainloop()

if __name__ == "__main__":
    main()