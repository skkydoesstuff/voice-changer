import numpy as np
from scipy.signal import stft, istft

SAMPLE_RATE = 0
reverb_buffers = []  # Initialize as empty list
wacky_buffer = np.array([])
wacky_buffer_size = 0

def setup(sample_rate):
    global SAMPLE_RATE, reverb_buffers
    SAMPLE_RATE = sample_rate
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

def pitch_shift_phase_vocoder(signal, semitones):
    # Convert semitones to ratio (12 semitones = 1 octave)
    pitch_ratio = 2 ** (semitones / 12.0)
    
    # Short-time Fourier transform
    f, t, Zxx = stft(signal, fs=SAMPLE_RATE, nperseg=2048)
    
    # Shift frequency bins
    shifted_Zxx = np.zeros_like(Zxx)
    for i in range(Zxx.shape[0]):
        new_i = int(i * pitch_ratio)
        if 0 <= new_i < Zxx.shape[0]:
            shifted_Zxx[new_i] += Zxx[i]
    
    # Inverse transform back to audio
    _, shifted = istft(shifted_Zxx, fs=SAMPLE_RATE)
    
    return shifted[:len(signal)]  # Trim to original length

def wacky(signal, buffer_time=0.5):
    global wacky_buffer, wacky_buffer_size
    wacky_buffer = np.append(wacky_buffer, signal)
    buffer_len = int(SAMPLE_RATE * buffer_time)
    
    if len(wacky_buffer) >= buffer_len:
        output = wacky_buffer[:buffer_len][::-1]
        wacky_buffer = wacky_buffer[len(signal):]
        return output[:len(signal)]
    else:
        return np.zeros_like(signal)