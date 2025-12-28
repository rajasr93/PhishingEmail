from abc import ABC, abstractmethod
import logging

class BaseAgent(ABC):
    def __init__(self, name, logger=None):
        self.name = name
        self.logger = logger or logging.getLogger(name)

    @abstractmethod
    def analyze(self, email_data):
        """
        Analyzes the email_data and returns a result dict.
        Must raise NotImplementedError if not overridden.
        """
        raise NotImplementedError
