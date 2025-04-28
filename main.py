from utils.env_loader import load_env
from utils.model_loader import load_model
from agents.bookkeeper_agent import BookkeeperAgent

def main():
    config = load_env()
    model = load_model(config)
    agent = BookkeeperAgent(model)

    # Example: Add a transaction
    print(agent.run(
        "add_transaction", 
        description="Payment to AWS for cloud hosting", 
        amount=-50.00
    ))

    # Example: Process and output categorized ledger
    print(agent.run(
        "process_transactions"
    ))

if __name__ == "__main__":
    main()
