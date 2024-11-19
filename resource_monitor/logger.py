import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter
import os
from abc import ABC, abstractmethod  # For Observer base class
from config import LOG_FILE, LOG_BACKUP


class LogObserver(ABC):
    """
    Abstract base class for log observers.
    """
    @abstractmethod
    def update(self, log_message):
        pass


class CPULogger:
    _instances = {}

    def __init__(self, name=__name__, log_file=LOG_FILE, level=logging.INFO, backup_count=LOG_BACKUP, formatter=None):
        """
        Initialize Logger instance.

        :param name: Name of the logger.
        :param log_file: Path to the log file.
        :param level: Logging level.
        :param backup_count: Number of backup log files to retain.
        :param formatter: Optional custom formatter for the log messages.
        """
        self.name = name
        self.log_file = log_file
        self.level = level
        self.backup_count = backup_count
        self.formatter = formatter or Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = self._setup_logger()
        self.observers = []  # List of observers

    def _ensure_log_directory(self):
        """
        Create File directory if doesn't exist.
        """
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def _setup_logger(self):
        """
        Set logger instance with TimedRotatingFileHandler.
        """
        # Check for existing singleton instance
        if self.name in CPULogger._instances:
            return CPULogger._instances[self.name]
        self._ensure_log_directory()

        # config logger
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        logger.propagate = False

        if not logger.hasHandlers():
            handler = TimedRotatingFileHandler(
                filename=self.log_file,
                when='D',  # Daily Rotation
                interval=1,
                backupCount=self.backup_count,
                encoding='utf-8'
            )

            # Set formatter
            handler.setFormatter(self.formatter)

            logger.addHandler(handler)

        # Store the instance in the singleton dictionary
        CPULogger._instances[self.name] = logger
        return logger

    def attach(self, observer: LogObserver):
        """
        Attach observer to the logger.
        :param observer: An instance of LogObserver.
        """
        self.observers.append(observer)

    def detach(self, observer: LogObserver):
        """
        Detach observer from the logger.
        :param observer: An instance of LogObserver.
        """
        self.observers.remove(observer)

    def notify(self, log_message):
        """
        Notify all attached observers with a log message.
        :param log_message: The message send to observers.
        """
        for observer in self.observers:
            observer.update(log_message)

    def log(self, level, message):
        """
        Log a message and notify observers.
        :param level: Log level.
        :param message: Log message.
        """
        self.logger.log(level, message)
        self.notify(message)

    def get_logger(self):
        """
        Return the configured logger instance.
        """
        return self.logger
