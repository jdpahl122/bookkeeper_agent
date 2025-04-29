import csv
import tempfile
import shutil

class MarkTransactionPaidTask:
    def __init__(self, csv_file="example/processed_transactions.csv"):
        self.csv_file = csv_file

    def execute(self):
        transactions = []

        # Load unpaid transactions safely
        with open(self.csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('payment_status', 'Unpaid') != "Paid":
                    transactions.append(row)

        if not transactions:
            print("No unpaid transactions found.")
            return

        print("\n===== Unpaid Transactions =====")
        for idx, txn in enumerate(transactions, start=1):
            print(f"[{idx}] {txn['date']} | {txn['description']} | {txn['amount']} | Type: {txn['type']} | Due: {txn.get('due_date', txn['date'])}")

        try:
            choice = int(input("\nEnter the number of the transaction to mark as Paid: "))
            if not (1 <= choice <= len(transactions)):
                print("Invalid choice.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        selected_txn = transactions[choice - 1]

        # Rewrite file, updating payment_status
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='')
        with open(self.csv_file, mode='r') as file, temp_file:
            reader = csv.DictReader(file)
            # Dynamically update fieldnames
            fieldnames = reader.fieldnames.copy()
            if 'due_date' not in fieldnames:
                fieldnames.append('due_date')
            if 'payment_status' not in fieldnames:
                fieldnames.append('payment_status')

            writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                # Ensure every row has required fields
                if 'due_date' not in row:
                    row['due_date'] = row.get('date', '')  # fallback
                if 'payment_status' not in row:
                    row['payment_status'] = 'Unpaid'

                if (row['date'] == selected_txn['date'] and
                    row['description'] == selected_txn['description'] and
                    row['amount'] == selected_txn['amount']):
                    row['payment_status'] = "Paid"
                writer.writerow(row)

        shutil.move(temp_file.name, self.csv_file)

        print(f"\nMarked '{selected_txn['description']}' as Paid successfully!")
        return "Transaction update complete."
