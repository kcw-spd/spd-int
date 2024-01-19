import pymysql
import numpy as np

# Connect to the MySQL database
db = pymysql.connect(host='localhost', user='your_username', password='your_password', db='your_database')

# Create a cursor object
cursor = db.cursor()

# Execute SQL select statement
cursor.execute("SELECT * FROM your_table")

# Fetch a single row using fetchone() method
data = cursor.fetchone()

# List of available cars
cars = {
    'mid_size_car': ['Car 1', 'Car 2'],
    'full_size_car': ['Car 3', 'Car 4'],
    'suv': ['Car 5', 'Car 6']
}

# Get the vehicle type from the data
vehicle_type = data['VEHICLE_TYPES']

# Use numpy to generate a random index
random_index = np.random.randint(len(cars[vehicle_type]))

# Get a random car from the list
random_car = cars[vehicle_type][random_index]

# Print the selected data and the randomly assigned car
print(f"Selected data: {data}")
print(f"Assigned car: {random_car}")

# Close the database connection
db.close()
