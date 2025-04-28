import csv
from .base_task import BaseTask
from datetime import datetime

class AddTransactionTask(BaseTask):
    def __init__(self, model, csv_file_path="example/transactions.csv"):
        super().__init__(model)
        self.csv_file_path = csv_file_path

    def execute(self, description, amount, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        with open(self.csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, description, amount])

        return f"Transaction added: {description} | {amount} | {date}"
