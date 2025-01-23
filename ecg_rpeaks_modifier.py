import numpy as np
import neurokit2 as nk
from scipy.signal import find_peaks


class ECGRPeakModifier:
    """
    A class to adjust R-peak positions in an ECG signal by detecting peaks within segments 
    and replacing R-peaks based on specific conditions.
    """

    def __init__(self, ecg_arr, srate=250):
        """
        Initialize the ECGRPeakModifier class.

        Parameters:
        ecg_arr (numpy.ndarray): The raw ECG signal.
        srate (int): Sampling rate of the ECG signal in Hz (default: 250).
        """
        self.ecg_arr = ecg_arr
        self.srate = srate
        self.ecg_clean_method = 'biosppy' # Method for cleaning the ECG signal
        self.ecg_peaks_method = 'neurokit' # Method for detecting R-peaks
        self.height_threshold = 0.4 # Threshold for peak height detection


    def get_rpeaks(self):
        """
        Clean the ECG signal and detect initial R-peaks.

        Returns:
        numpy.ndarray: Detected R-peak indices, or False if detection fails.
        """
        self.ecg_arr = nk.ecg_clean(self.ecg_arr, sampling_rate=self.srate, method=self.ecg_clean_method)
        try:
            _, peaks = nk.ecg_peaks(self.ecg_arr, sampling_rate=self.srate, method=self.ecg_peaks_method, correct_artifacts=True)
            self.rpeaks = peaks['ECG_R_Peaks']
        except:
            self.rpeaks = []

        return self.rpeaks
        

    def adjust_rpeaks(self):
        """
        Adjust R-peak positions based on detected peaks within the segments between R-peaks.

        Returns:
        tuple: A tuple containing adjusted R-peak positions and a list of candidate R-peaks.
        """
        if len(self.rpeaks) == 0:
            return False, False
        
        adjusted_rpeaks = self.rpeaks.copy()
        candidate_rpeaks = []

        # Calculate the height threshold for peak detection
        peak_height = (np.max(self.ecg_arr) - np.min(self.ecg_arr)) * self.height_threshold

        for i in range(len(self.rpeaks) - 1):
            # Extract the segment between two R-peaks
            segment = self.ecg_arr[self.rpeaks[i]:self.rpeaks[i + 1]]
            rpeak_left = self.ecg_arr[self.rpeaks[i]]
            rpeak_right = self.ecg_arr[self.rpeaks[i + 1]]

            try:
                # Detect peaks within the segment using the height threshold
                peaks, _ = find_peaks(segment, height=peak_height)
            except Exception as e:
                print(f"Error finding peaks: {e}")
                continue

            if len(peaks) == 1:
                abs_peak_idx = self.rpeaks[i] + peaks[0]
                left_diff = segment[peaks[0]] - rpeak_left
                right_diff = segment[peaks[0]] - rpeak_right

                if left_diff >= 0 and right_diff >= 0:
                    # Replace the closer R-peak with the detected peak
                    if (abs_peak_idx - self.rpeaks[i]) > (self.rpeaks[i + 1] - abs_peak_idx):
                        adjusted_rpeaks[i + 1] = abs_peak_idx
                    else:
                        adjusted_rpeaks[i] = abs_peak_idx

                elif left_diff * right_diff <= 0:
                    # Replace the lower R-peak with the detected peak
                    if rpeak_left < rpeak_right:
                        adjusted_rpeaks[i] = abs_peak_idx
                    else:
                        adjusted_rpeaks[i + 1] = abs_peak_idx

            elif len(peaks) == 2:
                abs_peak_idx_1 = self.rpeaks[i] + peaks[0]
                abs_peak_idx_2 = self.rpeaks[i] + peaks[1]

                diff_1 = segment[peaks[0]] - rpeak_left
                diff_2 = segment[peaks[1]] - rpeak_right

                if diff_1 > 0 and diff_2 > 0:
                    # Replace R-peaks with the detected peaks
                    adjusted_rpeaks[i] = abs_peak_idx_1
                    adjusted_rpeaks[i + 1] = abs_peak_idx_2

        # Check the difference between original and adjusted R-peaks
        diff = np.abs(self.rpeaks - adjusted_rpeaks)
        diff = diff[diff > 0]

        if len(diff) >= len(self.rpeaks) * 0.5:
            for i in range(len(adjusted_rpeaks) - 1):
                segment = self.ecg_arr[adjusted_rpeaks[i]:adjusted_rpeaks[i + 1]]
                try:
                    peaks, _ = find_peaks(segment)
                    max_peak_idx = np.argmax(segment[peaks])
                    max_peaks = adjusted_rpeaks[i] + peaks[max_peak_idx]
                    candidate_rpeaks.append(max_peaks)
                except Exception as e:
                    print(f"Error processing candidate peaks: {e}")
                    continue

            # Remove duplicates from candidate R-peaks
            candidate_rpeaks = [peak for peak in candidate_rpeaks if peak not in adjusted_rpeaks]
            return adjusted_rpeaks, candidate_rpeaks

        return adjusted_rpeaks, False