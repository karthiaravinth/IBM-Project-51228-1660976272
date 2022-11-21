#IBM DB2
import ibm_db
def db2Connection():
  hs_name = "0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud"
  hs_uid = "hbm87480"
  hs_ps = ""  # password
  hs_dr = "{IBM DB2 ODBC DRIVER}"
  hs_db = "bludb"
  hs_port = "31198"
  hs_pcol = "TCPIP"

  dsn = (
      "DRIVER={0};DATABASE={1};HOSTNAME={2};PORT={3};PROTOCOL={4};UID={5};PWD={6};"
  ).format(hs_dr,hs_db,hs_name,hs_port,hs_pcol,hs_uid,hs_ps)
  try : 
    con = ibm_db.connect(dsn,"","")
    return con
  except:
    return None

def insert(con,username,password):
  sql="INSERT INTO users(username,password) VALUES ({},'{}')".format(username,password)
  out = ibm_db.exec_immediate(con,sql)
  print("Data Inserted Successfully")
  print('Number of affected rows : ',ibm_db.num_rows(out),"\n")

def read():
  username = input("Enter the UserName : ")
  password = input("ENter the Password : ")
  con = db2Connection
  if con is not None:
    insert(con,username,password)
