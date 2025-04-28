from utils.env_loader import load_env
from utils.model_loader import load_model
from agents.bookkeeper_agent import BookkeeperAgent

def main():
    config = load_env()
    model = load_model(config)
    agent = BookkeeperAgent(model)

    # 1. Add a transaction
    print(agent.run(
        "add_transaction", 
        description="Payment to AWS for cloud hosting", 
        amount=-50.00
    ))

    # 2. Add another
    print(agent.run(
        "add_transaction", 
        description="Customer payment via Stripe", 
        amount=200.00
    ))

    # 3. Categorize all Uncategorized transactions
    print(agent.run(
        "categorize_transactions"
    ))

if __name__ == "__main__":
    main()
