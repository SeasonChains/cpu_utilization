import psutil
import time
from logger import logger
from config import CPU_THRESHOLD, LOG_INTERVAL

class CPULoad:
    def __init__(self, threshold=CPU_THRESHOLD, log_interval=LOG_INTERVAL):
        """
        Initialize the CPU Load class.
        :param threshold: CPU usage threshold for warnings.
        :param update_interval: Time interval for monitoring in seconds.
        """
        self.threshold = threshold
        self.log_interval = log_interval

    def load_check(self):
        """Collect CPU load and log alerts."""
        cpu_count = psutil.cpu_count(logical=True)
        logger.info(f"Initialized metrics for {cpu_count} CPU cores.")
        load_avg_per = [x / cpu_count * 100 for x in psutil.getloadavg()]
        # Collect CPU times
        for cpu_core in range(cpu_count):
            cpu_usage = psutil.cpu_times_percent(interval=self.log_interval,percpu=True)
            logger.info(f"CPU Usage: {cpu_usage} for the core : {cpu_core}")
        
        for load in load_avg_per:
            if  load > self.threshold:
                logger.warning(f"ALERT: CPU usage exceeded threshold! ({cpu_usage})")
    
    def monitor(self):
        self.load_check()

if __name__ == "__main__":
    cpu_load = CPULoad()
    cpu_load.monitor()

