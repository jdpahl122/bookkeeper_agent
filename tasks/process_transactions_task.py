import csv
import hashlib
import os
import shutil
import tempfile
from datetime import datetime
from .base_task import BaseTask
import re

class ProcessTransactionsTask(BaseTask):
    def __init__(self, model, raw_csv="example/transactions.csv", processed_csv="example/processed_transactions.csv", summary_csv="example/monthly_summary.csv"):
        super().__init__(model)
        self.raw_csv = raw_csv
        self.processed_csv = processed_csv
        self.summary_csv = summary_csv

    def execute(self):
        processed_hashes = self._load_processed_hashes()
        new_processed_rows = []
        summary = {}

        with open(self.raw_csv, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                date = row['date']
                description = row['description']
                amount = float(row['amount'])
                txn_hash = self._generate_hash(date, description, amount)

                if txn_hash in processed_hashes:
                    continue  # Already processed

                month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")

                # Categorize
                prompt = (
                    f"Categorize this transaction for a SaaS startup:\n"
                    f"Description: '{description}'\n"
                    f"Amount: {amount}\n\n"
                    f"Instructions:\n"
                    f"- Only respond with a simple category label (e.g., 'Hosting Expenses', 'Subscription Revenue', 'Office Supplies').\n"
                    f"- No explanations. One line only."
                )
                category = self.model.invoke(prompt).strip().split("\n")[0]
                category = re.sub(r'[\"\']', '', category).strip().title()

                # Determine type
                if amount < 0:
                    type_ = "Accounts Payable" if "Expense" in category or "Supplies" in category else "Expense"
                else:
                    type_ = "Accounts Receivable" if "Revenue" in category else "Revenue"

                new_processed_rows.append({
                    "date": date,
                    "description": description,
                    "amount": amount,
                    "category": category,
                    "type": type_,
                    "month": month,
                })

                # Update monthly summary
                if month not in summary:
                    summary[month] = {
                        "Accounts Payable": 0,
                        "Accounts Receivable": 0,
                        "Revenue": 0,
                        "Expense": 0
                    }
                summary[month][type_] += amount

        # Append new processed rows to file
        self._append_processed(new_processed_rows)

        # Update summary
        self._write_summary(summary)

        print("\n====== Monthly Financial Summary ======")
        for month, totals in summary.items():
            net_income = (totals['Revenue'] + totals['Accounts Receivable']) + (totals['Expense'] + totals['Accounts Payable'])
            print(f"\n{month}:")
            print(f"  Total Accounts Payable: {totals['Accounts Payable']:.2f}")
            print(f"  Total Accounts Receivable: {totals['Accounts Receivable']:.2f}")
            print(f"  Total Revenue: {totals['Revenue']:.2f}")
            print(f"  Total Expenses: {totals['Expense']:.2f}")
            print(f"  Net Income: {net_income:.2f}")

        return "\nProcessing complete."

    def _generate_hash(self, date, description, amount):
        raw = f"{date}{description}{amount}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _load_processed_hashes(self):
        hashes = set()
        if not os.path.isfile(self.processed_csv):
            return hashes
        with open(self.processed_csv, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                h = self._generate_hash(row['date'], row['description'], row['amount'])
                hashes.add(h)
        return hashes

    def _append_processed(self, new_rows):
        file_exists = os.path.isfile(self.processed_csv)
        with open(self.processed_csv, mode='a', newline='') as file:
            fieldnames = ['date', 'description', 'amount', 'category', 'type', 'month']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerows(new_rows)

    def _write_summary(self, summary):
        existing_summary = {}

        # Load existing monthly summaries if file exists
        if os.path.isfile(self.summary_csv):
            with open(self.summary_csv, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing_summary[row['month']] = {
                        'accounts_payable': float(row['accounts_payable']),
                        'accounts_receivable': float(row['accounts_receivable']),
                        'revenue': float(row['revenue']),
                        'expenses': float(row['expenses']),
                        'net_income': float(row['net_income'])
                    }

        # Merge new summary into existing summary
        for month, totals in summary.items():
            if month not in existing_summary:
                existing_summary[month] = {
                    'accounts_payable': 0.0,
                    'accounts_receivable': 0.0,
                    'revenue': 0.0,
                    'expenses': 0.0,
                    'net_income': 0.0
                }

            existing_summary[month]['accounts_payable'] += totals['Accounts Payable']
            existing_summary[month]['accounts_receivable'] += totals['Accounts Receivable']
            existing_summary[month]['revenue'] += totals['Revenue']
            existing_summary[month]['expenses'] += totals['Expense']
            existing_summary[month]['net_income'] = (
                existing_summary[month]['revenue'] + existing_summary[month]['accounts_receivable']
                + existing_summary[month]['expenses'] + existing_summary[month]['accounts_payable']
            )

        # Rewrite the summary file
        with open(self.summary_csv, mode='w', newline='') as file:
            fieldnames = ['month', 'accounts_payable', 'accounts_receivable', 'revenue', 'expenses', 'net_income']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for month, totals in sorted(existing_summary.items()):
                writer.writerow({
                    'month': month,
                    'accounts_payable': f"{totals['accounts_payable']:.2f}",
                    'accounts_receivable': f"{totals['accounts_receivable']:.2f}",
                    'revenue': f"{totals['revenue']:.2f}",
                    'expenses': f"{totals['expenses']:.2f}",
                    'net_income': f"{totals['net_income']:.2f}"
                })
