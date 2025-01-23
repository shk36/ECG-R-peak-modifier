# ECG-R-peak-modifier
ECG R-Peak Adjustment and Candidate Detection Algorithm

## Overview
This repository contains an implementation of an advanced algorithm to refine and adjust R-peaks in ECG signals. The algorithm processes raw ECG data by cleaning the signal, detecting initial R-peaks, and performing segment-based refinement to detect additional candidate R-peaks. It is designed for robust R-peak detection in noisy ECG signals.

## Features
- **Signal Cleaning:** Uses `biosppy` for preprocessing and noise removal.
- **Initial R-Peak Detection:** Employs `neurokit` for reliable initial peak detection.
- **Dynamic Thresholding:** Applies a height threshold (40% of signal amplitude range) to identify peaks between R-peaks.
- **Segment Analysis:** Refines R-peaks based on conditions such as proximity and signal value differences.
- **Candidate R-Peak Detection:** Detects and returns secondary peaks (R’-peaks) for advanced ECG analysis.
- **Duplicate Removal:** Ensures final R-peak and candidate R-peak lists are unique and non-overlapping.

## Algorithm Workflow
1. **ECG Signal Cleaning:**  
   Raw ECG signals are cleaned using `biosppy` to remove noise and artifacts.
2. **Initial R-Peak Detection:**  
   `neurokit` detects initial R-peaks in the cleaned ECG signal.
3. **Segment-Based Refinement:**  
   - Signal segments between consecutive R-peaks are extracted.
   - Additional peaks are detected within each segment using a dynamic height threshold.
   - Detected peaks replace the nearest or lower-value R-peak, if conditions are satisfied.
4. **Candidate Peak Extraction:**  
   If significant differences exist between initial and adjusted R-peaks, secondary peaks are detected and returned as R’-peaks.
5. **Final Peak Lists:**  
   Unique R-peaks and candidate R-peaks are returned for further analysis.

## Requirements
- Python 3.7+
- Required Python Libraries:
  - `numpy`
  - `neurokit2`
  - `scipy`

## Installation
Clone the repository and install the required dependencies:
```bash
git clone https://github.com/<username>/ecg-rpeak-adjustment.git
cd ecg-rpeak-adjustment
pip install -r requirements.txt
```

## Usage
```bash
import numpy as np
from ecg_rpeak_modifier import ECGRPeakModifier

# Load your ECG signal as a numpy array
ecg_signal = np.load("path_to_ecg_signal.npy")
sampling_rate = 250  # Example sampling rate

# Initialize the ECGRPeakModifier
modifier = ECGRPeakModifier(ecg_signal, srate=sampling_rate)

# Detect initial R-peaks
initial_rpeaks = modifier.get_rpeaks()

# Adjust R-peaks and detect candidate peaks
adjusted_rpeaks, candidate_rpeaks = modifier.adjust_rpeaks()

print("Adjusted R-Peaks:", adjusted_rpeaks)
print("Candidate R-Peaks:", candidate_rpeaks)
```

## Example Output
- Adjusted R-Peaks: Positions of refined R-peaks after processing.
- Candidate R-Peaks: Detected alternative R-peaks for detailed analysis.
