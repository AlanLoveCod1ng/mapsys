from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import Table

db_engine = create_engine('sqlite:///db.sqlite?check_same_thread=False')
Base = declarative_base()
session = Session(db_engine)

class Cafeteria(Base):
    __table__ = Table('Cafeteria', Base.metadata,
                    autoload=True, autoload_with=db_engine)
    def getAttr(self):
        temp = dict(self.__dict__)
        temp.pop('_sa_instance_state')
        return temp

def update_check(info):
    allowed_changed_attr = {
        'status': set(['Open','Closed']),
        'wait_times': set(['< 5 min', '5 - 15 min', '> 20 min'])
    }
    for attr,value in info.items():
        if attr not in allowed_changed_attr:
            raise Exception('Attempting to change non-allowed attr')
        if value not in allowed_changed_attr[attr]:
            raise Exception('Attempting to change with unexpected value')

    
def fetch_cafeteria(filter:dict = {}) -> list[Cafeteria]:
    query = session.query(Cafeteria)
    for attr,value in filter.items():
        query = query.filter( getattr(Cafeteria,attr)==value )
    res = query.all()
    return res
def update_cafeteria(info:dict, filter:dict):
    tobe_updated = fetch_cafeteria(filter)
    update_check(info)
    for cafeteria in tobe_updated:
        for attr,value in info.items():
            setattr(cafeteria,attr,value)
    session.commit()