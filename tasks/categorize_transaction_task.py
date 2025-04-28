import csv
import tempfile
import shutil
from .base_task import BaseTask

class CategorizeTransactionTask(BaseTask):
    def __init__(self, model, csv_file_path="example/real_transactions.csv"):
        super().__init__(model)
        self.csv_file_path = csv_file_path

    def execute(self):
        updated_rows = []
        with open(self.csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['category'] == "Uncategorized":
                    prompt = (
                        f"Categorize this transaction for a SaaS company:\n"
                        f"Transaction description: '{row['description']}'\n"
                        f"Transaction amount: {row['amount']}\n"
                        f"\n"
                        f"Instructions:\n"
                        f"- Only respond with a short category label like 'Hosting Expenses', 'Subscription Revenue', 'Software Subscriptions', etc.\n"
                        f"- Do not explain, do not use markdown, do not add extra text.\n"
                        f"- Respond with JUST the category."
                    )
                    category = self.model.invoke(prompt)
                    cleaned_category = category.strip().split("\n")[0]  # Take only first line
                    row['category'] = cleaned_category
                updated_rows.append(row)

        with tempfile.NamedTemporaryFile('w', delete=False, newline='') as tmpfile:
            fieldnames = ['date', 'description', 'amount', 'category']
            writer = csv.DictWriter(tmpfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

        shutil.move(tmpfile.name, self.csv_file_path)
        return "Categorization complete!"
