# PLAN.md

## Architecture

1. Read CSV with companies (name + address)
2. For each company, query three data sources (mocked)
3. Collect contacts from all sources
4. Remove duplicates
5. Calculate confidence score (0-100)
6. Pick the best contact
7. Write results to a new CSV

## Data Sources (mocked)

- **Registry** → official owner names (reliable, no email/phone)
- **Listing** → phone numbers, sometimes names
- **Enrichment** → emails, phones, variable confidence

## Confidence Score (0-100)

| Criteria | Points |
|----------|--------|
| Provider already has confidence | use that value |
| Name matches across sources | +20 |
| Enrichment confirms registry name | +15 |
| Phone matches across sources | +20 |
| Name is generic ("info@", empty) | -30 |

**Threshold:** 70. Below that, contact is blank and `needs_human_review = true`.

## Privacy / Compliance

- ✅ Uses mock data only
- ❌ No scraping
- ❌ No email guessing

## Clarifying Questions

1. **Who is the priority contact?** (Owner, AP Manager, CFO)
2. **Email or phone?** (default: email)
3. **How many people for manual review?** (higher threshold = less review)