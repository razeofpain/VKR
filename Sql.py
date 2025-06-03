import sqlite3 as sl

class SqlBd:
	def __init__(self, bd_name):
		self.bd_name = bd_name
		self.con = sl.connect(self.bd_name)
		self.cursor = self.con.cursor()

	def create_table(self, request):
		with self.con:
			data = self.con.execute(f"select count(*) from sqlite_master where type='table' and name='{self.bd_name}'")
			for row in data:
				if row[0] == 0:
					with self.con:
						self.con.execute(request)

	def set_data(self, request):
		self.con.execute(request)
		self.con.commit()

	def select_request(self, request):
		self.cursor.execute(request)
		self.con.commit()
		rows = self.cursor.fetchall()
		return rows

	def bd_close(self):
		self.cursor.close()
		self.con.close()