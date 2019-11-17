from apscheduler.schedulers.blocking import BlockingScheduler
import bot


sched = BlockingScheduler()

"""
@sched.scheduled_job('cron', hour='20', timezone='Japan')
def tweet_img():
    bot.run()"""
sched.add_job(bot.run, 'interval', minutes=1)

sched.start()
