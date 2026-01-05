import numpy as np
from scipy.signal import stft, istft

SAMPLE_RATE = 0
BLOCK = 0
reverb_buffers = []  # Initialize as empty list
wacky_buffer = np.array([])
wacky_buffer_size = 0

def setup(sample_rate, block):
    global SAMPLE_RATE, BLOCK, reverb_buffers
    SAMPLE_RATE = sample_rate
    BLOCK = block
    # Create buffers for reverb delays
    delays = [0.03, 0.05, 0.08, 0.11]
    reverb_buffers = [np.zeros(int(SAMPLE_RATE * d)) for d in delays]
    wacky_buffer_size = 128

def volume_effect(signal, gain=1.5):
    return signal * gain

def distortion_effect(signal, amount=0.5):
    return np.tanh(signal * (1 + amount * 10))

def simple_reverb(signal, mix=0.3):
    global reverb_buffers
    if not reverb_buffers:
        return signal
    output = signal.copy()
    signal_len = len(signal)
    
    for buffer in reverb_buffers:
        buffer_len = len(buffer)
        
        if signal_len <= buffer_len:
            output += buffer[:signal_len] * (mix / len(reverb_buffers))
            buffer[:-signal_len] = buffer[signal_len:]
            buffer[-signal_len:] = signal
        else:
            output[:buffer_len] += buffer * (mix / len(reverb_buffers))
            buffer[:] = signal[-buffer_len:]
    
    return output

def pitch_shift_phase_vocoder(signal, semitones, block_size = 512):
    global BLOCK
    if block_size > BLOCK:
        block_size = BLOCK

    pitch_ratio = 2 ** (semitones / 12.0)
    nperseg = min(block_size, len(signal))  # avoid nperseg > signal
    f, t, Zxx = stft(signal, fs=SAMPLE_RATE, nperseg=nperseg)
    
    # frequency bin interpolation
    bins = np.arange(Zxx.shape[0])
    new_bins = bins / pitch_ratio
    shifted_Zxx = np.zeros_like(Zxx, dtype=complex)
    for col in range(Zxx.shape[1]):
        shifted_Zxx[:, col] = np.interp(
            bins, new_bins, Zxx[:, col].real
        ) + 1j * np.interp(bins, new_bins, Zxx[:, col].imag)
    
    _, shifted = istft(shifted_Zxx, fs=SAMPLE_RATE, nperseg=nperseg)
    return shifted[:len(signal)]

def ten_dollar_mic(signal):
    return pitch_shift_phase_vocoder(signal, -10, 10)

def wacky(signal, buffer_time=0.5):
    global wacky_buffer, wacky_buffer_size
    wacky_buffer = np.append(wacky_buffer, signal)
    buffer_len = int(SAMPLE_RATE * buffer_time)
    
    if buffer_time <= 0:
        buffer_time = 0.1

    if len(wacky_buffer) >= buffer_len:
        output = wacky_buffer[:buffer_len][::-1]
        wacky_buffer = wacky_buffer[len(signal):]
        return output[:len(signal)]
    else:
        return np.zeros_like(signal)