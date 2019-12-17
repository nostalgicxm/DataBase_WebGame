import random

from flask import Flask, Blueprint, jsonify
from flask import render_template
from flask_bootstrap import Bootstrap


from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, create_engine, MetaData, Table, func, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from action.init_db import Base

engine = create_engine("postgresql://postgres:123456@localhost:5432/orm_work")
conn = engine.connect()
meta = MetaData(engine)

players = Table("players", meta, autoload=True)
treasures = Table("treasures", meta, autoload=True)
markets = Table("markets", meta, autoload=True)
box = Table("box", meta, autoload=True)

# flask -alchemy
# Base = automap_base()
# Base.prepare(engine, reflect=True)
# Base.classes.keys()  # 获取所有的对象名
# # 获取表对象
# players = Base.classes.players
# treasures = Base.classes.treasures
# markets = Base.classes.markets
# box = Base.classes.box


bp = Blueprint("action", __name__)


# welcome 界面有各个操作的链接,设想所有动作都完成后在welcome里设置超链接直接进行操作
# 最后有空把界面整好看点
@bp.route('/')
def show_all():
    user = {'user': '我的用户，欢迎来到小游戏'}
    posts = [
        {
            'author': {'user': 'Dear Sir/Madam'},
            'body': ' It\'s Cool! Let\'s start to play! '
        }
    ]
    return render_template('show_all.html', title='Home', user=user, posts=posts)


@bp.route("/<string:user>/login", methods=['GET'])
def login(user):

    try:  # 插入新用户
        conn.execute(
            players.insert().values(pname=user, money=100, lucky=0, workability=0, at1="红玛瑙", at2="布甲", tt1="铁剑"))
    # except Exception as e:  # 用户名被占用,插入失败
        # raise e
    except Exception:
        pass
    return jsonify({"state": "Success", "name": user, "money": 100, "lucky": 0, "workability": 0, "at1": "红玛瑙 ", " at2 ": "布甲", "tt1": "铁剑"})


# 穿戴宝物
@bp.route("/<string:user>/wear_treasure/<string:treasure>", methods=['GET'])
def wear(user, treasure):
    # 找到用户
    wear_id = conn.execute(select([players]).where(players.c.pname == user)).fetchone()[0]
    # print(wear_id)
    # print(type(wear_id))
    his_box = conn.execute(select([box]).where(box.c.pid == wear_id)).fetchall()  # fetchall() 对象迭代后得到元组
    # 找到要穿的宝物的对应id
    treasure_id = conn.execute(select([treasures]).where(treasures.c.tname == treasure)).fetchone()[0]
    # print(treasure_id)
    flag = False
    for trea in his_box:
        if trea[2] == treasure_id:
            flag = True
            break
    if flag:
        # 将原宝物脱下一件
        # 先判断该宝物类别
        type_ = conn.execute(select([treasures]).where(treasures.c.tname == treasure)).fetchone()[2]
        # print(type_)
        if type_ == 'L':  # 穿的是配饰类，把原来的那件脱掉，配饰有两件
            x = random.randint(1, 2) + 4
            print(x)
            old_trea = conn.execute(select([players]).where(players.c.pname == user)).fetchone()[x]  # 宝物名最后放进box
            if x == 5:
                conn.execute(players.update().where(players.c.pid == wear_id).values(at1=treasure))
            else:
                conn.execute(players.update().where(players.c.pid == wear_id).values(at2=treasure))
        old_trea_id = conn.execute(select([treasures]).where(treasures.c.tname == old_trea)).fetchone()[0]
        # 原宝物加入box
        conn.execute(box.insert().values(pid=wear_id, tid=old_trea_id))
        return jsonify({"state": "success", "result": "Already wear treasure wanted"})
    else:
        return jsonify({"state": "failure", "result": "You don't have such treasures to wear"})


# 挂牌宝物
@bp.route("/<string:user>/sell/<string:treasure>/<int:price>", methods=['GET'])
def hang(user, treasure, price):
    # 找到卖家
    hanger_id = conn.execute(select([players]).where(players.c.pname == user)).fetchone()[0]
    treasure_id = conn.execute(select([treasures]).where(treasures.c.tname == treasure)).fetchone()[0]
    # 先确定自己确实有该宝物可以挂牌,默认只挂牌box里的，因为戴的都是自己喜欢的
    his_treasures = conn.execute(select([box]).where(box.c.pid == hanger_id)).fetchall()  # fetchall() 对象迭代后得到元组
    flag = False
    for trea in his_treasures:
        if trea[2] == treasure_id:
            flag = True
            break
    if flag:
        conn.execute(markets.insert().values(pid=hanger_id, tid=treasure_id, price=price))
        return jsonify({"state": "hang_out treasures success", "user": user, "treasure": treasure, "price": price})
    else:
        return jsonify({"state": "hang_out treasures failure", "result": "No such treasures to hang out"})


# 浏览市场
@bp.route("/<string:user>/market", methods=['GET'])
def browse(user):
    # 先检查用户权限
    find_one = conn.execute(select([players]).where(players.c.pname == user)).fetchall()
    if len(find_one) == 0:
        return jsonify({"State": "failure", "result": "You don't have authority, please register first"})
    # 遍历浏览市场所有记录
    # watcher_id = conn.execute(select([players]).where(players.c.pname == user)).fetchone()[0]
    his_market = conn.execute(select([markets])).fetchall()
    result = []
    i = 0
    for record in his_market:
        # print(record)
        dict = {"sid ": record[0], "pid": record[1], " tid": record[2], "price": record[3]}
        result.append(dict)
    # print(result)
    return jsonify({"State": "success", "result": result})


# 在市场上买宝物
@bp.route("/<string:user>/buy/<string:treasure>", methods=['GET'])
def buy(user, treasure):
    # 先检查用户权限
    buyer_id = conn.execute(select([players]).where(players.c.pname == user)).fetchone()[0]
    find_one = conn.execute(select([players]).where(players.c.pname == user)).fetchall()
    if len(find_one) == 0:
        return jsonify({"State": "failure", "result": "You don't have authority, please register first"})
    # 检查市场中是否有该宝物存在
    treasure_record = conn.execute(select([treasures]).where(treasures.c.tname == treasure)).fetchone()
    treasure_id_ = treasure_record[0]
    his_market = conn.execute(select([markets])).fetchall()
    flag = False
    for record in his_market:
        if record[2] == treasure_id_:
            flag = True
            break
    if flag:
        price = conn.execute(select([markets]).where(treasure_id_ == markets.c.tid)).fetchone()[3]
        money_old = conn.execute(select([players]).where(players.c.pname == user)).fetchone()[2]
        if money_old < price:
            return jsonify({"State": "failure", "result": "You don't have enough money to buy"})
        # 更新金额
        conn.execute(players.update().where(players.c.pid == buyer_id).values(money=money_old - price))
        # 市场删除该宝物
        conn.execute(markets.delete().where(markets.c.tid == treasure_id_))
        # 挂牌宝物要从卖家宝盒那里删除，卖家进账
        seller_id = conn.execute(select([markets]).where(markets.c.tid == treasure_id_)).fetchone()[1]
        conn.execute(box.delete().where(box.c.pid == seller_id and box.c.tid == treasure_id_))
        # 更新宝盒
        conn.execute(box.insert().values(pid=buyer_id, tid=treasure_id_))
        result = {"user": user, "treasure": treasure, "trade_money": price}
        # 检查宝盒是否已满
        his_box = conn.execute(select([box]).where(box.c.pid == buyer_id)).fetchall()
        if len(his_box) >= 10:
            system_reclaim(user)
        return jsonify({"State": "success", "result": result})
    else:
        return jsonify({"State": "failure", "result": "We don't have such treasures for you to buy"})

# 收回挂牌宝物,挂牌宝物始终在盒子内
@bp.route("/<string:user>/reclaim/<string:treasure>", methods=['GET'])
def reclaim(user, treasure):
    user_id = conn.execute(select([players]).where(players.c.pname == user)).fetchone()[0]
    # 检查是否有宝物挂牌在市场上
    his_treasures = conn.execute(select([markets]).where(markets.c.pid == user_id)).fetchall()
    if len(his_treasures) == 0:
        return jsonify({"State": "failure", "result": "There is no treasure belonging to you in the market"})
    # 有宝物，收回
    conn.execute(markets.delete().where(markets.c.pid == user_id))
    result = {"user": user, "treasure": treasure}
    return jsonify({"State": "success", "result": result})


# 注册用户后最先进行寻宝和赚钱
# 自动寻宝,每个人都有,后台运行
def look_for_treasure():
    # 遍历每个玩家
    session = sessionmaker(engine)()
    for user in conn.execute(select([players])):
        pid = user['pid']
        # 若宝箱已满,根据id来count
        find_box = conn.execute(select([box]).where(box.c.pid == pid))
        # size = box.count()
        size = 0
        for i in find_box:
            size = size + 1
        if size >= 10:
            system_reclaim(user['pid'])
        # 随机选取配饰类或工具类再根据运气或工作能力选取宝物等级
        player_level = user['workability'] + user['lucky']

        if player_level > 5:
            player_level = 5

        trea = session.query(treasures.c.tid).filter(treasures.c.level >= player_level - 1,
                                                     treasures.c.level <= player_level + 2).all()
        # print(trea)
        x = random.randint(0, len(trea) - 1)
        # print(trea[x][0])
        # 宝物级别
        trea_level = session.query(treasures.c.level).filter(treasures.c.tid == trea[x][0]).all()[0]
        # print(type(trea_level))
        # print(trea_level[0])
        # print(user['workability'])
        # 更新工作能力和运气值
        workability_new = user['workability'] + trea_level[0]
        lucky_new = user['lucky'] + trea_level[0] * 2
        conn.execute(players.update().where(players.c.pid == pid).values(workability=workability_new, lucky=lucky_new))

        conn.execute(box.insert().values(pid=pid, tid=trea[x][0]))
        print("玩家 %s 寻宝成功" % user['pname'])
    return 0


# 自动赚钱和运气值
def bonus_for_work():
    # 遍历每个玩家
    for user in conn.execute(select([players])):
        # print(user)
        print("玩家 %s 正在劳动，一份耕耘，一份收获！" % user['pname'])
        # 假定赚取奖金与工作能力线性相关
        workability_ = user['workability']
        money_new = user['money'] + 10 * workability_
        conn.execute(players.update().values(money=money_new))
        print("玩家 %s 赚钱成功" % user['pname'])
    return 0


def system_reclaim(user):
    # 盒子已满，不然不会到这里
    user_id_ = conn.execute(select([players]).where(players.c.pname == user)).fetchone()[0]
    # 随机回收盒子中等级最低的宝物
    his_box = conn.execute(select([box]).where(box.c.pid == user_id_)).fetchall()
    print(len(his_box))
    print(his_box)
    # 对盒子里的宝物按level排序，删除第一个宝物
    min_trea_level = 10
    for trea1 in his_box:
        trea_level = conn.execute(select([treasures]).where(treasures.c.tid == trea1[2])).fetchone()[3]
        if trea_level < min_trea_level:
            min_trea_level = trea_level
            to_delete_id = trea1[2]
    # 删除该宝物
    # 用bid来删除，因为符合条件的不止一个，但bid是唯一的
    to_delete_bid = conn.execute(select([box]).where(box.c.tid == to_delete_id and box.c.pid == user_id_)).fetchone()[0]
    conn.execute(box.delete().where(box.c.bid == to_delete_bid))
    his_box2 = conn.execute(select([box]).where(box.c.pid == user_id_)).fetchall()
    # print(len(his_box2))
    print("系统回收成功")
    return 0


if __name__ == '__main__':
    print("yes")
