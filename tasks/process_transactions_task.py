import csv
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
        processed_ids = self._load_processed_ids()
        new_processed_rows = []
        summary = {}

        with open(self.raw_csv, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                transaction_id = row['transaction_id']

                if transaction_id in processed_ids:
                    continue  # Already processed

                date = row['date']
                description = row['description']
                amount = float(row['amount'])
                month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")

                # Categorize
                prompt = (
                    f"You are a professional bookkeeper categorizing financial transactions for a SaaS startup.\n"
                    f"Transaction Description: '{description}'\n"
                    f"Transaction Amount: {amount}\n\n"
                    f"Categorization Instructions:\n"
                    f"- If the description mentions 'Stripe', treat it as 'Revenue' (not Accounts Receivable).\n"
                    f"- If the description includes 'invoice', 'payment from customer', or similar, treat as 'Subscription Revenue' under Accounts Receivable.\n"
                    f"- If the amount is negative and description mentions 'consulting', 'contractor', or 'services', treat as 'Professional Services' under Accounts Payable.\n"
                    f"- If the amount is negative and description includes 'rent', 'subscription', 'domain', 'hosting', 'software', treat as 'Operating Expenses' under Accounts Payable.\n"
                    f"- Otherwise, categorize with the best fitting label.\n"
                    f"- Only respond with the CATEGORY LABEL, no explanations, no quotes.\n"
                    f"- Examples of valid outputs: 'Subscription Revenue', 'Revenue', 'Professional Services', 'Office Expenses', 'Hosting Expenses'."
                )
                category = self.model.invoke(prompt).strip().split("\n")[0]
                category = re.sub(r'[\"\']', '', category).strip().title()

                # Determine type
                if amount < 0:
                    if "Expense" in category or "Services" in category:
                        type_ = "Accounts Payable"
                    else:
                        type_ = "Expense"
                else:
                    if "Revenue" in category:
                        type_ = "Revenue"
                    else:
                        type_ = "Accounts Receivable"

                new_processed_rows.append({
                    "transaction_id": transaction_id,
                    "date": date,
                    "description": description,
                    "amount": amount,
                    "category": category,
                    "type": type_,
                    "month": month,
                    "due_date": date,  # Default for now; will Net 30 later
                    "payment_status": "Unpaid"
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

        # Update monthly summary
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

    def _load_processed_ids(self):
        ids = set()
        if not os.path.isfile(self.processed_csv):
            return ids
        with open(self.processed_csv, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'transaction_id' in row:
                    ids.add(row['transaction_id'])
        return ids

    def _append_processed(self, new_rows):
        file_exists = os.path.isfile(self.processed_csv)
        with open(self.processed_csv, mode='a', newline='') as file:
            fieldnames = ['transaction_id', 'date', 'description', 'amount', 'category', 'type', 'month', 'due_date', 'payment_status']
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
