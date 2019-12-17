# 配置
import os


# 设置
class Config(object):
    # 设置密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # 密钥的值为 you-will-never-guess
    # 设置定时任务
    JOBS = [
        {
            'id': 'job1',
            'func': '__main__:look_for_treasure',
            'trigger': 'cron',
            'second': 5,
        },
        {
            'id': 'job2',
            'func': '__main__:bonus_for_work',
            'trigger': 'cron',
            'second': 5,
        },
        {
            'id': 'job3',
            'func': '__main__:wear',
            'trigger': 'cron',
            'second': 5,
        },
        {
            'id': 'job4',
            'func': '__main__:hang',
            'trigger': 'cron',
            'second': 5,
        }
    ]
