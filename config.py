from app import app
from flaskext.mysql import MySQL

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '210713@MONSter'
app.config['MYSQL_DATABASE_DB'] = 'indaba'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)
conn = mysql.connect()
if(conn):
    print('yes')
else:
    print("no connection with the server")    

 