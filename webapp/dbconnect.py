import MySQLdb

def connection():
	conn = MySQLdb.connect(host="localhost",
                           user = "nope",
                           passwd = "nope",
                           db = "nope")
	c = conn.cursor()

	return c, conn

