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


"""def assign_top_vehicles(owner_make, owner_loyalty_score, is_luxury_owner, presence_of_children, income_key):
    weights = []
    debug_info = []  # To store debug information

    print("\n### Debugging Weights Calculation Start ###")  # Start of debugging block

    for index, row in vehicle_list_df.iterrows():
        weight = 1.0
        debug_details = {'Index': index, 'Make': row['MAKE'], 'Model': row['MODEL'], 'Initial Weight': weight}

        print(f"Initial weight for {row['MAKE']} {row['MODEL']}: {weight}")  # Initial weight

        # Adjust weight based on loyalty score
        if row['MAKE'] == owner_make:
            loyalty_bonus = owner_loyalty_score
            weight *= (1 + loyalty_bonus)  # Increase the likelihood for the same make
            debug_details['Loyalty Weight Adjustment'] = f"+{loyalty_bonus}"

        # Adjust weight for luxury owners
        if is_luxury_owner and row['MAKE'] in luxury_brands:
            weight *= 2
            debug_details['Luxury Owner Weight Multiplier'] = 2
            print("Luxury owner: weight doubled")  # Luxury owner adjustment

        # Adjust weight for owners with children preferring spacious vehicles
        if presence_of_children == 'Yes' and any(row[type_col] == 1 for type_col in spacious_vehicle_types):
            weight *= 1.5
            debug_details['Children Weight Multiplier'] = 1.5
            print("Presence of children: weight *= 1.5")  # Children presence adjustment

        # Adjust weight based on income key
        if row['MAKE'] in luxury_brands and income_key >= 15:  # Assuming income keys 15 and above indicate higher income
            weight *= 1.5
            debug_details['Income Weight Multiplier'] = 1.5
            print("Higher income level: weight *= 1.5")  # Income level adjustment

        weights.append(weight)
        debug_details['Final Weight'] = weight
        debug_info.append(debug_details)
        print(f"Final weight for {row['MAKE']} {row['MODEL']}: {weight}")  # Final weight

    print("Total weight before normalization:", sum(weights))  # Total weight before normalization

    # Normalize the weights
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]

    print("Normalized weights:", normalized_weights)  # Normalized weights

    # Choose the top 3 vehicles based on the weights
    chosen_indices = np.random.choice(len(vehicle_list_df), size=3, replace=False, p=normalized_weights)
    recommended_vehicles = vehicle_list_df.iloc[chosen_indices]

    print("\n### Debugging Weights Calculation End ###")  # End of debugging block

    # Debug print
    pprint("Vehicle Selection Debug Information:")
    for info in debug_info:
        if info['Index'] in chosen_indices:
            pprint(info)
    
    # Return both recommended vehicles and debug information
    return recommended_vehicles[['MAKE', 'MODEL', 'VEHICLE_TYPES']].to_dict('records'), debug_info

"""
def assign_top_vehicles(owner_make, owner_loyalty_score, is_luxury_owner, presence_of_children, income_key):
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
    
    # Normalize the weights
    weights /= weights.sum()
    
    # Choose the top 3 vehicles based on the weights
    chosen_indices = np.random.choice(len(vehicle_list_df), size=3, replace=False, p=weights)
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
    query = "SELECT id, PresenceOfChildren, AutoOwnerMake, IncomeKey FROM inventory_table where InventoryId = 50017786"
    cursor.execute(query)
    results = cursor.fetchall()
    for record in results:
        owner_make = record['AutoOwnerMake'].upper()
        loyalty_score = loyalty_scores.get(owner_make, 0)
        is_luxury_owner = owner_make in luxury_brands
        presence_of_children = 'Yes' if record['PresenceOfChildren'] == 'Yes' else 'No'
        income_rank = income_key_mapping.get(record['IncomeKey'].upper(), 0)  # Default to 0 if not found

        owner_luxury = owner_make in luxury_brands
        # top_vehicles, debug_info = assign_top_vehicles(owner_make, loyalty_score, owner_luxury, presence_of_children, income_rank)
        insert_recommendations(conn, record['id'], top_vehicles)
        perform_sanity_checks(top_vehicles, debug_info, vehicle_list_df, luxury_brands, owner_luxury)

        pprint(f"Profile: {record}")
        for vehicle in top_vehicles:
            pprint(f"Recommendation: {vehicle['MAKE']} {vehicle['MODEL']} ({vehicle['VEHICLE_TYPES']})")
    
    cursor.close()
    
    
if __name__ == '__main__':
    conn = create_db_connection()
    if conn:
        fetch_data_and_recommend(conn)
        conn.close()
    else:
        print("Failed to establish database connection.")