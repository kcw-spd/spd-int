from json import load
import pandas as pd
import random
import mysql.connector
import os
from dotenv import load_dotenv
from random import choices
import numpy as np

load_dotenv()
print("Environment variables loaded.")

# Load the master vehicle list into a Pandas DataFrame
vehicle_list_df = pd.read_csv(r'C:\Users\kylew\Source Path Digital\Code\x_unique_cars_final_types_x_3.csv')
print("Vehicle list DataFrame loaded.")

# Convert the vehicle list DataFrame into a dictionary for easy lookup
vehicle_type_map = vehicle_list_df.set_index(['MAKE', 'MODEL']).to_dict('index')
print("Vehicle type map created.")

load_dotenv()

# Load the master vehicle list into a Pandas DataFrame
vehicle_list_df = pd.read_csv(r'C:\Users\kylew\Source Path Digital\Code\x_unique_cars_final_types_x_3.csv')

# Convert the vehicle list DataFrame into a dictionary for easy lookup
vehicle_type_map = vehicle_list_df.set_index(['MAKE', 'MODEL']).to_dict('index')

# These represent an Auto Owner's loyalty score for each brand
loyalty_scores = {
    'ACURA' : 0.5,
    'ALFA ROMEO' : 0.421,
    'AM GENERAL' : 0,
    'AMC' : 0,
    'AMERICAN MOTORS (AMC)' : 0,
    'ASTON MARTIN' : 0.389,
    'AUDI' : 0.388,
    'BENTLEY' : 0.607,
    'BMW' : 0.644,
    'BUICK' : 0.485,
    'CADILLAC' : 0.478,
    'CHEVROLET' : 0.596,
    'CHRYSLER' : 0.294,
    'DAEWOO' : 0,
    'DAIHATSU' : 0,
    'DATSUN' : 0,
    'DELOREAN' : 0,
    'DODGE' : 0.248,
    'EAGLE' : 0,
    'FERRARI' : 0.587,
    'FIAT' : 0.024,
    'FISKER' : 0,
    'FORD' : 0.734,
    'GENESIS' : 0.575,
    'GEO' : 0,
    'GMC' : 0.502,
    'HONDA' : 0.621,
    'HUMMER' : 0,
    'HYUNDAI' : 0.64,
    'INFINITI' : 0.379,
    'ISUZU' : 0,
    'JAGUAR' : 0.125,
    'JEEP' : 0.527,
    'KARMA' : 0.444,
    'KIA' : 0.648,
    'LAMBORGHINI' : 0.413,
    'LAND ROVER' : 0.376,
    'LEXUS' : 0.553,
    'LINCOLN' : 0.571,
    'LOTUS' : 0,
    'MASERATI' : 0.488,
    'MAYBACH' : 0,
    'MAZDA' : 0,
    'MCLAREN' : 0.455,
    'MERCEDES-BENZ' : 0.543,
    'MERCURY' : 0,
    'MERKUR' : 0,
    'MINI' : 0.409,
    'MITSUBISHI' : 0.533,
    'NISSAN' : 0.609,
    'OLDSMOBILE' : 0,
    'PEUGEOT' : 0,
    'PININFARINA' : 0,
    'PLYMOUTH' : 0,
    'POLESTAR' : 0.412,
    'PONTIAC' : 0,
    'PORSCHE' : 0.529,
    'RAM' : 0.6,
    'RENAULT' : 0,
    'ROLLS-ROYCE' : 0.52,
    'SAAB' : 0,
    'SATURN' : 0,
    'SCION' : 0,
    'SMART' : 0,
    'SUBARU' : 0.624,
    'SUZUKI' : 0,
    'TESLA' : 0.796,
    'TOYOTA' : 0.637,
    'VOLKSWAGEN' : 0.563,
    'VOLVO' : 0.535,
    'WAGONEER' : 0
}

# This is how a person's car is defined as Luxury 
luxury_brands = ['ACURA', 'ALFA ROMEO', 'ASTON MARTIN', 'AUDI', 'BENTLEY', 'BUICK', 'BMW', 'CADILLAC', 'FERRARI', 'FIAT', 'FISKER', 'GENESIS', 'HUMMER', 'INFINITI', 'JAGUAR', 'KARMA', 'LAMBORGHINI', 'LAND ROVER', 'LEXUS', 'LINCOLN', 'LOTUS', 'MASERATI', 'MAYBACH', 'MCLAREN', 'MERCEDES-BENZ', 'MINI', 'PININFARINA', 'POLESTAR', 'PORSCHE', 'ROLLS-ROYCE', 'SAAB', 'TESLA', 'VOLVO']

# Define spacious vehicle types
spacious_vehicle_types = {'SUV', 'MID_SIZE_SUV', 'FULL_SIZE_SUV', 'MINIVAN'}

# Define luxury vehicle types
luxury_vehicle_types = {'SEDAN', 'SPORTS_CAR', 'ELECTRIC_VEHICLE', 'FULL_SIZE_SUV'}


# Assuming a mapping of IncomeKey from A (lowest) to higher (more likely to afford luxury)
income_key_mapping = {chr(i): i - 64 for i in range(65, 91)} # Mapping 'A' to 1, 'B' to 2, ..., 'Z' to 26


# Function to get vehicles that match certain criteria
def get_matching_vehicles(df, make=None, vehicle_types=[]):
    """
    Returns a subset of the given DataFrame `df` that contains vehicles matching the specified `make` and `vehicle_types`.

    Parameters:
        df (DataFrame): The input DataFrame containing vehicle data.
        make (str, optional): The make of the vehicles to filter. Defaults to None.
        vehicle_types (list, optional): The types of vehicles to filter. Defaults to [].

    Returns:
        DataFrame: A subset of the input DataFrame containing vehicles that match the specified make and vehicle types.
    """
    if make:
        df = df[df['MAKE'] == make]
    for vehicle_type in vehicle_types:
        df = df[df[vehicle_type] == 1]
    return df


def random_vehicle_assignment(vehicle_list_df, current_make, presence_of_children):
    """
    Generates a random vehicle assignment based on a list of vehicles, the current make, and the presence of children.

    Args:
        vehicle_list_df (pandas.DataFrame): A DataFrame containing the list of vehicles for random selection.
        current_make (str): The current make of the vehicle.
        presence_of_children (str): Indicates whether there are children present or not. Valid values are 'Yes' or 'No'.

    Returns:
        tuple: A tuple containing the make and model of the chosen vehicle.
    """
    # List of vehicles for random selection
    vehicle_choices = []
    weights = []

    for _, vehicle in vehicle_list_df.iterrows():
        weight = 1.0
        vehicle_make = vehicle['MAKE']

        # Brand loyalty consideration
        if vehicle_make.upper() == current_make.upper():
            weight += loyalty_scores.get(vehicle_make.upper(), 0)

        # Luxury brand preference
        if vehicle_make.upper() in luxury_brands and vehicle['LUXURY'] == 1:
            weight *= 2

        # Spacious vehicle type preference for customers with children
        if presence_of_children == 'Yes':
            if any(vehicle[type_col] == 1 for type_col in spacious_vehicle_types):
                weight *= 2

        vehicle_choices.append((vehicle['MAKE'], vehicle['MODEL']))
        weights.append(weight)
    
    # Use weighted random selection to pick a vehicle
    chosen_vehicle_index = random.choices(range(len(vehicle_choices)), weights=weights, k=1)[0]
    chosen_vehicle = vehicle_choices[chosen_vehicle_index]
    
    print("Chosen vehicle:", chosen_vehicle)  # Print statement for debugging
    
    return chosen_vehicle

# Function to assign a random vehicle from the list
def assign_random_vehicle(owner_make, owner_loyalty_score, is_luxury_owner):
    # Assign weights based on loyalty score and whether the owner has a luxury car
    weights = []
    for index, row in vehicle_list_df.iterrows():
        weight = 1.0
        if row['MAKE'] == owner_make:
            weight += owner_loyalty_score
        if is_luxury_owner and row['MAKE'] in luxury_brands:
            weight *= 2
        weights.append(weight)

    # Normalize the weights
    total_weight = sum(weights)
    normalized_weights = [float(w) / total_weight for w in weights]

    # Choose the top 3 vehicles based on the weights without replacement
    chosen_indices = np.random.choice(
        len(vehicle_list_df),
        size=3,
        replace=False,
        p=normalized_weights
    )
    recommended_vehicles = vehicle_list_df.iloc[chosen_indices]
    return recommended_vehicles[['MAKE', 'MODEL', 'VEHICLE_TYPES']].to_dict('records')

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password1',
    'database': 'db'
}

def create_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        print("Database connection established.")
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
def insert_recommendations(conn, customer_id, presence_of_children, recommendations):
    cursor = conn.cursor()
    for rec in recommendations:
        insert_query = ("INSERT INTO vehicle_recommendations (customer_id, presence_of_children, make, model, vehicle_types) "
                        "VALUES (%s, %s, %s, %s, %s)")
        cursor.execute(insert_query, (customer_id, presence_of_children, rec['MAKE'], rec['MODEL'], rec['VEHICLE_TYPES']))
    conn.commit()
    cursor.close()

def fetch_data_and_recommend(conn):
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, PresenceOfChildren, AutoOwnerMake, IncomeKey FROM inventory_table"
    cursor.execute(query)
    results = cursor.fetchall()

    for record in results:
        owner_make = record['AutoOwnerMake'].upper()
        loyalty_score = loyalty_scores.get(owner_make, 0)
        is_luxury_owner = owner_make in luxury_brands
        presence_of_children = 'Yes' if record['PresenceOfChildren'] == 'Yes' else 'No'
        income_rank = income_key_mapping.get(record['IncomeKey'].upper(), 0) # Default to 0 if not found
        # Get top 3 recommendations
        recommended_vehicles = assign_random_vehicle(owner_make, loyalty_score, is_luxury_owner)
        
        # Insert recommendations into database
        insert_recommendations(conn, record['id'], presence_of_children, recommended_vehicles)

        print(f"Profile: {record}")
        for vehicle in recommended_vehicles:
            print(f"Recommendation: {vehicle['MAKE']} {vehicle['MODEL']}")

    cursor.close()

if __name__ == '__main__':
    conn = create_db_connection()
    if conn:
        fetch_data_and_recommend(conn)
        conn.close()
    else:
        print("Failed to establish database connection.")