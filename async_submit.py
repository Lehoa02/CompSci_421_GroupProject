# async_submit.py
import asyncio
import glob
from pathlib import Path

import aiohttp


AUDIO_GLOB = "data/audio/*.wav"
UPLOAD_URL = "http://127.0.0.1:5000/upload"


async def upload_one(session: aiohttp.ClientSession, path: str):
    file_path = Path(path)
    print(f"Uploading {file_path.name} ...")

    # open file in binary mode (sync open is fine here)
    with file_path.open("rb") as f:
        data = aiohttp.FormData()
        data.add_field("file", f, filename=file_path.name)

        async with session.post(UPLOAD_URL, data=data) as resp:
            if resp.status != 200:
                text = await resp.text()
                print(f"  ✖ Failed for {file_path.name}: {resp.status} {text}")
                return None

            json_data = await resp.json()
            print(f"  ✓ Done: {file_path.name} -> "
                  f"centroid={json_data['spectral_centroid_mean']:.0f}, "
                  f"bandwidth={json_data['spectral_bandwidth_mean']:.0f}, "
                  f"rms={json_data['rms_mean']:.3f}")
            return json_data


async def main():
    files = sorted(glob.glob(AUDIO_GLOB))
    if not files:
        print("No audio files found in data/audio")
        return

    print(f"Found {len(files)} files, uploading concurrently using aiohttp+asyncio...\n")

    async with aiohttp.ClientSession() as session:
        tasks = [upload_one(session, p) for p in files]
        results = await asyncio.gather(*tasks)

    # Filter out any failed uploads
    results = [r for r in results if r is not None]
    print(f"\nUploaded & analyzed {len(results)} files.")


if __name__ == "__main__":
    asyncio.run(main())
