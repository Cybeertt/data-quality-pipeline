import csv
import json
from datetime import datetime, timedelta

def load_data(file_path):
    data = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                "id": row["contributor_id"],
                "name": row["name"],
                "country": row["country"],
                "score": int(row["score"]),
                "last_active": row["last_active"]
            })
    return data

def calculate_metrics(data):
    total = len(data)
    scores = [d["score"] for d in data]
    avg_score = round(sum(scores) / total, 2)

    now = datetime.now()
    cutoff = now - timedelta(days=30)

    active = 0
    inactive = 0
    for d in data:
        last_active = datetime.strptime(d["last_active"], "%Y-%m-%d")
        if last_active >= cutoff:
            active += 1
        else:
            inactive += 1

    countries = {}
    for d in data:
        country = d["country"]
        countries[country] = countries.get(country, 0) + 1

    low_quality = [d for d in data if d["score"] < 50]

    return {
        "total_contributors": total,
        "average_score": avg_score,
        "active_count": active,
        "inactive_count": inactive,
        "countries": countries,
        "flagged_low_quality": low_quality
    }

def generate_report(data, metrics):
    report = {
        "summary": metrics,
        "contributors": data
    }
    with open("output.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Report generated: output.json")

if __name__ == "__main__":
    data = load_data("sample_data.csv")
    metrics = calculate_metrics(data)
    generate_report(data, metrics)

    print(f"Total: {metrics['total_contributors']}")
    print(f"Avg score: {metrics['average_score']}")
    print(f"Active: {metrics['active_count']}")
    print(f"Inactive: {metrics['inactive_count']}")
    print(f"Countries: {metrics['countries']}")
    print(f"Low quality: {len(metrics['flagged_low_quality'])} contributors")
