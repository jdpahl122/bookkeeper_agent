import csv
from .base_task import BaseTask
from datetime import datetime
import os

class AddTransactionTask(BaseTask):
    def __init__(self, model, csv_file_path="example/transactions.csv"):
        super().__init__(model)
        self.csv_file_path = csv_file_path

    def execute(self, description, amount, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        next_transaction_id = self._find_next_transaction_id()

        file_exists = os.path.isfile(self.csv_file_path)

        with open(self.csv_file_path, mode='a', newline='') as file:
            fieldnames = ['transaction_id', 'date', 'description', 'amount']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({
                'transaction_id': next_transaction_id,
                'date': date,
                'description': description,
                'amount': amount
            })

        return f"Transaction added: ID {next_transaction_id} | {description} | {amount} | {date}"

    def _find_next_transaction_id(self):
        if not os.path.isfile(self.csv_file_path):
            return 1
        with open(self.csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            ids = [int(row['transaction_id']) for row in reader if 'transaction_id' in row and row['transaction_id'].isdigit()]
            if ids:
                return max(ids) + 1
            return 1
