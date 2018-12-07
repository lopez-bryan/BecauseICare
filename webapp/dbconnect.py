import MySQLdb

# This is where I make the connection to the MySQL database
def connection():
	conn = MySQLdb.connect(host="localhost",
                           user = "vsearch",
                           passwd = "vsearchpasswd",
                           db = "becauseicare")
	c = conn.cursor()

	return c, conn

