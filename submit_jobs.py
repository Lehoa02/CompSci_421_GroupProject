import csv
import glob
from tasks import compute_dft_features

def submit_folder(folder_glob_pattern: str):
    files = glob.glob(folder_glob_pattern)
    print(f"Found {len(files)} files")

    async_results = []
    for f in files:
        res = compute_dft_features.delay(f)
        async_results.append(res)
        print(f"Queued task {res.id} for {f}")

    # Collect all results and save to CSV
    rows = []
    for res in async_results:
        result = res.get(timeout=300)
        rows.append(result)

    fieldnames = ["file_path", "sr", "spectral_centroid_mean",
                  "spectral_bandwidth_mean", "rms_mean"]
    with open("dft_features.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("Saved features to dft_features.csv")

if __name__ == "__main__":
    submit_folder("data/audio/*.wav")
