from abc import ABC, abstractmethod

class BaseTask(ABC):
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
