import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter
from scipy.signal.windows import hamming
import pandas as pd
import os

SAMPLE_RATE = 16000
ENERGY_THRESHOLD = 0.001

"""     Work FLow:      
        
        1. Reading .wav Audio files from test sub folder (about 10 speakers)
        2. Pre-process each .wav audio file:
            1. pre emphasize
            2. dc removal
            3. calculate energy (and ZCR if needed)
            4. classify silence segments in the file (by energy level)
            5. trim silence segments
        3. Returns processed data (format: {[audio data] : 'Speaker name'})
        4. Save the new data in another sub folder
        5. Moving to Features extractions
        
"""


def process_audio_folder(folder_path):
    processed_data = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".wav"):
                full_path = os.path.join(root, file)
                try:
                    data = process_audio_better(full_path)
                    processed_data[os.path.splitext(file)[0]] = data
                except Exception as e:
                    print(f"Error processing {file}: {e}")
    return processed_data

#TODO: To fix the trimming part, and to see if the energy array length is ok (the length of the array and the length of the audio array not the same)

def process_audio_better(file_path, win_length=1024, overlap=512):
    rate, audio = wavfile.read(file_path)
    audio = pre_emphasis_filter(audio)
    audio = remove_dc(audio)
    energy, _ = energy_rate(audio, win_length, overlap, rate)
    print(f"audio length before: {len(audio)}")
    audio = remove_silence(audio, energy, win_length, overlap)
    print(f"audio length After: {len(audio)}")
    return audio


def remove_silence(audio_data, energy, win_length, overlap, threshold=ENERGY_THRESHOLD):

    non_silent_audio = []
    for sample, energy_value in zip(audio_data, energy):
        # Check if energy value is above threshold
        if energy_value > threshold:
            # If yes, append the sample to non-silent audio
            non_silent_audio.append(sample)

    return np.array(non_silent_audio)


def pre_emphasis_filter(signal, alpha=0.97):
    return lfilter([1, -alpha], 1, signal)


# DC removal
def remove_dc(signal):
    return signal - np.mean(signal)


# Energy Rate calculation
def energy_rate(signal, win_length, overlap, sample_rate):
    step = win_length - overlap
    energy = []
    frames = range(0, len(signal) - win_length, step)
    for i in frames:
        windowed_signal = signal[i:i + win_length] * hamming(win_length)
        energy.append(np.sum(windowed_signal ** 2) / float(win_length))
        # Convert to numpy array for easier manipulation
    energy = np.array(energy)

    # Normalize the energy values
    normalized_energy = (energy - np.min(energy)) / (np.max(energy) - np.min(energy)) if np.max(energy) != np.min(
        energy) else np.zeros_like(energy)

    return normalized_energy, np.array(frames) / float(sample_rate)


folder_path = 'TEDLIUM_release1/test_short_clips'
results = process_audio_folder(folder_path)
print(results)


"""
def read_audio_folder(folder_path):
    wav_data = {}
    # Walk through all files and folders within the directory
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".wav"):
                path = os.path.join(root, file)
                # audio, zcr, zcr_time, energy, energy_time, data_output, classifications = process_audio(path)
                audio_class = process_audio(path)

    return wav_data



    

# Function to classify each frame based on a tuple of ZCR and energy
def classify_frame(energy):
    # Define clear, non-overlapping conditions for each classification
    if energy < ENERGY_THRESHOLD:
        return 'silence'  # Low ZCR and low energy indicate silence


# Main processing function
def process_audio(path, win_length=1024, overlap=512):
    sample_rate, audio = wavfile.read(path)
    audio = pre_emphasis_filter(audio)
    audio = remove_dc(audio)
    energy, energy_time = energy_rate(audio, win_length, overlap, sample_rate)

    data_output = list(energy)
    classifications = [classify_frame(energy) for energy in data_output]

    return audio, energy, energy_time, data_output, classifications


# Load the PCM file
def read_pcm_file(file_path, sample_rate=16000):
    with open(file_path, 'rb') as pcm_file:
        pcm_data = np.fromfile(pcm_file, dtype=np.int16)
    # Write to WAV file
    wavfile.write('phn_saf1.wav', sample_rate, pcm_data)
    return pcm_data


# Pre-emphasis filter



# Zero-Crossing Rate calculation
def zero_crossing_rate(signal, win_length, overlap, sample_rate):
    step = win_length - overlap
    zcr = []
    frames = range(0, len(signal) - win_length, step)
    for i in frames:
        windowed_signal = signal[i:i + win_length] * hamming(win_length)
        crossings = np.where(np.diff(np.sign(windowed_signal)))[0]
        zcr.append((len(crossings)) / float(win_length))
    return np.array(zcr), np.array(frames) / float(sample_rate)"""

