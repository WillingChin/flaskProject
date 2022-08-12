import logging
from sqlalchemy import MetaData, create_engine, Table, Column, select, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref

metadata = MetaData()
# ToDo: do not use check_same_thread
engine = create_engine('sqlite:///user_database', connect_args={'check_same_thread': False}, echo=False)  # echo=False
Base = declarative_base()
db_session = sessionmaker(bind=engine)()


'''
@Title dao
@Project ：Crime data analysis
@File    ：user_database.py
@Author  ：XChen202
@Date    ：7/15/2022 9:59M
@evn python3.7
'''


# Table sys_dict
class SysDict(Base):
    __tablename__ = "sys_dict"
    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    is_del = Column(Integer)
    #sys_dict_item_data = relationship("SysDictItem", backref="sys_dict")
    sys_dict_item_data = relationship('SysDictItem', backref='sys_dict_item')
# end SysDict


# Table sys_dict_item
class SysDictItem(Base):
    __tablename__ = 'sys_dict_item'
    id = Column(Integer, primary_key=True)
    dict_id = Column(Integer, ForeignKey("sys_dict.id"))
    item_text = Column(String)
    item_value = Column(String)
    item_sort = Column(String)
    selected = Column(Integer)
    is_del = Column(Integer)
# end SysDictItem


# Retrieving data from the database
# get list by code (return sys_dict_item)
def get_chart_type_data(code):
    logging.info("get_chart_type_data() code: " + code)
    sys_dict = db_session.query(SysDictItem) \
        .order_by(SysDictItem.item_sort) \
        .join(SysDictItem, SysDict.sys_dict_item_data) \
        .filter(SysDict.code == code) \
        .all()
    return sys_dict;
# end get_chart_type_data

# get list by code (return sys_dict_item)
def get_chart_type_selected_data(code, selected):
    logging.info("get_chart_type_data() code: " + code +" selected: "+ selected)
    sys_dict = db_session.query(SysDictItem) \
        .order_by(SysDictItem.item_sort) \
        .join(SysDictItem, SysDict.sys_dict_item_data) \
        .filter(SysDict.code == code, SysDictItem.selected == selected) \
        .all()
    return sys_dict;
# end get_chart_type_data
