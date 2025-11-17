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

Ask me for my laptop’s local IP address
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

## 6. Let me run the job submitter

```bash
python submit_jobs.py
```
You should see tasks show up in your worker window as they are processed.
