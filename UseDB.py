from sqlite3 import connect
from datetime import datetime

class search:
	def today(self, gr):
		for row in self.cur.execute('SELECT "Дата" "ДеньНедели", "ВремяНачала", "Дисциплина", "Преподаватель", "Аудитория" FROM "' + gr + '"  where "ТипЗанятия"="ЛР" ORDER BY "Дата"'):
			return row

	def __init__(self):
		self.con = connect('rasp.db', timeout=5)
		self.cur = self.con.cursor()

class opendb:
	def del_usr(self,message):
		self.cur.execute('DELETE FROM LoginsG WHERE id=?', [int(message.chat.id)])
		self.con.commit()
		self.con.close()

	def ins_id(self, message):
		self.cur.execute('INSERT INTO LoginsG (id) VALUES (?)', [message.chat.id])
		self.con.commit()
		self.con.close()

	def ins_all(self, message):
		self.cur.execute('INSERT INTO LoginsG (id, gr) VALUES (?, ?)', [message.chat.id, message.text])
		self.con.commit()
		self.con.close()

	def upd_gr(self, message):
		self.cur.execute('UPDATE LoginsG SET gr=? WHERE id=?', [message.text, message.chat.id])
		self.con.commit()
		self.con.close()

	def find_gr(self, message):
		gr= ''
		for row in self.cur.execute('SELECT * FROM LoginsG WHERE id=?', [message.chat.id]):
			print('find_gr:',row[2])
			gr = row[2]
		self.con.close()
		return gr

	def find_usr(self, message):
		user_row = ''
		for row in self.cur.execute('SELECT * FROM LoginsG WHERE id=?', [message.chat.id]):
			print(row)
			user_row = row
		self.con.close()
		return user_row

	def __init__(self):
		today_stat = ''
		fileR = open('statistics.txt', 'r')
		file_stat = fileR.read()
		for i in file_stat.split('\n'):
			if datetime.now().strftime('%d.%m.%Y') in i:
				today_stat = i
		print('today_stat:', today_stat, '\n')

		if today_stat == '':
			today_stat = datetime.now().strftime('%d.%m.%Y') + '  all:1'
			file_stat = file_stat + '\n' + today_stat
		else:
			file_stat = file_stat.replace(today_stat, today_stat.split(':')[0] + ':' + str(int(today_stat.split(':')[-1])+1))
		fileR.close()
		
		fileWR = open('statistics.txt', 'w')
		fileWR.write(file_stat)
		fileWR.close()

		self.con = connect('userdb.db', timeout=5)
		self.cur = self.con.cursor()

		self.cur.execute('CREATE TABLE IF NOT EXISTS LoginsG( id Integer, name char(20), gr char(20) )')
		self.con.commit()
		print('init')


#if __name__ == "__main__":
#	print(opendb.find_gr())
