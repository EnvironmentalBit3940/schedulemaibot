import requests
from bs4 import BeautifulSoup
import re
from os import system
from re import match
from requests import get


def get_scheldue(group_name):
#	print('\nВ парсере вход:', group_name, search_day, week_number, allweek, '\n')
	target_url = 'http://www.mai.ru/education/schedule/detail.php?group=' + group_name
	request = requests.get(target_url)
	html_page = BeautifulSoup(request.text, "lxml")
	table_row = html_page.find_all('div', {'class':'sc-container'})
	location_row = html_page.find_all('div', 'sc-table-col sc-item-location')
	dates = [re.findall(r'\d+\.\d+', str(i))[0] for i in html_page.find_all('div', 'sc-table-col sc-day-header sc-blue')] + [re.findall(r'\d+\.\d+', str(i))[0] for i in html_page.find_all('div', 'sc-table-col sc-day-header sc-gray')]
	days = []
	i = 0
	
	date_names = [re.findall(r'>\w\w<', str(i))[0][1:-1] for i in html_page.find_all('span', 'sc-day')]
	dates = [dates[i] + ' ' + date_names[i] for i in range(len(dates))]
	
	for day in table_row:
		days.append({'time':[], 'period':[], 'type':[], 'title':[], 'location':[], 'lecturer':[]})
		for lesson_time in day.find_all('div', 'sc-table-col sc-item-time'):
			days[i]['time'].append(lesson_time.get_text())
			#print(lesson_time)
		
		for type_of_lesson in day.find_all('div', 'sc-table-col sc-item-type'):
			days[i]['type'].append(type_of_lesson.get_text())
		
		for title in day.find_all('div', 'sc-table-col sc-item-title'):
			
			days[i]['title'].append(re.findall(r'>.+<', str(title))[0][1:-1])
			if title.find_all('span', 'sc-lecturer') == []:
				days[i]['lecturer'].append({'name':'None', 'link':'None'})
			else:
				days[i]['lecturer'].append({'name':title.find_all('span', 'sc-lecturer')[0].get_text(), 'link':title.find_all('a')[0].get_text()})
		
		#print('\n')
		#print(html_page.find_all('div', 'sc-table-col sc-item-location'))
		for location_row in day.find_all('div', 'sc-table-col sc-item-location'):
			days[i]['location'].append(location_row.get_text()[1:])
		#else:
		#	days[i]['location'].append(location_row[i].get_text()[1:])
		
		i+=1
	
	#print('\n', days)
	return dates, days
		

def get_session(group_name):
	target_url = 'https://www.mai.ru/education/schedule/session.php?group=' + group_name
	request = requests.get(target_url)
	soup = BeautifulSoup(request.text, "html.parser")

	result = []
	i = 0

	for day in soup.find_all('div', class_="sc-container"):
		day = day.get_text().split('\n')

		for i in range(day.count('')):
			day.pop(day.index(''))

		result.append(day)

		i += 1

	return result


def get_grp_list():
	target_url = 'http://www.mai.ru/education/schedule/'
	request = get(target_url)
	soup = BeautifulSoup(request.text, "html.parser")
	all_groups = []
	raw = []
	
	for part in soup.find_all('div', class_="sc-container"):
		part = part.get_text().split('\n')
				
		for i in range(part.count('')):
			part.pop(part.index(''))
				
		raw.append(part)
		
	for lvl in raw:
		for gr in lvl:
			if match(r'\w+-\w+-\w+', gr) != None:
				all_groups.append(gr)

	return all_groups

if __name__ == '__main__':
	get_scheldue('М4О-311Б-16')
