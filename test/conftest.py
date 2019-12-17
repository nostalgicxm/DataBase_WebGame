import pytest
from flask import Flask, app
from flask.testing import FlaskClient

from action.act import bp


# 对固件进行集中管理
# 利用固件做任何事情，其中最常见的可能就是数据库的初始连接和最后关闭操作
# 在复杂的项目中，可以在不同的目录层级定义 conftest.py，其作用域为其所在的目录和子目录。
# 不要自己显式调用 conftest.py，pytest 会自动调用，可以把 conftest 当做插件来理解。

@pytest.fixture
def client() -> FlaskClient:
    app = Flask(__name__)
    ctx = app.app_context()
    ctx.push()
    app.register_blueprint(bp)
    client = app.test_client()
    return client

