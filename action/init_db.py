# 创建连接相关
from sqlalchemy import create_engine, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
# 创建表中的字段(列)
from sqlalchemy import Column
# 表中字段的属性
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.orm import sessionmaker, relationship

# 创建基类
Base = declarative_base()


# 如果不声明外键关联那么表与表之间就是独立的，与数据库的逻辑设计相悖。
# ForeignKeyConstraint是定义组合外键的唯一方法
# MySQL 使用 AUTO_INCREMENT 关键字来执行 auto-increment 任务。
# 默认地，AUTO_INCREMENT 的开始值是 1，每条新记录递增 1。
# 要让 AUTO_INCREMENT 序列以其他的值起始，请使用下面的 SQL 语法：
# ALTER TABLE Persons AUTO_INCREMENT=100

# 创建表
class Treasures(Base):
    __tablename__ = 'treasures'
    tid = Column(Integer, primary_key=True, autoincrement=True)
    tname = Column(String(10), unique=True)
    type = Column(String(1))
    level = Column(Integer)


class Players(Base):
    __tablename__ = 'players'
    pid = Column(Integer, primary_key=True, autoincrement=True)
    pname = Column(String(10), nullable=False, unique=True)
    money = Column(Integer, CheckConstraint("money > 0"))
    lucky = Column(Integer)
    workability = Column(Integer)
    at1 = Column(String(10), ForeignKey('treasures.tname'))  # 有重复值的不能设置为唯一约束
    at2 = Column(String(10), ForeignKey('treasures.tname'))
    tt1 = Column(String(10), ForeignKey('treasures.tname'))


class Markets(Base):
    __tablename__ = 'markets'
    sid = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    pid = Column(Integer, ForeignKey('players.pid'))
    tid = Column(Integer, ForeignKey('treasures.tid'))
    price = Column(Integer)


# Box 初始化里面没有宝物,宝物得靠玩家去赚
class Box(Base):
    __tablename__ = 'box'
    bid = Column(Integer, primary_key=True)
    pid = Column(Integer, ForeignKey('players.pid'))
    tid = Column(Integer, ForeignKey('treasures.tid'))


def init_db():
    """创建所有定义的表到数据库中"""
    Base.metadata.create_all(engine)  # 创建所有的表结构
    init_treasures(engine)


def drop_db():
    """从数据库中删除所有定义的表"""
    Base.metadata.drop_all(engine)


# 初始化宝物库，初始化只能进行一次
def init_treasures(engine):
    DBSession = sessionmaker(bind=engine)
    # 创建session 对象
    session = DBSession()
    # 初始化玩家
    # session.add_all([
    #     Players(pid=1, pname="花木兰", money=100, lucky=0, workability=0, at1="红玛瑙", at2="布甲", tt1="铁剑"),
    #     Players(pid=2, pname="猪八戒", money=100, lucky=0, workability=0, at1="红玛瑙", at2="布甲", tt1="铁剑"),
    #     Players(pid=3, pname="安琪拉", money=100, lucky=0, workability=0, at1="红玛瑙", at2="布甲", tt1="铁剑"),
    #     Players(pid=4, pname="蔡文姬", money=100, lucky=0, workability=0, at1="红玛瑙", at2="布甲", tt1="铁剑"),
    #     Players(pid=5, pname="庄周", money=100, lucky=0, workability=0, at1="红玛瑙", at2="布甲", tt1="铁剑"),
    #     Players(pid=6, pname="亚瑟", money=100, lucky=0, workability=0, at1="红玛瑙", at2="布甲", tt1="铁剑"),
    #     Players(pid=7, pname="兰陵王", money=100, lucky=0, workability=0, at1="红玛瑙", at2="布甲", tt1="铁剑"),
    #     Players(pid=8, pname="倩女", money=100, lucky=0, workability=0, at1="红玛瑙", at2="布甲", tt1="铁剑"),
    #     Players(pid=9, pname="姜太公", money=100, lucky=0, workability=0, at1="红玛瑙", at2="布甲", tt1="铁剑"),
    #     Players(pid=10, pname="秦始皇", money=100, lucky=0, workability=0, at1="红玛瑙", at2="布甲", tt1="铁剑"),
    # ])
    # 注意add 只能进行一遍，多来几遍就会报错了
    session.add_all([
        Treasures(tid=1, tname="铁剑", type='W', level=1),
        Treasures(tid=2, tname="雷鸣刀", type='W', level=2),
        Treasures(tid=3, tname="元素杖", type='W', level=3),
        Treasures(tid=4, tname="匕首", type='W', level=4),
        Treasures(tid=5, tname="疾步之靴", type='W', level=5),
        Treasures(tid=6, tname="红玛瑙", type='L', level=1),
        Treasures(tid=7, tname="搏击拳套", type='L', level=2),
        Treasures(tid=8, tname="圣杯", type='L', level=3),
        Treasures(tid=9, tname="魅影面罩", type='L', level=4),
        Treasures(tid=10, tname="布甲", type='L', level=5)])
    session.commit()

if __name__ == '__main__':
    # 初始化数据库连接
    engine = create_engine('postgresql://postgres:123456@localhost:5432/orm_work')
    drop_db()  # 先清除原先的不然初始化有问题
    init_db()
