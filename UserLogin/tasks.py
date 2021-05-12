"""
File for scheduling parallel tasks.
"""

import datetime
import pytz

from background_task import background

from .models import *


@background(queue='my-queue')
def daily_create_mess_objects():
    """
    Create MessAttendance Objects for all customer type users, for the coming 31 days.
    Deletes the MessAttendance objects from 31 days ago so as to not over populate the database
    :return: None
    """
    print("start")  # To note that the function is running

    # Calculation of all required dates for querying the database
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    date_start = datetime.datetime(year=now.year, month=now.month, day=now.day)
    date_end = date_start + datetime.timedelta(days=31)
    date_to_del = date_start - datetime.timedelta(days=31)

    # Generate a QueryDict object at once and perform querying on the object,
    # instead of accessing it from the database multiple times
    attendance_qset = MessAttendance.objects.filter(date__range=[date_start, date_end])
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']

    # Creation of MessAttendance Objects
    users = User.objects.filter(type='customer')
    for user in users:
        try:
            mess_user = MessUser.objects.get(user=user)
        except:
            MessUser.objects.update_or_create(user=user)
            mess_user = MessUser.objects.get(user=user)
        attendance_qset = attendance_qset.filter(user=mess_user)

        dates = [date_start + datetime.timedelta(days=i) for i in range(33)]
        for dt in dates:
            for meal in meals:
                try:
                    attendance_qset.get(meal=meal, date=dt)
                except:
                    MessAttendance.objects.update_or_create(
                        user=mess_user,
                        meal=meal,
                        date=dt
                    )

    # Deletion of objects from 31 days ago
    del_qset = MessAttendance.objects.filter(date=date_to_del)
    for q in del_qset:
        q.delete()

    print("finished")  # To note that the function is running
