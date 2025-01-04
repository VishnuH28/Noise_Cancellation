import numpy as np
import pyaudio
import wave
import time
from scipy import signal
from threading import Thread, Event
import queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NoiseReducer:
    def __init__(self, mode='single_speaker', chunk_size=2048, sample_rate=44100):
        """
        Initialize the noise reduction system.
        
        Args:
            mode (str): 'single_speaker' or 'multiple_speakers'
            chunk_size (int): Size of audio chunks to process
            sample_rate (int): Audio sample rate
        """
        self.mode = mode
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.audio_queue = queue.Queue(maxsize=100)  # Limit queue size
        self.output_frames = []
        
        # Audio stream parameters
        self.format = pyaudio.paFloat32
        self.channels = 1
        self.p = pyaudio.PyAudio()
        
        # Initialize noise profile
        self.noise_profile = None
        self.is_calibrating = False
        
        # Recording control
        self.recording = False
        self.stop_flag = Event()
        
        # Pre-compute filter coefficients
        nyquist = self.sample_rate / 2
        self.b, self.a = signal.butter(4, [300/nyquist, 3400/nyquist], btype='band')
        
    def callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        if self.recording or self.is_calibrating:
            try:
                audio_chunk = np.frombuffer(in_data, dtype=np.float32)
                
                if self.recording:
                    # Process audio in callback for better timing
                    processed = self.process_chunk(audio_chunk)
                    self.output_frames.append(processed)
                else:
                    self.audio_queue.put(audio_chunk)
                    
            except Exception as e:
                logger.error(f"Error in callback: {e}")
                
        return (in_data, pyaudio.paContinue)
    
    def process_chunk(self, chunk):
        """Process a single chunk of audio data"""
        # Apply pre-computed bandpass filter
        filtered = signal.lfilter(self.b, self.a, chunk)
        
        if self.noise_profile is not None:
            # Simple spectral subtraction
            chunk_spec = np.fft.rfft(filtered)
            noise_spec = np.fft.rfft(self.noise_profile)
            
            # Compute magnitude spectra
            chunk_mag = np.abs(chunk_spec)
            noise_mag = np.abs(noise_spec)
            
            # Subtract noise floor
            clean_mag = np.maximum(chunk_mag - noise_mag, 0)
            
            # Reconstruct signal
            clean_spec = clean_mag * np.exp(1j * np.angle(chunk_spec))
            filtered = np.fft.irfft(clean_spec)
        
        return np.clip(filtered, -1, 1)
    
    def calibrate_noise(self, duration=2.0):
        """Calibrate noise profile from ambient sound"""
        logger.info("Starting noise calibration...")
        self.is_calibrating = True
        self.audio_queue.queue.clear()
        
        # Calculate required number of chunks
        chunks_needed = int(duration * self.sample_rate / self.chunk_size)
        noise_chunks = []
        
        # Start stream for calibration
        stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self.callback
        )
        
        start_time = time.time()
        while len(noise_chunks) < chunks_needed and (time.time() - start_time) < duration + 0.5:
            try:
                chunk = self.audio_queue.get(timeout=0.1)
                noise_chunks.append(chunk)
            except queue.Empty:
                continue
        
        stream.stop_stream()
        stream.close()
        
        if noise_chunks:
            self.noise_profile = np.mean(np.vstack(noise_chunks), axis=0)
            logger.info("Noise calibration completed")
        else:
            logger.warning("No audio chunks received during calibration")
            
        self.is_calibrating = False
    
    def record(self, duration, filename):
        """Record and process audio for specified duration"""
        logger.info(f"Starting recording to {filename}")
        self.recording = True
        self.output_frames = []
        
        # Open recording stream
        stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self.callback
        )
        
        # Wait for specified duration
        time.sleep(duration)
        
        # Stop recording
        self.recording = False
        stream.stop_stream()
        stream.close()
        
        if self.output_frames:
            # Combine all frames
            audio_data = np.concatenate(self.output_frames)
            
            # Convert to int16 for wave file
            audio_data = (audio_data * 32767).astype(np.int16)
            
            # Save to file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 2 bytes for int16
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            actual_duration = len(audio_data) / self.sample_rate
            logger.info(f"Recording saved to {filename}")
            logger.info(f"Actual recording duration: {actual_duration:.2f} seconds")
        else:
            logger.warning("No audio frames captured")
    
    def cleanup(self):
        """Cleanup resources"""
        self.p.terminate()

def main():
    """Main function to demonstrate usage"""
    # Initialize noise reducer
    mode = input("Select mode (single_speaker/multiple_speakers): ").strip()
    noise_reducer = NoiseReducer(mode=mode)
    
    try:
        # Calibrate noise
        input("Press Enter to start noise calibration (ensure silence)...")
        noise_reducer.calibrate_noise()
        
        # Get recording parameters
        duration = float(input("Enter recording duration (seconds): "))
        filename = input("Enter output filename (.wav): ")
        
        # Countdown
        print("Recording will start in 3 seconds...")
        time.sleep(3)
        print("Recording...")
        
        # Record audio
        noise_reducer.record(duration, filename)
        print("Recording completed")
        
    except KeyboardInterrupt:
        print("\nRecording interrupted by user")
    except Exception as e:
        logger.error(f"Error during recording: {e}")
    finally:
        noise_reducer.cleanup()

if __name__ == "__main__":
    main()