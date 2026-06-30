# Live Data Credentials and Placeholders

Status: Planning reference

Genesis must keep deterministic offline execution for tests and CI. Live data providers are optional until a sprint explicitly requires them.

## Current default

The current implementation uses deterministic providers and fixture-backed validation. No live credentials are required to run:

```text
python3 scripts/verify.py
```

## Sprint 3 useful credentials

Sprint 3 can produce placeholder supplier and cost intelligence without live credentials. Live data improves accuracy for supplier shortlists, price checks, marketplace fees, and demand validation.

Recommended optional credentials:

| Capability | Provider examples | Placeholder env vars |
| --- | --- | --- |
| LLM reasoning | OpenAI | `OPENAI_API_KEY` |
| Web search | Google Custom Search, SerpAPI, Tavily, Brave Search | `GOOGLE_CSE_API_KEY`, `GOOGLE_CSE_ID`, `SERPAPI_API_KEY`, `TAVILY_API_KEY`, `BRAVE_SEARCH_API_KEY` |
| Marketplace research | Amazon Product Advertising API, Flipkart affiliate/API where available | `AMAZON_ACCESS_KEY`, `AMAZON_SECRET_KEY`, `AMAZON_ASSOCIATE_TAG`, `FLIPKART_AFFILIATE_ID`, `FLIPKART_AFFILIATE_TOKEN` |
| Supplier research | IndiaMART, Alibaba, TradeIndia, ExportersIndia where API access is approved | `INDIAMART_API_KEY`, `ALIBABA_API_KEY`, `TRADEINDIA_API_KEY`, `EXPORTERSINDIA_API_KEY` |
| Shipping estimates | Shiprocket, Delhivery, India Post where available | `SHIPROCKET_EMAIL`, `SHIPROCKET_PASSWORD`, `DELHIVERY_API_KEY`, `INDIA_POST_API_KEY` |
| Currency and tax assumptions | Exchange-rate provider, GST/tax source if used | `EXCHANGE_RATE_API_KEY`, `GST_DATA_API_KEY` |
| Storage/docs | Google Drive, Google Sheets | `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_DRIVE_ACCESS_TOKEN`, `GOOGLE_DRIVE_REFRESH_TOKEN`, `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_DRIVE_FOLDER_ID`, `GOOGLE_SHEETS_ID` |

## Implemented live search backend

SerpAPI is supported for Sprint 2 live web and marketplace research.

```bash
export GENESIS_RESEARCH_PROVIDER=live_web
export GENESIS_SEARCH_PROVIDER=serpapi
export SERPAPI_API_KEY=<your-key>
```

For marketplace/source-targeted search:

```bash
export GENESIS_RESEARCH_PROVIDER=marketplace
export SERPAPI_API_KEY=<your-key>
```

Do not commit API keys into source control, fixtures, docs, or screenshots. Configure them only through runtime environment variables or GitHub repository secrets.

## Later sprint credentials

Sprint 4 Creative Studio:

- Image generation or design providers: `OPENAI_API_KEY`, `CANVA_API_KEY`, `FIGMA_ACCESS_TOKEN`

OpenAI Images are implemented as an optional Sprint 4 provider. Deterministic local PNG/SVG/PDF assets remain the default.

```bash
export GENESIS_CREATIVE_IMAGE_PROVIDER=openai
export OPENAI_API_KEY=<your-key>
export GENESIS_OPENAI_IMAGE_MODEL=gpt-image-2
export GENESIS_OPENAI_IMAGE_LIMIT=3
```

`GENESIS_OPENAI_IMAGE_LIMIT` controls how many premium PNG assets are generated per Creative Pack. Remaining assets are still generated deterministically so the workflow stays complete.

## Implemented Google Drive upload boundary

Google Drive upload is supported as an optional runtime integration for exporting generated assets, docs, and launch-pack files.

```bash
export GOOGLE_DRIVE_ACCESS_TOKEN=<oauth-access-token>
export GOOGLE_DRIVE_FOLDER_ID=<optional-folder-id>

python3 -m apps.cli.main drive upload .genesis-data/creative_assets/<creative-id>/product-hero.png --name product-hero.png
```

OAuth client ID and client secret identify the Google app, but they are not enough to upload files by themselves. A user consent flow must exchange them for an access token and, for longer-running automation, a refresh token. Genesis currently implements the upload boundary using `GOOGLE_DRIVE_ACCESS_TOKEN`; refresh-token automation can be added when the OAuth consent flow is introduced.

Never commit Google OAuth client secrets, access tokens, refresh tokens, service account JSON, or downloaded credential files.

Sprint 5 Marketing Engine:

- SEO/search providers: `GOOGLE_SEARCH_CONSOLE_CREDENTIALS`, `SEMRUSH_API_KEY`, `AHREFS_API_KEY`
- Email: `SENDGRID_API_KEY`, `MAILCHIMP_API_KEY`

Sprint 6 Publishing Engine:

- Meta: `META_APP_ID`, `META_APP_SECRET`, `META_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `FACEBOOK_PAGE_ID`
- Shopify: `SHOPIFY_STORE_URL`, `SHOPIFY_ACCESS_TOKEN`
- Amazon: `AMAZON_SELLER_PARTNER_APP_ID`, `AMAZON_SELLER_PARTNER_REFRESH_TOKEN`
- WhatsApp: `WHATSAPP_BUSINESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`

## Placeholder policy

- Tests must not require live credentials.
- CI must pass with deterministic providers.
- Missing credentials should trigger a clear fallback, not a crash.
- Live provider outputs must record source, confidence, retrieval time, and assumptions.
- Any live supplier or marketplace result must be treated as evidence, not truth, until founder or human review approves it.
