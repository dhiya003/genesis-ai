# Phase 2 Automation Hook Registry

| Manual Step | Phase 1 Tool | Phase 2 Automation Hook | Dependency |
| --- | --- | --- | --- |
| Lead capture | Google Form / sheet | Supabase lead table + API endpoint | Supabase |
| Instagram DM follow-up | Manual reply | Meta API conversation workflow | Meta API approval |
| Launch pack generation | CLI runner | Hosted API job | VPS / Cloudflare |
| Daily scorecard | Manual update | Scheduled analytics worker | Worker scheduler |
| Order confirmation | WhatsApp manual message | WhatsApp automation workflow | Approved WhatsApp provider |

Phase 1 must remain executable without these dependencies.
