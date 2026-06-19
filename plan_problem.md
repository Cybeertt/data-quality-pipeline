# PLAN.md

## Problem

Process contributor data and calculate quality metrics.

## Architecture

1. Read CSV with contributor data (id, name, country, score, last_active)
2. Calculate metrics:
   - Average score
   - Active vs inactive (active = last 30 days)
   - Countries distribution
   - Flag low-quality contributors (score < 50)
3. Generate JSON report
4. Optional: classify quality using AI (Claude API)

## Data Sources

- CSV file (sample_data.csv)
- No external APIs

## Output

JSON with:
- total_contributors
- average_score
- active_count
- inactive_count
- countries
- flagged_low_quality

## Why this matters

Hub.xyz processes data from 500k+ contributors worldwide. This pipeline shows how I'd handle data quality at scale.
