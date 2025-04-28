from .base_agent import BaseAgent
from tasks.add_transaction_task import AddTransactionTask
from tasks.process_transactions_task import ProcessTransactionsTask

class BookkeeperAgent(BaseAgent):
    def __init__(self, model):
        self.model = model
        self.tasks = {
            "add_transaction": AddTransactionTask(model),
            "process_transactions": ProcessTransactionsTask(model),
        }

    def run(self, task_name, *args, **kwargs):
        task = self.tasks.get(task_name)
        if not task:
            raise ValueError(f"Unknown task: {task_name}")
        return task.execute(*args, **kwargs)
