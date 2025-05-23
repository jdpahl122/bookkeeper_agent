from utils.env_loader import load_env
from utils.model_loader import load_model
from agents.bookkeeper_agent import BookkeeperAgent
import csv
import os

def view_status(summary_csv="example/monthly_summary.csv"):
    if not os.path.isfile(summary_csv):
        print("No summary available yet.")
        return

    print("\n====== Current Financial Status ======")
    with open(summary_csv, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(f"\nMonth: {row['month']}")
            print(f"  Accounts Payable: {row['accounts_payable']}")
            print(f"  Accounts Receivable: {row['accounts_receivable']}")
            print(f"  Revenue: {row['revenue']}")
            print(f"  Expenses: {row['expenses']}")
            print(f"  Net Income: {row['net_income']}")

def main():
    config = load_env()
    model = load_model(config)
    agent = BookkeeperAgent(model)

    while True:
        print("\n===== Bookkeeper CLI =====")
        print("[1] Add a new transaction manually")
        print("[2] Process transactions (skip already processed)")
        print("[3] View current status")
        print("[4] Generate AR Aging Report")
        print("[5] Generate AP Aging Report")
        print("[6] Mark a Transaction as Paid")
        print("[7] Exit")

        choice = input("\nEnter your choice (1-7): ")

        if choice == '1':
            description = input("Enter transaction description: ")
            amount = float(input("Enter transaction amount: "))
            print(agent.run("add_transaction", description=description, amount=amount))

        elif choice == '2':
            print(agent.run("process_transactions"))

        elif choice == '3':
            view_status()

        elif choice == '4':
            from tasks.generate_ar_aging_report import GenerateARAgingReportTask
            report_task = GenerateARAgingReportTask()
            print(report_task.execute())

        elif choice == '5':
            from tasks.generate_ap_aging_report import GenerateAPAgingReportTask
            report_task = GenerateAPAgingReportTask()
            print(report_task.execute())

        elif choice == '6':
            from tasks.mark_transaction_paid_task import MarkTransactionPaidTask
            task = MarkTransactionPaidTask()
            print(task.execute())

        elif choice == '7':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
