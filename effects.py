import numpy as np

SAMPLE_RATE = 0

def setup(sample_rate):
    SAMPLE_RATE = sample_rate

def volume_effect(signal, gain=1.5):
    return signal * gain

def distortion_effect(signal, amount=0.5):
    return np.tanh(signal * (1 + amount * 10))

def simple_reverb(signal, mix=0.3):
    delays = [0.03, 0.05, 0.08, 0.011]
    output = signal.copy()

    for delay_time in delays:
        delay_samples = int(SAMPLE_RATE * delay_time)
        if delay_samples < len(signal):
            delayed = np.pad(signal[:-delay_samples], (delay_samples, 0))
            output += delayed * (mix / len(delays))

    return output