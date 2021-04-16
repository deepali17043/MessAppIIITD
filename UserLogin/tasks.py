import redis
from celery import shared_task
from .models import *
from .views import IST
import logging
from random import randint

@shared_task
def update_number():
    r = redis.StrictRedis()
    v = randint(0, 9)
    print(v)
    r.set('my_number', v)
    print("something")

@shared_task
def daily_create_mess_objects():
    # r = redis.StrictRedis()
    # numdays = 22
    # today = datetime.datetime.now(IST).date()
    print("hi")
    logging.display("somethinggggggg")
    date_create = datetime.datetime(year=2021, month=5, day=1)
    logging.info('date_created')
    attendance_qset = MessAttendance.objects.filter(date=date_create)

    users = User.objects.filter(username='2017043')
    for user in users:
        try:
            mess_user = MessUser.objects.get(user=user)
        except:
            MessUser.objects.update_or_create(user=user)
            mess_user = MessUser.objects.get(user=user)
        tmpattendance = attendance_qset.filter(user=mess_user).count()
        if tmpattendance < 4:
            for meal in meal_choices:
                MessAttendance.objects.update_or_create(
                    user=mess_user,
                    date=date_create,
                    meal=meal
                )
                print("done", meal)
            print("tmp<4")
        print(user.name)
    print("okay, done")
    return
