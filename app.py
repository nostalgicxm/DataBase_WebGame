from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from sqlalchemy import create_engine

from action.act import bp, bonus_for_work, look_for_treasure, wear, hang, browse, system_reclaim
from action.config import Config
from action.init_db import drop_db, init_db


if __name__ == "__main__":
    # 初始化数据库
    engine = create_engine("postgresql://postgres:123456@localhost:5432/orm_work")
    # drop_db()  # 先清除原先的不然初始化有问题
    # init_db()

    # 启动flask
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.config.from_object(Config())    # 配置自动执行任务

    # 自动寻宝和赚钱,每天早上七点准时赚钱,晚上七点准时寻宝
    # 实例化一个调度器
    scheduler = BlockingScheduler()
    scheduler.add_job(look_for_treasure, 'interval', seconds=5)
    scheduler.add_job(bonus_for_work, 'interval', seconds=5)
    # scheduler.add_job(wear('xm', '布甲'), 'interval', seconds=1)
    # scheduler.add_job(hang('xm', '布甲', 50), 'interval', seconds=1)
    # scheduler.add_job(browse('xm'), 'interval', seconds=1)
    # scheduler.add_job(system_reclaim('xm'), 'interval', seconds=1)
    scheduler.start()
    app.register_blueprint(bp)
    # app.run()
    app.run(debug=True)