import numpy as np
import librosa
from celery_app import celery_app

TARGET_SR = 44100
FRAME_SIZE = 4096
HOP_LENGTH = 2048


@celery_app.task(bind=True)
def compute_dft_features(self, file_path: str) -> dict:
    self.update_state(state="PROGRESS", meta={"stage": "loading", "file": file_path})

    y, sr = librosa.load(file_path, sr=None, mono=True)

    if sr != TARGET_SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=TARGET_SR)
        sr = TARGET_SR

    self.update_state(state="PROGRESS", meta={"stage": "stft", "file": file_path})

    stft = librosa.stft(y, n_fft=FRAME_SIZE, hop_length=HOP_LENGTH)
    magnitude = np.abs(stft)

    spectral_centroid = librosa.feature.spectral_centroid(S=magnitude, sr=sr)
    spectral_bandwidth = librosa.feature.spectral_bandwidth(S=magnitude, sr=sr)

    # 👇 Fix: use waveform for RMS with correct frame_length
    rms = librosa.feature.rms(
        y=y,
        frame_length=FRAME_SIZE,
        hop_length=HOP_LENGTH,
    )

    features = {
        "file_path": file_path,
        "sr": int(sr),
        "spectral_centroid_mean": float(np.mean(spectral_centroid)),
        "spectral_bandwidth_mean": float(np.mean(spectral_bandwidth)),
        "rms_mean": float(np.mean(rms)),
    }

    return features
