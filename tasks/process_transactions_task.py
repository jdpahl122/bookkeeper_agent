import csv
import shutil
import tempfile
from datetime import datetime
from .base_task import BaseTask
import os

class ProcessTransactionsTask(BaseTask):
    def __init__(self, model, raw_csv="example/transactions.csv", processed_csv="example/processed_transactions.csv", summary_csv="example/monthly_summary.csv"):
        super().__init__(model)
        self.raw_csv = raw_csv
        self.processed_csv = processed_csv
        self.summary_csv = summary_csv

    def execute(self):
        processed_rows = []
        summary = {}

        with open(self.raw_csv, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                date = row['date']
                description = row['description']
                amount = float(row['amount'])
                month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")

                # Categorize transaction
                prompt = (
                    f"Categorize this transaction for a SaaS startup:\n"
                    f"Description: '{description}'\n"
                    f"Amount: {amount}\n\n"
                    f"Instructions:\n"
                    f"- Only respond with a simple category label (e.g., 'Hosting Expenses', 'Subscription Revenue', 'Office Supplies').\n"
                    f"- No explanations. One line only."
                )
                category = self.model.invoke(prompt).strip().split("\n")[0]
                category = category.replace('"', '').replace("'", '').strip()

                # Determine type
                if amount < 0:
                    type_ = "Accounts Payable" if "Expense" in category or "Supplies" in category else "Expense"
                else:
                    type_ = "Accounts Receivable" if "Revenue" in category else "Revenue"

                processed_rows.append({
                    "date": date,
                    "description": description,
                    "amount": amount,
                    "category": category,
                    "type": type_,
                    "month": month,
                })

                # Update monthly summaries
                if month not in summary:
                    summary[month] = {
                        "Accounts Payable": 0,
                        "Accounts Receivable": 0,
                        "Revenue": 0,
                        "Expense": 0
                    }

                summary[month][type_] += amount

        # Write processed transactions to processed CSV
        with tempfile.NamedTemporaryFile('w', delete=False, newline='') as tmpfile:
            fieldnames = ['date', 'description', 'amount', 'category', 'type', 'month']
            writer = csv.DictWriter(tmpfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_rows)

        shutil.move(tmpfile.name, self.processed_csv)

        # Pretty Print Summary to Terminal
        print("\n====== Monthly Financial Summary ======")
        for month, totals in summary.items():
            net_income = (totals['Revenue'] + totals['Accounts Receivable']) + (totals['Expense'] + totals['Accounts Payable'])
            print(f"\n{month}:")
            print(f"  Total Accounts Payable: {totals['Accounts Payable']:.2f}")
            print(f"  Total Accounts Receivable: {totals['Accounts Receivable']:.2f}")
            print(f"  Total Revenue: {totals['Revenue']:.2f}")
            print(f"  Total Expenses: {totals['Expense']:.2f}")
            print(f"  Net Income: {net_income:.2f}")

        # Save/update monthly_summary.csv
        self._write_summary(summary)

        return f"\nProcessing complete. Updated {self.processed_csv} and {self.summary_csv}."

    def _write_summary(self, summary):
        file_exists = os.path.isfile(self.summary_csv)
        with open(self.summary_csv, mode='a', newline='') as file:
            fieldnames = ['month', 'accounts_payable', 'accounts_receivable', 'revenue', 'expenses', 'net_income']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for month, totals in summary.items():
                net_income = (totals['Revenue'] + totals['Accounts Receivable']) + (totals['Expense'] + totals['Accounts Payable'])
                writer.writerow({
                    'month': month,
                    'accounts_payable': f"{totals['Accounts Payable']:.2f}",
                    'accounts_receivable': f"{totals['Accounts Receivable']:.2f}",
                    'revenue': f"{totals['Revenue']:.2f}",
                    'expenses': f"{totals['Expense']:.2f}",
                    'net_income': f"{net_income:.2f}"
                })
