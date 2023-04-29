from datetime import datetime
from application import cur, con
class Cafeteria:
    def __init__(self, info:tuple) -> None:
        self.id = info[0]
        self.name = info[1]
        self.address = info[2]
        self.hours_open = info[3]
        self.hours_closed = info[4]
        self.status = info[5]
        self.wait_times = info[6]
        self.coords_lat = info[7]
        self.coords_lon = info[8]
        self.type = info[9]
        self.password = info[10]
        self.tele = info[11]
        self.salt = info[12]
    def getAttr(self):
        return self.__dict__


def fetch_cafeteria(filter:dict = {}) -> list[Cafeteria]:
    filter_cond = []
    for entry in filter:
        filter_cond.append(f"{entry} = {filter[entry]}")
    # get sql filter statement
    filter_stmt = " WHERE " + " AND ".join(filter_cond) if filter_cond else ""
    print(f"SELECT * FROM Cafeteria" + filter_stmt)
    res = cur.execute(f"SELECT * FROM Cafeteria" + filter_stmt)
    result_list = [Cafeteria(i) for i in res.fetchall()]
    return result_list
def update_cafeteria(info:dict, filter:dict):
    filter_cond = []
    for entry in filter:
        filter_cond.append(f"{entry} = {filter[entry]}")
    # get sql filter statement
    filter_stmt = " WHERE " + " AND ".join(filter_cond) if filter_cond else ""
    update_info = []
    for entry in info:
        update_info.append(f"{entry} = '{info[entry]}'")
    # get sql filter statement
    set_stmt = " SET " + ", ".join(update_info) if update_info else ""
    sql_stmt = f"UPDATE Cafeteria" + set_stmt + filter_stmt
    cur.execute(sql_stmt)
    con.commit()