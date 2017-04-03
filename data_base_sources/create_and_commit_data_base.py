import MySQLdb
import StringIO, csv
import pandas as pd
import os

#read data from csv file
data_frame = pd.read_csv('data_brut.csv') 
list_keys=data_frame.columns;
#extraction features 
#print(list_keys[1])
#print(data_frame[0:1])




#settings data base 
HOST = 'localhost'
USER = 'krayni'
PASSWD = 'tunisie20'
DATABASE = 'data_base_krayni'
#create user : CREATE USER 'krayni'@'localhost' IDENTIFIED BY 'tunisie20'
#data base data 
table_data = {

	        'My_data':(

	        ('kyran dale', 'kg@showmedo.com', '2007-09-11',0,'FR'),

	        ('ian ozsvald', 'ian@showmedo.com', '2008-01-11',1,'AR'),

	        ('thomas eddison', 'tom@gec.com', '2007-11-24',1,'TUN'),

	        ('richard coates', 'rc@tinburgen.org', '2008-04-22',0,'EN'),

	        ('karl von frisch', 'kvf@maxplank.ac.de', '2008-01-09',0,'ITA'),

	        ('susan mortimer', 'suzie@backlogger.com', '2007-08-15',1,'USA'),

	        ('alan sussman', 'alan.sussman@gmail.com', '2007-07-15',0,'LIB'),

	        ('bernard reeves', 'bernie@abc.com', '2007-07-23',0,'KSA'),

	        ('phil tensing', 'phit@mmd.com', '2008-02-05',0,'TUN'),

	        ('elaine dean', 'ellie@lotech.com', '2007-11-24',1,'JAP'),

	        )

	    }


#print data base 

def prettyPrint(data):
  print "There are %d data items"%len(data)
  for i,d in enumerate(data):
      print "%d --- "%i, d

#connection 

db_connection = MySQLdb.connect(
	        host=HOST,
	        user=USER,
	        passwd=PASSWD,	        
	           )

cursor = db_connection.cursor()
#GRANT ALL PRIVILEGES ON *.* TO 'krayni'@'localhost' WITH GRANT OPTION; give me all permission 
cursor.execute('use data_base_krayni')

###SQL Part

#use data_base_krayni

#if new table 
#crete_sql="drop table if exists flower_krayni; CREATE TABLE flower_krayni ( name VARCHAR(100), email VARCHAR(100), join_date VARCHAR(100), author_status VARCHAR(100), country  VARCHAR(100))"
#cursor.execute(crete_sql)

#creation of data base 

for data in table_data['My_data']:
     qstr = "INSERT INTO contacts " +\
	            "(name, email, join_date, author_status,country) values ('%s', '%s', '%s', %d,'%s')"%(data[0], data[1], data[2], data[3],data[4])
     #print qstr    


     cursor.execute(qstr)
#save data base 
db_connection.commit() 


save_data_base="mysqldump -u root -p data_base_krayni contacts >users_data_base_CAB.sql"
os.system(save_data_base)








newsql='SELECT * FROM contacts WHERE author_status=0';
cursor.execute(newsql)
A=[]
i=0
for xx in cursor:
   A.insert(i,xx[0]);
   i=i+1;
   print(i)
   print(xx)

print('result') 
print(A)

