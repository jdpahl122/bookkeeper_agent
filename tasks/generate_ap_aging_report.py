import csv
from datetime import datetime

class GenerateAPAgingReportTask:
    def __init__(self, csv_file="example/processed_transactions.csv"):
        self.csv_file = csv_file

    def execute(self):
        today = datetime.now()
        aging_buckets = {
            "0-30 days": [],
            "31-60 days": [],
            "61-90 days": [],
            "90+ days": []
        }

        with open(self.csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['type'] != "Accounts Payable" or row['payment_status'] == "Paid":
                    continue

                due_date_str = row.get('due_date') or row.get('date')
                if not due_date_str:
                    continue

                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                delta_days = (today - due_date).days

                if delta_days <= 30:
                    aging_buckets["0-30 days"].append(row)
                elif 31 <= delta_days <= 60:
                    aging_buckets["31-60 days"].append(row)
                elif 61 <= delta_days <= 90:
                    aging_buckets["61-90 days"].append(row)
                else:
                    aging_buckets["90+ days"].append(row)

        print("\n====== Accounts Payable Aging Report ======")
        for bucket, transactions in aging_buckets.items():
            print(f"\n{bucket}: {len(transactions)} transaction(s)")
            for t in transactions:
                print(f"- {t['description']} | Due: {t['due_date'] or t['date']} | Amount: {t['amount']}")

        return "AP Aging report generated successfully."
