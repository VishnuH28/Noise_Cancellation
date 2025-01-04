# Real-Time Noise Cancellation System

## Introduction
This project implements a real-time noise cancellation system in Python that can process audio in two distinct scenarios:
1. Single Speaker Mode: Isolates and enhances one primary speaker while minimizing all other voices and background noise
2. Multiple Speaker Mode: Preserves multiple speaker voices while filtering out environmental noise

## Features
- Real-time audio processing with low latency
- Adaptive noise profiling and calibration
- Two operational modes (single/multiple speakers)
- Bandpass filtering and spectral subtraction
- WAV file output support
- Processing time monitoring
- Configurable audio parameters

## Requirements
- Python 3.7 or higher
- NumPy
- SciPy
- PyAudio
- A working microphone

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/noise-cancellation-system.git
cd noise-cancellation-system
```

2. Create and activate a virtual environment (recommended):
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install numpy scipy pyaudio
```

Note: If you encounter issues installing PyAudio:
- Windows: `pip install pipwin && pipwin install pyaudio`
- macOS: `brew install portaudio && pip install pyaudio`
- Linux: `sudo apt-get install python3-pyaudio`

## Usage

1. Run the script:
```bash
python noise.py
```

2. Follow the prompts:
   - Select mode (single_speaker/multiple_speakers)
   - Press Enter to start noise calibration (ensure silence during calibration)
   - Enter recording duration in seconds
   - Enter output filename (with .wav extension)

3. The system will:
   - Calibrate to ambient noise
   - Count down 3 seconds before recording
   - Record and process audio for the specified duration
   - Save the processed audio to a WAV file

## Technical Details

### Audio Processing Pipeline
1. **Input**: Real-time audio capture using PyAudio
2. **Noise Calibration**: Ambient noise profile creation
3. **Processing**:
   - Bandpass filtering (300-3400 Hz for single speaker)
   - Spectral subtraction for noise reduction
   - Signal reconstruction
4. **Output**: Processed audio saved as WAV file

### Parameters
- Sample Rate: 44100 Hz
- Chunk Size: 2048 samples
- Audio Format: 32-bit float
- Channels: Mono (1 channel)
- Filter Order: 4th order Butterworth

## Project Structure
```
noise-cancellation-system/
├── noise.py           # Main implementation file
├── requirements.txt   # Package dependencies
└── README.md         # Documentation
```

## Pushing to GitHub

If you haven't pushed this project to GitHub yet, follow these steps:

1. Create a new repository on GitHub:
   - Go to github.com
   - Click "New repository"
   - Name it "noise-cancellation-system"
   - Don't initialize with README (we have our own)

2. Create a requirements.txt file:
```bash
pip freeze > requirements.txt
```

3. Initialize local repository and push:
```bash
git init
git add .
git commit -m "Initial commit: Real-time noise cancellation system"
git branch -M main
git remote add origin https://github.com/your-username/noise-cancellation-system.git
git push -u origin main
```

## Contributing
Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- SciPy library for signal processing functions
- PyAudio for real-time audio processing
- NumPy for numerical computations