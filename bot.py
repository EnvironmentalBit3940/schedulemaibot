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
from parser import get_scheldue
from UseDB import opendb
from datetime import date, timedelta, datetime
import os

bot = telebot.TeleBot(token)


def take_schedule(message, group_name):
	print('\n', group_name, '\n')
	schedule = ''
	if group_name == None or group_name == '':
		bot.send_message(message.chat.id, 'В базе не найден. Попробуй удалить номер группы и записать заново')
	try:
		try:
			schedule = open('data/' + group_name + '.txt', 'r').read().split('\ufeff')[-1].split('\n')
		except TypeError:
			print('TypeError! Хз с чего он')
			bot.send_message(message.chat.id,
							 'Ошибка! Попробуй удалить номер группы и записать заного. Если не помогло - отправь скрин диалога @forgottenmemes')

	except FileNotFoundError:
		print('Нет расписания! Группа = ', group_name)
		bot.send_message(message.chat.id,
						 'Ошибка! Попробуй удалить номер группы и записать заного. Если не помогло - отправь скрин диалога @forgottenmemes')
		open('gr_404.txt', 'w').write(group_name)

	return schedule
	

@bot.message_handler(commands=['start'])
def handle_start(message):
	print('\nStart ', message.chat.id, datetime.now())
	if opendb().find_usr(message) != None:
		bot.send_message(message.chat.id, config.startagain)
		handle_help(message)
		return

	current_func = 'change_group'
	bot.send_message(message.chat.id, config.start)


@bot.message_handler(commands=['help'])  # Обрабатывает команду /help
def handle_help(message):
	print('\nHelp ', message.chat.id, datetime.now())
	markup = telebot.types.ReplyKeyboardMarkup()
	markup.row('Какая следующая пара?', 'Узнать расписание')
	markup.row('Когда уже домой?')
	markup.row('Какая сейчас неделя?', 'Об авторах')
	markup.row('Настройки')
	bot.send_message(message.chat.id, 'Что ты хочешь узнать?', reply_markup=markup)  # Выводит их как ответ от бота


@bot.message_handler(commands=['settings'])  # Обработка команды /settings
def handle_settings(message):
	print(datetime.now(), "\nнастройки от ", message.chat.id)
	markup = telebot.types.ReplyKeyboardMarkup()
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


@bot.message_handler(func=lambda message: message.text == 'Сессия')
def session_menu(message):
	print('\nМеню сессии ', message.chat.id, datetime.now())
	markup = telebot.types.ReplyKeyboardMarkup()
	markup.row('Сколько дней до сессии?', 'Расписание экзаменов')
	markup.row('Ближайший экзамен')
	markup.row('Назад')
	bot.send_message(message.chat.id, 'Ох, сочувствую.', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Ближайший экзамен')
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


@bot.message_handler(func=lambda message: message.text == 'Узнать расписание')
def timetable_menu(message):
	print('\nМеню расписания ', message.chat.id, datetime.now())
	markup = telebot.types.ReplyKeyboardMarkup()
	markup.row('На завтра', 'На сегодня')
	markup.row('На неделю', 'Какая лаба следующая?')
	markup.row('Назад')
	bot.send_message(message.chat.id, 'Расписание чего?', reply_markup=markup)


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
	bot.send_message(message.chat.id, 'Вы уверены?', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🔥 Да')
def sure(message):
	opendb().del_usr(message)
	bot.send_message(message.chat.id, 'Данные удалены')


@bot.message_handler(func=lambda message: message.text == '🚫 Нет' or message.text == 'Назад')
def back(message):
	current_func == ''
	handle_help(message)


@bot.message_handler(func=lambda message: message.text == 'Настройки')
def setting(message):
	handle_settings(message)


@bot.message_handler(func=lambda message: message.text == 'Репозиторий лямбды на гите')
def labda_on_git(message):
	bot.send_message(message.chat.id, config.lambdaongit)


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
def session_date(message):
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


@bot.message_handler(
	func=lambda message: 'На завтра' == message.text or 'На сегодня' == message.text)
def tomorrow_table(message):
	print(datetime.now(), "\nНа сегодня\завтра ", message.chat.id, message.chat.username)
	group_name = opendb().find_gr(message)
	print(group_name)
	dates, schedule = get_scheldue(group_name)
	sended_message = ''
	
	if 'На завтра' == message.text:
		search_date = tomorrow_date
	else:
		search_date = today_date
	
	try:
		i = dates.index(search_date)
		sended_message += '===={}====\n'.format(dates[i])
		for j in range(len(schedule[i]['title'])):
			print()
			sended_message += '⌚' + schedule[i]['time'][j] + '\n📝' + schedule[i]['title'][j] + (('\n👤' + schedule[i]['lecturer'][j]['name']) if (schedule[i]['lecturer'][j]['name'] != 'None') else '') + ('\n📍' + schedule[i]['location'][j] + '\n' if schedule[i]['location'][j] != 'None' else '\n') + schedule[i]['type'][j] + '\n'
		
	except ValueError:
		sended_message = 'Пар нет, отдыхай :)'
	
	print('\nОтправляемое сообщение (Сегодня/завтра):\n\n', group_name, '\n', sended_message, '\n')
	bot.send_message(message.chat.id, sended_message)


@bot.message_handler(func=lambda message: 'Какая следующая пара?' == message.text)  # Останавливать его на след. день
def next_lesson(message):
	return
	print(datetime.now(), "\nСлед. пара ", message.chat.id, message.chat.username)
	group_name = opendb().find_gr(message)
	print(group_name)
	schedule = take_schedule(message, group_name)
	search_date = date.today().strftime('%d.%m.%Y')
	sended_message = ''

	for day in schedule:

		if day == '':
			break

		lesson_date = re.match(r'\d{2}\.\d{2}\.\d{4}', day).group()
		lesson_start_time = re.findall(r'\d+:\d{2}:\d{2}', day)[0]

		if lesson_start_time == '9:00:00':
			lesson_start_time = '09:00:00'

		lesson_name = day.split('\t')[-4]
		if lesson_name == 'Военная кафедра':
			break
		lesson_teacher_name = day.split('\t')[-3]
		try:
			lesson_type = config.types_of_lessons[day.split('\t')[-1]]
		except KeyError:
			lesson_type = day.split('\t')[-1]
		lesson_location = day.split('\t')[-2]

		if lesson_date == search_date and lesson_start_time > datetime.now().strftime('%H:%M:%S'):
			sended_message = 'Следующая пара:\n' '⌚' + lesson_start_time[:-3] + '\n📝' + lesson_name + (
				('\n👤' + lesson_teacher_name + '\n📍') if (
							lesson_teacher_name != 'NONAME NONAME ') else '\n📍') + lesson_location + '\n' + lesson_type + '\n'
			break

	if sended_message == '':
		sended_message = 'Сегодня больше нет пар :)'

	bot.send_message(message.chat.id, sended_message)
	print('\nОтправляемое сообщение (След. пара):\n\n', group_name, '\n', sended_message, '\n')


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


@bot.message_handler(func=lambda message: 'На неделю' == message.text)
def week_table(message):
	print(datetime.now(), "\nНа неделю ", message.chat.id, message.chat.username)
	group_name = opendb().find_gr(message)
	print(group_name)
	dates, schedule = get_scheldue(group_name)
	sended_message = ''
	
	for i in range(len(dates)):
		sended_message += '===={}====\n'.format(dates[i])
		for j in range(len(schedule[i]['title'])):
			print()
			sended_message += '⌚' + schedule[i]['time'][j] + '\n📝' + schedule[i]['title'][j] + (('\n👤' + schedule[i]['lecturer'][j]['name']) if (schedule[i]['lecturer'][j]['name'] != 'None') else '') + ('\n📍' + schedule[i]['location'][j] + '\n' if schedule[i]['location'][j] != 'None' else '\n') + schedule[i]['type'][j] + '\n'
		
		sended_message += '\n'
		
	bot.send_message(message.chat.id, sended_message)
	print('\nОтправляемое сообщение (Неделя):\n\n', group_name, '\n', sended_message, '\n')


@bot.message_handler(func=lambda message: 'Какая лаба следующая?' == message.text)
def next_laba(message):
	return
	print(datetime.now(), "\nЛабы ", message.chat.id, message.chat.username)
	group_name = opendb().find_gr(message)
	print(group_name)
	schedule = take_schedule(message, group_name)
	search_date = date.today().strftime('%d.%m.%Y')
	sended_message = ''

	for day in schedule:
		if day == None or day == ' ':
			break
		lesson_date = re.match(r'\d{2}\.\d{2}\.\d{4}', day).group()
		lesson_start_time = re.findall(r'\d+:\d{2}:\d{2}', day)[0]
		lesson_name = day.split('\t')[-4]
		lesson_day_name = day.split('\t')[1]

		if lesson_name == 'Военная кафедра' or day == '':
			break

		lesson_teacher_name = day.split('\t')[-3]

		try:
			lesson_type = config.types_of_lessons[day.split('\t')[-1]]
		except KeyError:
			lesson_type = day.split('\t')[-1]

		lesson_location = day.split('\t')[-2]

		if 'Лабораторная' in lesson_type:
			sended_message = 'Следующая лаба:\n' + '===== ' + lesson_day_name + ' =====\n⌚' + lesson_start_time[
																							  :-3] + '\n📝' + lesson_name + (
								 ('\n👤' + lesson_teacher_name + '\n📍') if (
											 lesson_teacher_name != 'NONAME NONAME ') else '\n📍') + lesson_location + '\n'
			break

	if sended_message == '':
		sended_message = 'Лабы не скоро :)'

	bot.send_message(message.chat.id, sended_message)
	print('\nОтправляемое сообщение (Неделя):\n\n', group_name, '\n', sended_message, '\n')


@bot.message_handler(func=lambda message: 'Об авторах' == message.text)
def developers(message):
	print(datetime.now(), '\ncredits от', message.chat.id)
	bot.send_message(message.chat.id, config.contacts)


@bot.message_handler(func=lambda message: current_func == 'change_group')
def change_gr(message):
	print('\nПоменяй группу ', message.chat.id, datetime.now())
	all_groups = os.listdir('data')

	if not (message.text + '.txt') in all_groups:
		bot.send_message(message.chat.id, config.completef)
		return

	opendb().upd_gr(message)

	bot.send_message(message.chat.id, config.completet)
	global current_func
	current_func = ''
	handle_help(message)


@bot.message_handler(content_types=["text"])  # Обрабатывет все текстовые сообщения, полученные от пользователя
def repeat_all_messages(message):
	print(message.text, message.chat.id, datetime.now())
	global current_func
	current_func = 'change_group'

	all_groups = os.listdir('data')

	user_row = opendb().find_usr(message)

	print('User_row:', user_row, 'n')
	print(datetime.now(), 'Обработка всех сообщений. Сообщение - ', message.text, user_row)

	if user_row != None and user_row != '':
		current_func = ''
		return

	print(datetime.now(), "Группы нет ", message.chat.id, message.chat.username)

	if not ((message.text + '.txt') in all_groups):
		opendb().ins_id(message)
		bot.send_message(message.chat.id, config.completef)
	else:
		opendb().ins_all(message)
		bot.send_message(message.chat.id, config.completet)
		current_func = ''
		handle_help(message)

if __name__ == '__main__':
	current_func = ''
	bot.polling(none_stop=True)  # Благодаря этой строке бот проверяет обновления в диалоге постоянно

# cur.execute('INSERT INTO Logins VALUES (?,?,?,?)', [message.chat.id, message.chat.username, course, gruppa])
# con.commit()
#		print(message.chat.username, "приглашает тебя по пиву!")
#		bot.send_message(message.chat.id, 'Разраб уже оповещен и рад слышать! (Главное - чтоб не в электричке. Разраб в электричке больше не пьет..)')
#		bot.send_message('64634999', '@' + message.chat.username + ' приглашает тебя выпить по пиву!')
