import csv


def export_to_csv(records, filename="output.csv"):
    if not records:
        return
    keys = records[0].keys()
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)
    print(f"Exported {len(records)} records to {filename}")
