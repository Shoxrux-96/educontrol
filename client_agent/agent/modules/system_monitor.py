import psutil


class SystemMonitor:
    def get_stats(self) -> dict:
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
            return {
                "cpu": int(cpu),
                "ram": int(ram),
                "disk": int(disk),
                "status": "online",
            }
        except Exception:
            return {"cpu": 0, "ram": 0, "disk": 0, "status": "online"}
