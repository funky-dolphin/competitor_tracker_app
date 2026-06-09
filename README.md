# AI Signal Tracker

A static dashboard that monitors RSS feeds from major AI companies and classifies signals as **Hot**, **New**, or **Watch**.

## Architecture

```
ingest.py          ← run locally to pull feeds
public/signals.json ← flat JSON read by the React app
src/               ← React + Vite frontend
```

No database. No AI API. The Python script writes a JSON file; the React app reads it.

## Local development

### 1. Fetch signals

```bash
pip install -r requirements.txt
python ingest.py
```

This writes `public/signals.json` with up to 5 recent entries per company.

### 2. Run the frontend

```bash
npm install
npm run dev
```

Open http://localhost:5173.

### Keeping signals fresh

Run `python ingest.py` whenever you want a fresh pull. To automate it locally, add a cron job:

```
# refresh every hour
0 * * * * cd /path/to/competitor-tracker-app && python ingest.py
```

## Deploying to Vercel

1. Push the repo to GitHub.
2. In Vercel, import the repository.
3. Framework preset: **Vite**. Build command: `npm run build`. Output directory: `dist`.
4. Deploy.

Run `python ingest.py` locally, commit the updated `public/signals.json`, and push to trigger a redeploy — or use a GitHub Action to run the script on a schedule and auto-commit the JSON.

## Signal classification

| Badge | Keywords matched |
|-------|-----------------|
| **Hot** | launch, introducing, announcing, released, new model, breakthrough, unveil |
| **Watch** | partnership, funding, acquisition, rumor, leak, hiring |
| **New** | everything else |

## Companies tracked

| Company | Source |
|---------|--------|
| OpenAI | openai.com/blog/rss.xml |
| Anthropic | anthropic.com/rss.xml |
| Google | blog.google/technology/ai/rss |
| Microsoft | blogs.microsoft.com/ai/feed |
| Apple | apple.com/newsroom/rss-feed.rss |
| Perplexity | blog.perplexity.ai/rss |
| Meta | Google News RSS search |
| Amazon | Google News RSS search |
