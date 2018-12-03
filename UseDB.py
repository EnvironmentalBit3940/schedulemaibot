import postgresql
import psycopg2
from datetime import datetime

#class search:
#	def today(self, gr):
#		for row in self.cur.execute('SELECT "Дата" "ДеньНедели", "ВремяНачала", "Дисциплина", "Преподаватель", "Аудитория" FROM "' + gr + '"  where "ТипЗанятия"="ЛР" ORDER BY "Дата"'):
#			res = row
#		self.con.close()
#		return res

#	def __init__(self):
#		self.con = connect('rasp.db', timeout=5)
#		self.cur = self.con.cursor()

class opendb:
	def del_usr(self,message):
		self.cur.execute('delete from loginsg where id=%s;', [int(message.chat.id)])
		self.con.commit()
		self.con.close()

	def ins_id(self, message):
		self.cur.execute('insert into loginsg (id) values (%s);', [message.chat.id])
		self.con.commit()
		self.con.close()

	def ins_all(self, message):
		self.cur.execute('insert into loginsg (id, gr) values (%s, %s);', [message.chat.id, message.text])
		self.con.commit()
		self.con.close()

	def upd_gr(self, message):
		self.cur.execute('update loginsg set gr=(%s) where id=(%s);', [message.text, message.chat.id])
		self.con.commit()
		self.con.close()

	def find_gr(self, message):
		self.cur.execute('select gr from loginsg where id=%s;', [message.chat.id])
		gr = self.cur.fetchone()[0]
		self.con.close()
		return gr

	def find_usr(self, message):
		self.cur.execute('select * from loginsg where id=%s;', [message.chat.id])
		user_row = self.cur.fetchone()
		self.con.close()
		return user_row

	def __init__(self):
		self.con = psycopg2.connect("dbname=userdb")
		self.cur = self.con.cursor()

		self.cur.execute('CREATE TABLE IF NOT EXISTS LoginsG( id Integer, name char(20), gr char(20) );')
		print('init')


if __name__ == "__main__":
	print(opendb())
