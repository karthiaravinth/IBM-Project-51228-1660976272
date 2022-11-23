#IBM DB2
import ibm_db
def db2Connection():
  hs_name = "0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud"
  hs_uid = "hbm87480"
  hs_ps = "Fmn5XBVS2UsAATS6"
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

