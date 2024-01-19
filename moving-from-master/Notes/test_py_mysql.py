import mysql.connector
from pprint import pprint
import pandas as pd 


# Define the connection parameters
connection_params = {
    "server": "localhost",
    "port": 3306,
    "driver": "MySQL",
    "name": "local",
    "database": "db",
    "username": "root",
    "password": "password1"
}

# Establish the connection
cnx = mysql.connector.connect(
  host=connection_params["server"],
  user=connection_params["username"],
  password=connection_params["password"],
  database=connection_params["database"]
)
# Create a cursor object
cursor = cnx.cursor()

# read a query into a dataframe
df = pd.read_sql("Select * from inventory_table limit 10", cnx)


# Execute a query
cursor.execute("Select * from inventory_table limit 10")


# fetch the headers
headers = [i[0] for i in cursor.description]

# Fetch all the rows
rows = cursor.fetchall()
# print the headers paired with the rows

for row in rows:
  pprint(row)

# Close the connection
cnx.close()