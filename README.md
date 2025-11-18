# 🔧 Quick Setup Instructions (For Connor)

These steps will get the Celery worker running on your laptop so we can process audio files in parallel.

---

## 1. Clone the repository

```bash
git clone https://github.com/Lehoa02/CompSci_421_GroupProject.git
cd CompSci_421_GroupProject
```

## 2. Create and activate a virtual environment

macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```
Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```
## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Update Redis URL in celery_app.py

My laptop’s local IP address: 143.200.36.6
Then edit the file:

```bash
REDIS_URL = "redis://<ANA_IP>:6379/0"
```
You do not need to run Redis — you connect to mine Redis instance.

## 5. Start the Celery worker

From the project folder:
```bash
celery -A celery_app.celery_app worker --loglevel=INFO --concurrency=4
```

If it works, you will see:
```bash
[INFO] celery@your-machine ready
```
Leave this terminal open — it is your Celery worker.

## 6. How we use async processing
There are two ways we send work to your worker:

6.1. Async batch submitter (uses asyncio + aiohttp)

I can run:
```bash
python async_submit.py
```
This script:

-finds all .wav files in data/audio/

-uses aiohttp + asyncio.gather to upload them concurrently to the Flask /upload endpoint

-each upload triggers a Celery task on your worker (compute_dft_features)

-results are written into dft_features.csv and shown on the dashboard

You’ll see tasks appear in your worker terminal as they are processed in parallel.

6.2. (Optional) Synchronous submitter
```bash
python submit_jobs.py
```
This still uses Celery, but submits files one by one and waits for each result.
We mainly keep it to show the difference vs. the async version.

---

## Bonus
The website of free music .wav format: 
```bash
https://cambridge-mt.com/ms3/mtk/
```
