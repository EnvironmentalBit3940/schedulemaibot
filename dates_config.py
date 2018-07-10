#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta

def datetime_object_date(date):
	return datetime(int(date.split('.')[2]), int(date.split('.')[1]), int(date.split('.')[0]))

wd = {1:'Пн', 2:'Вт', 3:'Ср', 4:'Чт', 5:'Пт', 6:'Сб', 7:'Вс', 0:'Пн'}

tomorrow_date = (date.today() + timedelta(days=1)).strftime('%d.%m') + ' ' + wd[(date.today() + timedelta(days=1)).isoweekday()]
today_date = date.today().strftime('%d.%m') + ' ' + wd[date.today().isoweekday()]
