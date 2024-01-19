from json import load
import pandas as pd
import random
import mysql.connector
import os
from dotenv import load_dotenv

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


# Function definitions
def random_make_model_for_brand_and_type(brand, vehicle_type):
    filtered_df = vehicle_list_df[(vehicle_list_df['MAKE'] == brand) & (vehicle_list_df['VEHICLE_TYPES'].str.contains(vehicle_type))]
    if not filtered_df.empty:
        random_row = filtered_df.sample().iloc[0]
        return random_row['MAKE'], random_row['MODEL']
    return None, None

def weighted_random_selection(weights):
    print("Weights for selection:", weights)
    total = sum(weights.values())
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in weights.items():
        if upto + weight >= r:
            return choice
        upto += weight

def adjust_vehicle_weights(presence_of_children, current_make, vehicle_weights):
    loyalty_score = loyalty_scores.get(current_make.upper(), 0)
    is_luxury = current_make.upper() in luxury_brands
    print(f"Adjusting weights for loyalty (score: {loyalty_score}) and luxury status (is luxury: {is_luxury}).")

    if presence_of_children == 'Yes':
        for vehicle_type in spacious_vehicle_types.intersection(vehicle_weights):
            vehicle_weights[vehicle_type] += 2
            print(f"Increased weight for {vehicle_type} due to presence of children.")

    for vehicle_type in vehicle_weights:
        vehicle_weights[vehicle_type] += loyalty_score
        if is_luxury and vehicle_type in luxury_vehicle_types:
            vehicle_weights[vehicle_type] += 1
            print(f"Increased weight for {vehicle_type} due to luxury status.")

def random_make_model_for_type(vehicle_type):
    filtered_df = vehicle_list_df[vehicle_list_df['VEHICLE_TYPES'].str.contains(vehicle_type)]
    if not filtered_df.empty:
        random_row = filtered_df.sample().iloc[0]
        return random_row['MAKE'], random_row['MODEL']
    return None, None

def assign_vehicle(presence_of_children, current_make, current_model):
    vehicle_types = get_vehicle_types(current_make, current_model)
    vehicle_weights = {vehicle_type: 1 for vehicle_type in vehicle_types}

    adjust_vehicle_weights(presence_of_children, current_make, vehicle_weights)

    loyalty_score = loyalty_scores.get(current_make.upper(), 0)
    if random.random() < loyalty_score:
        recommended_type = weighted_random_selection(vehicle_weights)
        recommended_make, recommended_model = random_make_model_for_brand_and_type(current_make, recommended_type)
    else:
        recommended_make, recommended_model, recommended_type = random_different_brand_model(current_make, vehicle_weights)

    return recommended_type, recommended_make, recommended_model

def get_vehicle_types(make, model):
    vehicle_info = vehicle_type_map.get((make.upper(), model.upper()))
    if vehicle_info:
        return vehicle_info['VEHICLE_TYPES'].split('|')
    return []

def random_different_brand_model(current_make, vehicle_weights):
    other_brands = set(loyalty_scores.keys()) - {current_make.upper()}
    selected_brand = random.choice(list(other_brands))
    vehicle_types = list(vehicle_weights.keys())
    selected_type = random.choice(vehicle_types)
    make, model = random_make_model_for_brand_and_type(selected_brand, selected_type)
    return make, model, selected_type

# Database configuration and connection
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

def fetch_data_and_recommend(conn):
    cursor = conn.cursor(dictionary=True)
    query = "SELECT PresenceOfChildren, AutoOwnerMake, AutoOwnerModel FROM inventory_table ORDER BY RAND() LIMIT 10"
    cursor.execute(query)
    results = cursor.fetchall()
    print(f"Fetched {len(results)} records for processing.")

    for record in results:
        recommended_type, recommended_make, recommended_model = assign_vehicle(
            record['PresenceOfChildren'],
            record['AutoOwnerMake'],
            record['AutoOwnerModel']
        )
        print(f"Profile: {record}, Recommendation: Type - {recommended_type}, Make - {recommended_make}, Model - {recommended_model}")

    cursor.close()

if __name__ == '__main__':
    conn = create_db_connection()
    if conn:
        fetch_data_and_recommend(conn)
        conn.close()
    else:
        print("Failed to establish database connection.")