# 将数据库清除
# 先连接上数据库
from flask.testing import FlaskClient
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.ext.declarative import declarative_base

from action import act
from action.init_db import init_treasures

Base = declarative_base()


def init_db():
    """创建所有定义的表到数据库中"""
    Base.metadata.create_all(engine)  # 创建所有的表结构
    init_treasures(engine)


def drop_db():
    """从数据库中删除所有定义的表"""
    Base.metadata.drop_all(engine)


# 加载数据库
engine = create_engine("postgresql://postgres:123456@localhost:5432/orm_work")
conn = engine.connect()
meta = MetaData(engine)

players = Table("players", meta, autoload=True)
treasures = Table("treasures", meta, autoload=True)
markets = Table("markets", meta, autoload=True)
box = Table("box", meta, autoload=True)

# 定义一个清空数据库其它内容只有初始化的函数


# drop_db()  # 先清除原先的不然初始化有问题, 删除了表，而不是让表的内容为空
# init_db()
# 使用测试案例的前提是存在宝物库，和正常运行的前提一样，只有宝物库是初始化了的
# 测试案例列表
treasures_ = conn.execute(select([treasures])).fetchall()
treasure_name_demo = []
for trea in treasures_:
    treasure_name_demo.append(trea[1])  # 存放宝物名称
user = ['xm', 'zh', 'ra']
operations = ["login", "wear", "hang", "browse", "buy", "reclaim"]
prices = [30, 60, 90, 120, 150]


# 对得到的json进行解析，看由pytest生成的是否和json自己生成的一样
def verify_json(json, username: str, operation: str, treasure: 'str' = 'test', price: 'int' = 0):
    if operation == "login":
        result = act.login(username).get_json(force=True)
    elif operation == "browse":
        result = act.browse(username).get_json(force=True)
    elif operation == "wear":
        result = act.wear(username, treasure).get_json(force=True)
    elif operation == "buy":
        result = act.buy(username, treasure).get_json(force=True)
    elif operation == "reclaim":
        result = act.reclaim(username, treasure).get_json(force=True)
    elif operation == "hang":
        result = act.hang(username, treasure, price).get_json(force=True)
    else:
        result = None
    assert json == result


# 生成测试案例
def test_act_get(client: FlaskClient):
    for username in user:
        for operation in operations:
            if operation in ['wear', 'buy', 'reclaim']:
                for treasure in treasure_name_demo:
                    response = client.get("/%s/%s/%s" % (username, operation, treasure))
                    json = response.get_json()  # 由于响应的内容包含html代码，不是json，改为此形式
                    # drop_db()
                    verify_json(json, username, operation, treasure)
            elif operation in ['login', 'browse']:
                response = client.get("/%s/%s" % (username, operation))
                json = response.get_json()
                # drop_db()
                verify_json(json, username, operation)
            elif operation == "hang":
                for treasure in treasure_name_demo:
                    for price in prices:
                        response = client.get("/%s/%s/%s/%d" % (username, operation, treasure, price))
                        json = response.get_json()
                        # drop_db()
                        verify_json(json, username, operation, treasure, price)
