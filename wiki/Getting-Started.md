# Getting Started

## Dashboard

1. Clone the repo
2. Open `dashboard/maya-command-center.html` in Chrome or Edge
3. Allow microphone for voice
4. (Optional) Start a backend and set the URL in Settings

## Backend options

### OpenJarvis (recommended)
```bash
curl -fsSL https://open-jarvis.github.io/OpenJarvis/install.sh | bash
jarvis serve --port 8000
```

### Minimal stub
```bash
cd harness
pip install fastapi uvicorn
python backend_stub.py
```

## Next

See [Architecture](Architecture) and [Workflows](Workflows).
