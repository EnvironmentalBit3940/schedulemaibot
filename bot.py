#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  bot.py
#
#  Copyright 2017 Сергей <sergey@Sergey-Tux2>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


import config
import re
import telebot
import time
import parser
from secret_config import TOKEN_NAME as token
from dates_config import today_date, tomorrow_date, datetime_object_date
from parser import get_scheldue, get_grp_list
from UseDB import opendb
from datetime import date, timedelta, datetime
import os
from telebot import types

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['all'])
def send_to_all(message):
	if message.chat.id != 64634999:
		return
	#Дописать for для отправки сообщения всем

@bot.message_handler(commands=['start'])
def handle_start(message):
	print('\nStart ', message.chat.id, datetime.now())
	if opendb().find_usr(message) != None:
		bot.send_message(message.chat.id, config.startagain)
		handle_help(message)
		return

	msg = bot.send_message(message.chat.id, config.start)
	bot.register_next_step_handler(msg, regestration)

def regestration(message):
	all_groups = get_grp_list()
	if not (message.text in all_groups):
		opendb().ins_id(message)
		gr_failture = bot.send_message(message.chat.id, config.completef)
		
		bot.register_next_step_handler(gr_failture, change_gr)
		
	else:
		opendb().ins_all(message)
		bot.send_message(message.chat.id, config.completet)
		current_func = ''
		handle_help(message)

@bot.message_handler(func=lambda message: message.text == 'Назад')
@bot.message_handler(commands=['help'])  # Обрабатывает команду /help
def handle_help(message):
	print('\nHelp ', message.chat.id, datetime.now())
	markup = telebot.types.ReplyKeyboardMarkup()
	markup.row('Расписание занятий', 'Расписание сессии')
	markup.row('Какая сейчас неделя?', 'Когда уже домой?')
	markup.row('Прочее', 'Настройки')
	bot.send_message(message.chat.id, 'Что ты хочешь узнать?', reply_markup=markup)  # Выводит их как ответ от бота


@bot.message_handler(func=lambda message: message.text == 'Настройки')
@bot.message_handler(commands=['settings'])  # Обработка команды /settings
def handle_settings(message):
	print(datetime.now(), "\nнастройки от ", message.chat.id)
	markup = telebot.types.ReplyKeyboardMarkup()
#	markup.row('Оповещения')
	markup.row('📝 Изменить группу')
	markup.row('❌ Сбросить настройки')
	markup.row('Назад')
	bot.send_message(message.chat.id, 'Меню настроек', reply_markup=markup)
	global current_func
	current_func = 'options'


@bot.message_handler(func=lambda message: message.text == 'Какая сейчас неделя?')
def now_week(message):
	print('\nНеделя ', message.chat.id, datetime.now())
	sended_message = ('Сейчас верхняя неделя!' if datetime.now().isocalendar()[1] - (
		34 if datetime.now().isocalendar()[1] < 31 else 0) % 2 == 1 else 'Сейчас нижняя неделя!')
	bot.send_message(message.chat.id, sended_message)


@bot.message_handler(func=lambda message: message.text == 'Расписание сессии')
def session_menu(message):
	print('\nМеню сессии ', message.chat.id, datetime.now())
	markup = telebot.types.ReplyKeyboardMarkup()
	markup.row('Сколько дней до сессии?', 'Расписание экзаменов')
	markup.row('Следующий экзамен')
	markup.row('Назад')
	bot.send_message(message.chat.id, 'Ох, сочувствую.', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Следующий экзамен')
def closest_exam(message):
	print('\nБлижайший экзамен ', message.chat.id, datetime.now())
	group_name = opendb().find_gr(message)

	sess = parser.get_session(group_name)
	sended_message = ''

	i = 0

	day = sess[i]

	if date.today().month != 1 and date.today().month != 6:
		sended_message = 4 * '=' + day[0][0:5] + ' ' + day[0][5::] + 4 * '=' + '\n👤 ' + day[4] + '\n📝 ' + day[
			3] + '\n⌚ Начало в ' + day[1].split(' – ')[0] + '\n📍 ' + (
							 ('В аудитории' + day[-1]) if not ('Кафедра' in day[-1]) else 'На кафедре') + '\n\n'
		bot.send_message(message.chat.id, sended_message)
		return

	print('session: ', sess[i][0].split()[0])

	while i < len(sess) and int(sess[i][0].split()[0].split('.')[0]) <= date.today().day:
		i += 1

	try: day = sess[i]
	except IndexError:
		sended_message = 'Сессия кончилась!'
	else:
		sended_message = 4 * '=' + day[0][0:5] + ' ' + day[0][5::] + 4 * '=' + '\n👤 ' + day[4] + '\n📝 ' + day[
		3] + '\n⌚ Начало в ' + day[1].split(' – ')[0] + '\n📍 ' + (
						 ('В аудитории' + day[-1]) if not ('Кафедра' in day[-1]) else 'На кафедре') + '\n\n'

	bot.send_message(message.chat.id, sended_message)


@bot.message_handler(func=lambda message: message.text == 'Расписание занятий')
def timetable_menu(message):
	print('\nМеню расписания ', message.chat.id, datetime.now())

	markup = telebot.types.InlineKeyboardMarkup()

	today_schedule = types.InlineKeyboardButton(text='На сегодня', callback_data='today_schedule')
	next_lessonInline = types.InlineKeyboardButton(text='Следующая пара', callback_data='next_lesson')
	next_labaInline = types.InlineKeyboardButton(text='Следующая лаба', callback_data='next_laba')
	next_schedule = types.InlineKeyboardButton(text='Следующий учебный день', callback_data='next_schedule')
	week_schedule = types.InlineKeyboardButton(text='На неделю', callback_data='week_schedule')

	markup.add(today_schedule, next_lessonInline, next_labaInline, next_schedule, week_schedule)

	bot.send_message(message.chat.id, 'Выбери из предложенного', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Расписание сессии')
def session_date(message):
	print('\nМеню расписания сессии', message.chat.id, datetime.now())

	markup = telebot.types.InlineKeyboardMarkup()

	next_examInline = types.InlineKeyboardButton(text='Следующий экзамен', callback_data='next_exam')
	all_examsInline = types.InlineKeyboardButton(text='На неделю', callback_data='week_schedule')

	markup.add(next_examInline, all_examsInline)

	bot.send_message(message.chat.id, 'Выбери из предложенного', reply_markup=markup)

@bot.message_handler(func=lambda message: '📝 Изменить группу' == message.text)
def edit_information(message):
	print(datetime.now(), "\nРедактирование информации в настройках от ", message.chat.id, message.chat.username)
	bot.send_message(message.chat.id, 'Напиши мне свою группу в формате М**-***-**')
	global current_func
	current_func = 'change_group'


@bot.message_handler(func=lambda message: '❌ Сбросить настройки' == message.text and current_func == 'options')
def delete(message):
	print(datetime.now(), "Сброс настроек от ", message.chat.id, message.chat.username)
	markup = telebot.types.ReplyKeyboardMarkup()
	markup.row('🔥 Да', '🚫 Нет')
	msg = bot.send_message(message.chat.id, 'Вы уверены?', reply_markup=markup)
	bot.register_next_step_handler(msg, sure)

def sure(message):
	if message.text == '🔥 Да':
		opendb().del_usr(message)
		bot.send_message(message.chat.id, 'Данные удалены')
	
	else:
		handle_help(message)


@bot.message_handler(func=lambda message: message.text == 'Сколько дней до сессии?')
def enspiration_date(message):
	print(datetime.now(), 'Время до сессии', message.chat.id, message.chat.username)
	if 2 <= date.today().month < 6:
		bot.send_message(message.chat.id,
						 'До июня осталось ' + str(date(date.today().year, 6, 1) - date.today()).split()[
							 0] + ' дней, ' + 'есть ещё много времени' if int(
							 str(date(2017, 6, 1) - date.today()).split()[
								 0]) > 30 else 'можно начинать ходить на пары, чтобы препод знал хоть, как ты выглядишь')
	elif 9 <= date.today().month:
		bot.send_message(message.chat.id, 'До января осталось ' + str(int(
			str(date(date.today().year, 12, 1) - date.today()).split()[
				0]) + 31) + ' дней, ' + 'есть ещё много времени' if int(str(date(2017, 6, 1) - date.today()).split()[
																			0]) > 30 else 'можно начинать ходить на пары, чтобы препод знал хоть, как ты выглядишь')
	elif date.today().month == 1 or date.today().month == 6:
		bot.send_message(message.chat.id, 'Иногда люди начинают готовиться к сессии в это время.')
	else:
		bot.send_message(message.chat.id, 'Дай отдохнуть, лето же!')


@bot.message_handler(func=lambda message: message.text == 'Расписание экзаменов') 
def session_timetable(message):
	print('\nРасписание экзаменов', message.chat.id, datetime.now())
	group_name = opendb().find_gr(message)

	sess = parser.get_session(group_name)
	sended_message = ''

	for day in sess:
		sended_message += 4 * '=' + day[0][0:5] + ' ' + day[0][5::] + 4 * '=' + '\n👤 ' + day[4] + '\n📝 ' + day[
			3] + '\n⌚ Начало в ' + day[1].split(' – ')[0] + '\n📍 ' + (
							  ('В аудитории' + day[-1]) if not ('Кафедра' in day[-1]) else 'На кафедре') + '\n\n'

	bot.send_message(message.chat.id, sended_message)
	print(sended_message)
	
@bot.message_handler(func=lambda message: message.text == 'Прочее')
def other(message):
	bot.send_message(message.chat.id, 'Скоро тут будет хорошо. Но не сегодня :)')
	return


@bot.callback_query_handler(func=lambda call: call.data == 'next_schedule')
def next_schedule(call):
	group_name = opendb().find_gr(call.message)
	print(group_name)
	dates, schedule = get_scheldue(group_name)
	sended_message = ''
	
	nowtime = (datetime.now() + timedelta(hours=3)).strftime('%H:%M')
	
	next_date = 0
	
	if not today_date in dates or nowtime < schedule[dates.index(today_date)]['time'][0].split()[0]:
		search_date = 0
	elif tomorrow_date in dates and nowtime > schedule[dates.index(today_date)]['time'][0].split()[0]:
		search_date = dates.index(tomorrow_date)
	else:
		search_date = 1
	

	try:
		day = schedule[search_date]
		sended_message += '===={}====\n'.format(dates[search_date])
		for j in range(len(schedule[search_date]['title'])):
			sended_message += '⌚' + day['time'][j] + '\n📝' + day['title'][j] + (('\n👤' + day['lecturer'][j]['name']) if (day['lecturer'][j]['name'] != 'None') else '') + ('\n📍' + day['location'][j] + '\n' if day['location'][j] != 'None' else '\n') + day['type'][j] + '\n'
			sended_message += '''
			'''
	except ValueError:
		sended_message = 'Пар нет, отдыхай :)'
	bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=sended_message)

@bot.callback_query_handler(func=lambda call: call.data == 'today_schedule')
def tomorrow_table(call):
	group_name = opendb().find_gr(call.message)
	print(group_name)
	dates, schedule = get_scheldue(group_name)
	sended_message = ''
	search_date = today_date

	try:
		i = dates.index(search_date)
		sended_message += '===={}====\n'.format(dates[i])
		for j in range(len(schedule[i]['title'])):
			print()
			sended_message += '⌚' + schedule[i]['time'][j] + '\n📝' + schedule[i]['title'][j] + (('\n👤' + schedule[i]['lecturer'][j]['name']) if (schedule[i]['lecturer'][j]['name'] != 'None') else '') + ('\n📍' + schedule[i]['location'][j] + '\n' if schedule[i]['location'][j] != 'None' else '\n') + schedule[i]['type'][j] + '\n'
			sended_message += '''
			'''
	except ValueError:
		sended_message = 'Пар нет, отдыхай :)'

	print('\nОтправляемое сообщение (Сегодня/завтра):\n\n', group_name, '\n', sended_message, '\n')
	bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=sended_message)


@bot.callback_query_handler(func=lambda call: call.data == 'next_lesson') 
def next_lesson(call):
	group_name = opendb().find_gr(call.message)
	
	dates, schedule = get_scheldue(group_name) #Выбираем группу
	sended_message = '' 

	search_date = today_date

	try:
		i = dates.index(search_date)
		day = schedule[i] #Берем расписание на сегодня
		j = 0
		nowtime = (datetime.now() + timedelta(hours=3)).strftime('%H:%M') #Поправка на отличие времени сервера
		
		while sended_message == '' and j < len(day['time']):
			tdy_time = day['time'][j]

			if nowtime < tdy_time.split()[0]:
				lctr = '👤{}\n'.format(day['lecturer'][j]['name']) if (day['lecturer'][j]['name'] != 'None') else ''
				lctn = '📍{}\n'.format(day['location'][j]) if day['location'][j] != 'None' else '\n'
				
				sended_message = 'Следующая пара: \n\n===== {} =====\n⌚ {}\n📝{}\n{}{}{}'.format(dates[i], day['time'][j], day['title'][j], lctr, lctn, day['type'][j])

			j += 1
			
		if sended_message == '':
			day = schedule[dates.index(tomorrow_date)]
			lctr = '👤{}\n'.format(day['lecturer'][0]['name']) if (day['lecturer'][0]['name'] != 'None') else ''
			lctn = '📍{}\n'.format(day['location'][0]) if day['location'][0] != 'None' else '\n'
			sended_message = 'Следующая пара: \n\n===== {} =====\n⌚ {}\n📝{}\n{}{}{}'.format(dates[i], day['time'][0], day['title'][0], lctr, lctn, day['type'][0])
#			sended_message = 'Сегодня больше нет пар, отдыхай :)'
		
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=sended_message)
		
	except Exception as e:
		sended_message = 'Тут ошибка'
		bot.send_message(call.message.chat.id, sended_message)
		bot.send_message(64634999, 'Следующую пару не нашел у ' + group_name + 'по причине ' + e)
	

@bot.message_handler(func=lambda message: 'Когда уже домой?' == message.text)
def when_freedom(message):
	print(datetime.now(), "\nКогда домой ", message.chat.id, message.chat.username)
	group_name = opendb().find_gr(message)
	print(group_name)
	dates, schedule = get_scheldue(group_name)
	sended_message = ''

	try:
		i = dates.index(today_date)

		for j in range(len(schedule[i]['time'])):

			lesson_start_time = re.findall(r'\d\d:\d\d', schedule[i]['time'][j])[0]
			lesson_end_time = re.findall(r'\d\d:\d\d', schedule[i]['time'][j])[1]

			if lesson_start_time < datetime.now().strftime('%H:%M:%S') < lesson_end_time:
				hour = int(lesson_end_time[0:2]) - int(datetime.now().strftime('%H'))
				minute = int(lesson_end_time[3:5]) - int(datetime.now().strftime('%M'))

				if minute < 0:
					hour -= 1
					minute += 60

				time_end = str(hour) + ':' + str(minute) if len(str(minute)) > 1 else str(hour) + ':0' + str(minute)

			elif lesson_start_time > datetime.now().strftime(
					'%H:%M:%S') and buf != lesson_start_time:
				i += 1
			buf = lesson_start_time

		if i > 1:
			if time_end != '':
				sended_message = 'Осталось ещё {} до конца пары, а потом ещё {} пары'.format(time_end, str(i))

			else:
				sended_message = 'Осталось ещё {} пары'.format(str(i))
		elif i == 1:
			if time_end != '':
				sended_message = 'Осталось ещё {} до конца пары, а потом ещё 1 парa'.format(time_end)

			else:
				sended_message = 'Осталось ещё 1 парa'
		else:
			if time_end != '':
				sended_message = 'Осталось ещё {} до конца пары, а потом домой!'.format(time_end)

			else:
				sended_message = 'Ты уже свободен на сегодня'


	except ValueError:
		sended_message = 'На сегодня ты свободен!'



	bot.send_message(message.chat.id, sended_message)
	print('\nОтправляемое сообщение (Когда домой):\n\n', group_name, sended_message, '\n')


@bot.callback_query_handler(func=lambda call: call.data == 'week_schedule')
def week_table(call):
	group_name = opendb().find_gr(call.message)
	print(group_name)
	dates, schedule = get_scheldue(group_name)
	sended_message = ''

	print(dates)
	for i in range(len(dates)):
		sended_message += '===={}====\n'.format(dates[i])
		for j in range(len(schedule[i]['title'])):
			print()
			sended_message += '⌚' + schedule[i]['time'][j] + '\n📝' + schedule[i]['title'][j] + (('\n👤' + schedule[i]['lecturer'][j]['name']) if (schedule[i]['lecturer'][j]['name'] != 'None') else '') + ('\n📍' + schedule[i]['location'][j] + '\n' if schedule[i]['location'][j] != 'None' else '\n') + schedule[i]['type'][j] + '\n'
			sended_message += '\n'
		sended_message += '\n'

	if sended_message == '':
		sended_message = 'Пар нет или расписание не закончено'

	bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=sended_message)
	print('\nОтправляемое сообщение (Неделя):\n\n', group_name, '\n', sended_message, '\n')

@bot.callback_query_handler(func=lambda call: call.data == 'next_laba')
def next_laba(call):
	group_name = opendb().find_gr(call.message)
	print(group_name)
	dates, schedule = get_scheldue(group_name)
	
	done = False
	i = 0
	
	while not done:
		try:
			day = schedule[i]
		
		except IndexError:
			sended_message = 'Лабы не скоро :)'
		
		try:
			done = True
			
			lsn_indx = day['type'].index('ЛР')
			lctr = ('👤{}\n'.format(day['lecturer'][lsn_indx]['name']) if (day['lecturer'][lsn_indx]['name'] != 'None') else '')
			lctn = '📍{}\n'.format(day['location'][lsn_indx]) if day['location'][lsn_indx] != 'None' else '\n'
			sended_message = 'Следубщая лабораторная:\n\n===== {} =====\n⌚ {}\n📝{}\n{}{}'.format(dates[i], day['time'][lsn_indx], day['title'][lsn_indx], lctr, lctn) 
			
		except:
			done = False
			
		i += 1
	bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=sended_message)
	print('\nОтправляемое сообщение (Неделя):\n\n', group_name, '\n', sended_message, '\n')


@bot.message_handler(func=lambda message: 'Об авторах' == message.text)
def developers(message):
	print(datetime.now(), '\ncredits от', message.chat.id)
	bot.send_message(message.chat.id, config.contacts)


@bot.message_handler(func=lambda message: current_func == 'change_group')
def change_gr(message):
	print('\nПоменяй группу ', message.chat.id, datetime.now())

	all_groups = get_grp_list()

	if not (message.text in all_groups):
		bot.send_message(message.chat.id, config.completef)
		return

	opendb().upd_gr(message)

	bot.send_message(message.chat.id, config.completet)
	handle_help(message)


@bot.message_handler(content_types=["text"])  # Обрабатывет все текстовые сообщения, полученные от пользователя
def repeat_all_messages(message):
	all_groups = get_grp_list()

	user_row = opendb().find_usr(message)

	print('User_row:', user_row)
	print(datetime.now(), 'Обработка всех сообщений. Сообщение - ', message.text, user_row)
	
	if user_row == None or user_row[2] == None:
		msg = bot.send_message(message.chat.id, 'А у тебя тут группа не записана, напиши мне шифр своей группы в формате М**-****-** (Если не ранее 2016 года поступления) или **-****-** (В иных случаях) (Третья звездочка - буква О, а не нолик! [Это для очников, в вечерке там В]), например: М4О-211Б-16 или 4О-404Б-14, если ваш факультет прикрепили к кому-то, то *-***-****-**')
		if user_row == None:
			opendb().ins_id(message)
		
		bot.register_next_step_handler(msg, change_gr)
	
	
if __name__ == '__main__':
	current_func = ''
	bot.polling(none_stop=True)  # Благодаря этой строке бот проверяет обновления в диалоге постоянно

# cur.execute('INSERT INTO Logins VALUES (?,?,?,?)', [message.chat.id, message.chat.username, course, gruppa])
# con.commit()
#		print(message.chat.username, "приглашает тебя по пиву!")
#		bot.send_message(message.chat.id, 'Разраб уже оповещен и рад слышать! (Главное - чтоб не в электричке. Разраб в электричке больше не пьет..)')
#		bot.send_message('64634999', '@' + message.chat.username + ' приглашает тебя выпить по пиву!')
