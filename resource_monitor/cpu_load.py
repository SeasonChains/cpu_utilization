import psutil
import time, logging
from logger import CPULogger
from config import CPU_THRESHOLD, LOG_INTERVAL, LOG_FILE
from abc import ABC, abstractmethod


class AlertObserver(ABC):
    """
    Abstract base class for alert observers.
    """
    @abstractmethod
    def notification(self, message: str):
        pass


class ConsoleAlert(AlertObserver):
    def notification(self, message: str):
        print(f"[ConsoleCPUAlert] {message}")

class CPULoad:
    def __init__(self, threshold=CPU_THRESHOLD, log_interval=LOG_INTERVAL, log_file=LOG_FILE):
        """
        Initialize the CPU Load class.
        :param threshold: CPU usage threshold for warnings.
        :param log_interval: Time interval for monitoring in seconds.
        :param log_file: Log file path.
        """
        self.threshold = threshold
        self.log_interval = log_interval
        self.log_file = log_file
        self.logger = CPULogger(name="CPULoadLogger", log_file=self.log_file, level=logging.INFO).get_logger()
        self.alert_observers = []  # List of alert observers

    def obsrvr_attach(self, observer: AlertObserver):
        """
        Attach an observer for alerts.
        :param observer: An instance of AlertObserver.
        """
        self.alert_observers.append(observer)

    def obsrvr_detach(self, observer: AlertObserver):
        """
        Detach an observer for alerts.
        :param observer: An instance of AlertObserver.
        """
        self.alert_observers.remove(observer)

    def obsrvr_notify(self, message: str):
        """
        Notify all attached observers with an alert message.
        :param message: Alert message to send.
        """
        for observer in self.alert_observers:
            observer.notification(message)

    def collect_cpu_core_usg(self):
        """Collect CPU usage for individual cores and log observation"""
        cpu_count = psutil.cpu_count(logical=True)
        self.logger.info(f"Monitoring {cpu_count} CPU cores.")
        per_core_usage = psutil.cpu_percent(interval=None, percpu=True)

        for core, usage in enumerate(per_core_usage):
            self.logger.info(f"Core {core}: {usage:.2f}% usage.")

        return per_core_usage

    def check_cpu_load_avrg(self):
        """Check and log system-wide load averages."""
        cpu_count = psutil.cpu_count(logical=True)
        load_averages = [x / cpu_count * 100 for x in psutil.getloadavg()]
        self.logger.info(f"System load averages (1m, 5m, 15m): {load_averages}")
        return load_averages

    def check_thresholds(self, per_core_usage, load_averages):
        """Check if usage exceeds thresholds and trigger warnings."""
        # Per-core checks
        for core, usage in enumerate(per_core_usage):
            if usage > self.threshold:
                message = f"ALERT: Core {core} usage exceeded threshold! ({usage:.2f}%)"
                self.logger.warning(message)
                self.obsrvr_notify(message)

        # System-wide checks
        for avg in load_averages:
            if avg > self.threshold:
                message = f"ALERT: System load average exceeded threshold! ({avg:.2f}%)"
                self.logger.warning(message)
                self.obsrvr_notify(message)

    def load_check(self):
        """Perform a single cycle of CPU load checking."""
        try:
            per_core_usage = self.collect_cpu_core_usg()
            load_averages = self.check_cpu_load_avrg()
            self.check_thresholds(per_core_usage, load_averages)
        except Exception as e:
            self.logger.error(f"Error during load check: {e}")

    def monitor(self):
        """Continuous CPU load monitor"""
        self.logger.info("Starting to monitor CPU load")
        try:
            while True:
                self.load_check()
                time.sleep(self.log_interval)
        except KeyboardInterrupt:
            self.logger.info("CPU load monitoring interrupted")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.logger.info("CPU load monitoring ended.")


def main():
    """
    CPU Load Monitoring execution
    """
    cpu_load = CPULoad()
    console_alert = ConsoleAlert()
    cpu_load.obsrvr_attach(console_alert)
    cpu_load.monitor()


if __name__ == "__main__":
    main()
