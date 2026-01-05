import threading
import sounddevice as sd
import numpy as np
import effects as e
import gui

BLOCK = 2048

stream = None
stop_event = threading.Event()
audio_lock = threading.Lock()

last_devices = {"in": None, "out": None}

# this function is bitchy and wants to be called first
e.setup(SAMPLE_RATE)

def get_channels(input_dev, output_dev):
    in_ch = min(1, sd.query_devices(input_dev)["max_input_channels"])
    out_ch = min(2, sd.query_devices(output_dev)["max_output_channels"])
    return in_ch, out_ch

def get_samplerate(input_dev, output_dev):
    in_sr = sd.query_devices(input_dev)["default_samplerate"]
    out_sr = sd.query_devices(output_dev)["default_samplerate"]
    return int(min(in_sr, out_sr))

def stop_audio():
    global stream
    stop_event.set()
    if stream is not None:
        try:
            stream.abort()
        except Exception:
            pass
        stream = None

def start_audio(input_dev, output_dev):
    global stream, SAMPLE_RATE

    with audio_lock:
        stop_audio()

        SAMPLE_RATE = get_samplerate(input_dev, output_dev)
        e.setup(SAMPLE_RATE)

        in_ch, out_ch = get_channels(input_dev, output_dev)

        stop_event.clear()

        def run():
            global stream
            try:
                with sd.Stream(
                    device=(input_dev, output_dev),
                    channels=(in_ch, out_ch),
                    samplerate=SAMPLE_RATE,
                    blocksize=BLOCK,
                    dtype="float32",
                    callback=callback,
                ) as s:
                    stream = s
                    stop_event.wait()
            except Exception as ex:
                print("Audio start failed:", ex)

        threading.Thread(target=run, daemon=True).start()

def callback(indata, outdata, frames, time, status):
    mono = indata[:, 0] if indata.shape[1] > 0 else np.zeros(frames)
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


def poll_devices():
    inp = gui.get_state("inputs")
    out = gui.get_state("outputs")

    if not inp or not out:
        gui.app.after(200, poll_devices)
        return

    inp_idx = int(inp.split(":")[0])
    out_idx = int(out.split(":")[0])

    if (inp_idx, out_idx) != (last_devices["in"], last_devices["out"]):
        last_devices["in"] = inp_idx
        last_devices["out"] = out_idx
        start_audio(inp_idx, out_idx)

    gui.app.after(200, poll_devices)

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

    gui.state["inputs"] = inputs[0]
    gui.state["outputs"] = outputs[0]

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

    gui.app.after(200, poll_devices)
    gui.app.mainloop()

if __name__ == "__main__":
    main()