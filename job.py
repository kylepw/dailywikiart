from apscheduler.schedulers.blocking import BlockingScheduler
import bot


sched = BlockingScheduler()

sched.add_job(bot.run, 'cron', hour=20, timezone='Japan')

sched.start()
