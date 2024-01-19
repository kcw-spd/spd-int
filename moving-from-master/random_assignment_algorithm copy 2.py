from pprint import pprint
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

# Process the DataFrame to create a 'VEHICLE_TYPES' column as a list of types
vehicle_types_columns = [col for col in vehicle_list_df.columns if col.startswith('TYPE_')]
vehicle_list_df['VEHICLE_TYPES'] = vehicle_list_df[vehicle_types_columns].apply(lambda row: [col.replace('TYPE_', '') for col in vehicle_types_columns if row[col]], axis=1)
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
spacious_vehicle_types = ['SUV', 'MID_SIZE_SUV', 'FULL_SIZE_SUV', 'MINIVAN']
# Define luxury vehicle types
# luxury_vehicle_types = {'SEDAN', 'SPORTS_CAR', 'ELECTRIC_VEHICLE', 'FULL_SIZE_SUV'}


# Assuming a mapping of IncomeKey from A (lowest) to higher (more likely to afford luxury)
income_key_mapping = {key: index + 1 for index, key in enumerate(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "U"])}

# Function to assign a random vehicle
def assign_random_vehicle(owner_make, owner_loyalty_score, is_luxury_owner, presence_of_children, income_key):
    weights = []
    for _, row in vehicle_list_df.iterrows():
        weight = 1.0

        # Adjust weight based on loyalty score
        if row['MAKE'] == owner_make:
            weight += owner_loyalty_score

        # Adjust weight for luxury owners
        if is_luxury_owner and row['MAKE'] in luxury_brands:
            weight *= 2

        # Adjust weight for owners with children preferring spacious vehicles
        if presence_of_children == 'Yes' and any(row[type_col] == 1 for type_col in spacious_vehicle_types):
            weight *= 1.5

        # Adjust weight based on income key (higher income, higher weight for luxury vehicles)
        if row['MAKE'] in luxury_brands and income_key >= 15:  # Assuming income keys 15 and above indicate higher income
            weight *= 1.5

        weights.append(weight)

    # Normalize the weights
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]

    # Choose the top 3 vehicles based on the weights
    chosen_indices = np.random.choice(len(vehicle_list_df), size=3, replace=False, p=normalized_weights)
    recommended_vehicles = vehicle_list_df.iloc[chosen_indices]
    return recommended_vehicles[['MAKE', 'MODEL', 'VEHICLE_TYPES']].to_dict('records')
# Function to assign the top 3 most likely vehicles

def perform_sanity_checks(recommended_vehicles, debug_info, vehicle_list_df, luxury_brands, owner_luxury):
    errors = []  # To store any errors found during sanity checks

    # Check if the recommended vehicles' types match one of the types in the dataframe
    for rec in recommended_vehicles:
        make = rec['MAKE']
        model = rec['MODEL']
        has_valid_type = any(vehicle_list_df[(vehicle_list_df['MAKE'] == make) & (vehicle_list_df['MODEL'] == model)][col] == 1 for col in vehicle_list_df.columns if col.startswith('TYPE_'))
        if not has_valid_type:
            errors.append(f"Inappropriate or undefined vehicle type for {make} {model}.")

    # If owner does not own a luxury brand, it's okay to recommend non-luxury brands
    if owner_luxury and not all(rec['MAKE'] in luxury_brands for rec in recommended_vehicles):
        errors.append("Non-luxury brands are being recommended to a luxury brand owner.")

    # Check if the weights are correctly adjusted and normalized
    total_weight = sum(item['Final Weight'] for item in debug_info)
    expected_total_weight = len(debug_info)  # Should be equal to the number of rows iterated over
    if not np.isclose(total_weight, expected_total_weight, rtol=1e-03):
        errors.append(f"Total weight mismatch. Expected ~{expected_total_weight}, got {total_weight}.")

    if errors:
        print("Sanity checks failed with the following errors:")
        for error in errors:
            print(f" - {error}")
    else:
        print("Sanity checks passed.")

def assign_top_vehicles1(owner_make, owner_loyalty_score, is_luxury_owner, presence_of_children, income_key):
    # Initialize weights as 1 for all vehicles
    weights = np.ones(len(vehicle_list_df))
    
    # Adjust weight based on loyalty score
    loyalty_weight_mask = (vehicle_list_df['MAKE'] == owner_make)
    weights[loyalty_weight_mask] += owner_loyalty_score
    
    # Adjust weight for luxury owners
    if is_luxury_owner:
        luxury_mask = vehicle_list_df['MAKE'].isin(luxury_brands)
        weights[luxury_mask] *= 2
    
    # Adjust weight for owners with children preferring spacious vehicles
    if presence_of_children == 'Yes':
        for vehicle_type in spacious_vehicle_types:
            spacious_mask = (vehicle_list_df[vehicle_type] == 1)
            weights[spacious_mask] *= 1.5
    
    # Adjust weight based on income key
    if income_key >= 15:  # Assuming income keys 15 and above indicate higher income
        higher_income_luxury_mask = vehicle_list_df['MAKE'].isin(luxury_brands)
        weights[higher_income_luxury_mask] *= 1.5
    
        # Normalize weights to sum to 1
    weights /= weights.sum()

    # Choose top vehicle based on weights
    chosen_index = np.random.choice(vehicle_list_df.index, p=weights)
    recommended_vehicle = vehicle_list_df.loc[chosen_index]

    # Construct the VEHICLE_TYPES string from the binary columns
    vehicle_types_columns = [col for col in vehicle_list_df.columns if col not in ['MAKE', 'MODEL', 'VEHICLE_TYPES']]
    vehicle_types = '|'.join([col for col in vehicle_types_columns if recommended_vehicle[col] == 1])

    # Add the constructed VEHICLE_TYPES string to the recommended vehicle dictionary
    recommended_vehicle_dict = recommended_vehicle[['MAKE', 'MODEL']].to_dict()
    recommended_vehicle_dict['VEHICLE_TYPES'] = vehicle_types

    return recommended_vehicle_dict

# Refactored function to calculate weights and assign the top 3 vehicles
def assign_top_vehicles(vehicle_list_df, owner_make, owner_loyalty_score, is_luxury_owner, presence_of_children, income_key):
    # Initial weights are 1.0 for all vehicles
    weights = np.ones(len(vehicle_list_df))

    # Adjust weights based on owner's loyalty to the brand
    same_make_mask = (vehicle_list_df['MAKE'] == owner_make)
    weights[same_make_mask] += owner_loyalty_score

    # Double the weight for luxury brands if the owner already owns a luxury brand
    if is_luxury_owner:
        luxury_brand_mask = vehicle_list_df['MAKE'].isin(luxury_brands)
        weights[luxury_brand_mask] *= 2

    # Increase weight by 1.5x for spacious vehicles if the owner has children
    if presence_of_children:
        spacious_mask = vehicle_list_df[spacious_vehicle_types].any(axis=1)
        weights[spacious_mask] *= 1.5

    # Increase weight by 1.5x for luxury brands if the owner's income is high
    if income_key >= 15:
        luxury_and_high_income_mask = vehicle_list_df['MAKE'].isin(luxury_brands)
        weights[luxury_and_high_income_mask] *= 1.5

    # Normalize weights to sum to 1
    weights /= weights.sum()

        # Choose top 3 vehicles based on weights
    chosen_indices = np.random.choice(vehicle_list_df.index, size=3, replace=False, p=weights)
    recommended_vehicles = vehicle_list_df.loc[chosen_indices]

    # Return recommended vehicles with their types
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

# Function to insert recommendations into the database
def insert_recommendations(conn, customer_id, recommendations):
    cursor = conn.cursor()
    for rec in recommendations:
        insert_query = ("INSERT INTO vehicle_recommendations (customer_id, make, model, vehicle_types) "
                        "VALUES (%s, %s, %s, %s)")
        cursor.execute(insert_query, (customer_id, rec['MAKE'], rec['MODEL'], rec['VEHICLE_TYPES']))
    conn.commit()
    cursor.close()

# Function to fetch data and recommend vehicles
def fetch_data_and_recommend(conn):
    cursor = conn.cursor(dictionary=True)
    query = ("SELECT id, PresenceOfChildren, AutoOwnerMake, IncomeKey "
             "FROM inventory_table WHERE InventoryId = 50017786")
    cursor.execute(query)
    records = cursor.fetchall()
    for record in records:
        owner_make = record['AutoOwnerMake'].upper()
        loyalty_score = loyalty_scores.get(owner_make, 0)
        is_luxury_owner = owner_make in luxury_brands
        presence_of_children = record['PresenceOfChildren'] == 'Yes'
        income_key = income_key_mapping.get(record['IncomeKey'].upper(), 0)

        top_vehicles = assign_top_vehicles1(vehicle_list_df, owner_make, loyalty_score, is_luxury_owner, presence_of_children, income_key)
        # insert_recommendations(conn, record['id'], top_vehicles)

        pprint(f"Recommendations for profile {record['id']}:")
        
        # Print all of the individuals relevant information
        pprint(f"Owner Make: {owner_make}")
        pprint(f"Loyalty Score: {loyalty_score}")
        pprint(f"Is Luxury Owner: {is_luxury_owner}")
        pprint(f"Presence of Children: {presence_of_children}")
        pprint(f"Income Key: {income_key}")
        pprint("Make, Model (Vehicle Types):")
                
        for vehicle in top_vehicles:
            # Debugging print statement
            print("Vehicle data:", vehicle)

            # Original print statement adjusted for potential absence of 'VEHICLE_TYPES'
            vehicle_type = vehicle.get('VEHICLE_TYPES', 'Unknown Type')
            pprint(f"{vehicle['MAKE']} {vehicle['MODEL']} ({vehicle_type})")

    
    
if __name__ == '__main__':
    conn = create_db_connection()
    if conn:
        fetch_data_and_recommend(conn)
        conn.close()
    else:
        print("Failed to establish database connection.")