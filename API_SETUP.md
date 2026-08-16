# API setup

The application is free-first. You do not need an API key to install the project, but live market data depends on an available public/provider endpoint.

## Alpha Vantage

If you want to use Alpha Vantage, create a free API key yourself and add it locally:

```text
ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
```

Put that line in `.env`. Never paste a real key into source code or commit it to GitHub.

The repository includes `.env.example` as a template.

## Provider behavior

The app tries cached data first, then Yahoo Finance, then Alpha Vantage if a key is configured. It never silently creates synthetic prices. If all providers fail, the research run stops and explains what failed.

Because free providers have rate limits and availability changes, the SQLite cache is important. Use **Force refresh** only when you actually need new data.

## No other keys required

This version intentionally has no AI/LLM API, brokerage credential, paid news service, or paid market-data requirement.
