# take a file path and create a table in the database, read the header row, and create the table with all text values
# if the table already exists, append a numeric value to the end of the table name
# 

import mysql.connector
from pprint import pprint
import csv
import os
import re
import sys
import argparse

# Define the connection parameters
from test_py_mysql import connection_params

# Establish the connection
cnx = mysql.connector.connect(
  host=connection_params["server"],
  user=connection_params["username"],
  password=connection_params["password"],
  database=connection_params["database"]
)
# Create a cursor object
cursor = cnx.cursor()


def create_table_from_csv(csv_file_path):
    # read the csv file
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # get the header row
        header_row = next(reader)
        # print(header_row)
        # create the table name from the file name
        table_name = os.path.splitext(os.path.basename(csv_file_path))[0]
        # if the table already exists, append a numeric value to the end of the table name
        if table_name in get_table_names():
            table_name = table_name + "_1"
        # create the table
        create_table(table_name, header_row)
        # insert the data
        insert_data(table_name, reader)
        # commit the changes
        cnx.commit()
        