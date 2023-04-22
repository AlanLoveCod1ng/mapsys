from datetime import datetime
class Cafeteria:
    def __init__(self, info:dict) -> None:
        curr = datetime.now()
        self.id = info.get("id", -1)
        self.name = info.get("name", "Unknown")
        self.address = info.get("address", "No available address.")
        open = info.get("hours_open", "09:00:00").split(":")
        close = info.get("hours_closed", "18:00:00").split(":")

        open_time = curr.replace(hour=int(open[0]), minute=int(open[1]), second=int(open[2]))
        close_time = curr.replace(hour=int(close[0]), minute=int(close[1]), second=int(close[2]))
        self.hours_open = open_time.strftime("%H:%M:%S")
        self.hours_closed = close_time.strftime("%H:%M:%S")
        self.status = "Open" if curr > open_time and curr < close_time else "Closed"
        if(info.get("status")=='Open' or info.get("status") == "Closed"):
            self.status = info.get("status")
        self.wait_times = info.get("wait_times","< 5 min")
        self.coords_lat = info.get("coords_lat","0")
        self.coords_lon = info.get("coords_lon","0")
        self.type =  info.get("type", "Fast Food")
        self.tele =  info.get("tele", "88888888")
    def getAttr(self):
        return self.__dict__