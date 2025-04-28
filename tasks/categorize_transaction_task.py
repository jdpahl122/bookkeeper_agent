import csv
import tempfile
import shutil
from .base_task import BaseTask

class CategorizeTransactionTask(BaseTask):
    def __init__(self, model, csv_file_path="example/transactions.csv"):
        super().__init__(model)
        self.csv_file_path = csv_file_path

    def execute(self):
        updated_rows = []
        with open(self.csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['category'] == "Uncategorized":
                    prompt = f"Categorize this transaction for a SaaS company: '{row['description']}' Amount: {row['amount']}"
                    category = self.model.invoke(prompt)
                    row['category'] = category.strip()
                updated_rows.append(row)

        # Save to a temp file and replace original
        with tempfile.NamedTemporaryFile('w', delete=False, newline='') as tmpfile:
            fieldnames = ['date', 'description', 'amount', 'category']
            writer = csv.DictWriter(tmpfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        
        shutil.move(tmpfile.name, self.csv_file_path)
        return "Categorization complete!"
