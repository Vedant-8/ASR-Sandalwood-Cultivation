import os
import numpy as np
from pydub import AudioSegment
from scipy.signal import butter, lfilter
from scipy.io.wavfile import write
import tempfile

# Function to design a Butterworth bandpass filter
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

# Function to apply the filter to the signal
def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

# Function to clean noise from a single MP3 file and save the output
def clean_noise_from_mp3(input_file, output_file, lowcut=300.0, highcut=3000.0, order=6):
    # Convert MP3 to WAV for processing
    audio = AudioSegment.from_mp3(input_file)
    
    # Extract raw data and sampling rate
    temp_wav = tempfile.mktemp(suffix='.wav')
    audio.export(temp_wav, format="wav")
    
    # Read WAV file data
    from scipy.io import wavfile
    fs, data = wavfile.read(temp_wav)
    
    # Check if stereo and convert to mono if necessary
    if len(data.shape) > 1:
        data = data.mean(axis=1)  # Convert stereo to mono
    
    # Apply bandpass filter
    filtered_data = bandpass_filter(data, lowcut, highcut, fs, order)
    
    # Save filtered data to output WAV
    temp_filtered_wav = tempfile.mktemp(suffix='.wav')
    write(temp_filtered_wav, fs, np.int16(filtered_data))
    
    # Convert back to MP3 format
    filtered_audio = AudioSegment.from_wav(temp_filtered_wav)
    filtered_audio.export(output_file, format="mp3")
    
    # Clean up temporary files
    os.remove(temp_wav)
    os.remove(temp_filtered_wav)

# Main function to process all files in the folder
def process_folder(input_folder, output_folder, lowcut=300.0, highcut=3000.0, order=6):
    # Create the output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Process each MP3 file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp3"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename)
            
            print(f"Processing {filename}...")
            clean_noise_from_mp3(input_file, output_file, lowcut, highcut, order)
            print(f"Saved cleaned file to {output_file}")

    print("All files processed.")


input_folder = "Signal Processing/Raw audios"
output_folder = "Signal Processing/Filtered audios"
process_folder(input_folder, output_folder)
