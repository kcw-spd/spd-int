import pandas as pd
import numpy as np
import mysql.connector
from pprint import pprint

# Load the master vehicle list into a Pandas DataFrame
vehicle_list_df = pd.read_csv(r'C:\Users\kylew\Source Path Digital\Code\x_unique_cars_final_types_x_3.csv')

# Extracting vehicle types columns
vehicle_types_columns = [col for col in vehicle_list_df.columns if col not in ['MAKE', 'MODEL']]
vehicle_list_df['VEHICLE_TYPES'] = vehicle_list_df[vehicle_types_columns].apply(lambda x: '|'.join(x.index[x.astype(bool)]), axis=1)

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
def adjust_weights_for_preferences(vehicle_list_df, current_vehicle_types, has_children, luxury_multiplier, loyalty_factor, owner_make):
    weights = np.ones(len(vehicle_list_df))

    # Adjust for current vehicle type preference
    for vehicle_type in current_vehicle_types:
        type_mask = vehicle_list_df[vehicle_type] == 1
        weights[type_mask] *= 1.5  # Increase the weight for preferred types
        print(f"Weights after adjusting for vehicle type {vehicle_type} preference:", weights[type_mask][:10])  # Print first 10 for brevity

    # Adjust for presence of children
    if has_children:
        family_friendly_types = spacious_vehicle_types # ['SUV', 'MINIVAN', 'LARGE_CAR']  # Define family-friendly vehicle types
        for ff_type in family_friendly_types:
            family_friendly_mask = vehicle_list_df[ff_type] == 1
            weights[family_friendly_mask] *= 1.2  # Slightly increase the weight for family-friendly vehicles
            print(f"Weights after adjusting for family-friendly type {ff_type}:", weights[family_friendly_mask][:10])

    # Adjust for luxury preference based on income
    luxury_mask = vehicle_list_df['MAKE'].isin(luxury_brands)
    weights[luxury_mask] *= luxury_multiplier
    print("Weights after adjusting for luxury preference:", weights[luxury_mask][:10])

    # Apply loyalty factor to the current vehicle's make
    same_make_mask = vehicle_list_df['MAKE'] == owner_make
    weights[same_make_mask] *= loyalty_factor
    print(f"Weights after applying loyalty factor for {owner_make}:", weights[same_make_mask][:10])

    return weights

def assign_top_vehicles(vehicle_list_df, owner_vehicle_info, is_luxury_owner, presence_of_children, income_key):
    # Extract current vehicle make and types
    owner_make = owner_vehicle_info['MAKE']
    current_vehicle_types = owner_vehicle_info['VEHICLE_TYPES'] # Assuming this is a list of types

    # Calculate loyalty and luxury multipliers
    loyalty_score = loyalty_scores.get(owner_make, 0)
    loyalty_factor = 1 + (loyalty_score ** 2)
    income_scale = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9, "J": 10, "K": 11, "L": 12, "M": 13, "N": 14, "O": 15, "P": 16, "Q": 17, "R": 18, "U": 19}
    income_value = income_scale.get(income_key, 1)
    luxury_multiplier = 1 + (income_value / len(income_scale))
    print("Luxury multiplier:", luxury_multiplier)
    print("Loyalty factor:", loyalty_factor)

    # Adjust weights based on preferences
    weights = adjust_weights_for_preferences(vehicle_list_df, current_vehicle_types, presence_of_children, luxury_multiplier, loyalty_factor, owner_make)

    # Normalize the weights
    weights /= weights.sum()
    print("Normalized weights:", weights[:10])

    # Choose top 3 vehicles based on weights
    chosen_indices = np.random.choice(vehicle_list_df.index, size=3, replace=False, p=weights)
    recommended_vehicles = vehicle_list_df.loc[chosen_indices]
    print("Chosen vehicle indices:", chosen_indices)

    return recommended_vehicles[['MAKE', 'MODEL', 'VEHICLE_TYPES']].to_dict('records')

def assign_top_vehicles(vehicle_list_df, owner_make, owner_loyalty_score, is_luxury_owner, presence_of_children, income_key):
    # Initialize weights as 1 for all vehicles
    weights = np.ones(len(vehicle_list_df))

    # Apply a more significant loyalty factor
    # For example, the factor could be proportional to the loyalty score plus a base increase
    loyalty_factor = 2 * owner_loyalty_score + 1
    is_same_make = vehicle_list_df['MAKE'] == owner_make
    weights[is_same_make] *= loyalty_factor

    print(f"Weights after applying loyalty factor ({loyalty_factor}) for {owner_make}:", weights[is_same_make])    # Initialize weights as 1 for all vehicles

    # Double the weight for luxury brands if the owner already owns a luxury brand
    if is_luxury_owner:
        weights[vehicle_list_df['MAKE'].isin(luxury_brands)] *= 2
        print("Weights after doubling for luxury brands:", weights)

    # Increase weight by 1.5x for spacious vehicles if the owner has children
    if presence_of_children == 'Yes':
        spacious_mask = vehicle_list_df[spacious_vehicle_types].any(axis=1)
        weights[spacious_mask] *= 1.5
        print("Weights after 1.5x increase for spacious vehicles:", weights)

    # Map income keys to a numerical scale (1 for A, 2 for B, ..., 18 for R)
    income_scale = {
        "A": 1, "B": 2, "C": 3, "D": 4, "E": 5,
        "F": 6, "G": 7, "H": 8, "I": 9, "J": 10,
        "K": 11, "L": 12, "M": 13, "N": 14, "O": 15,
        "P": 16, "Q": 17, "R": 18
    }
    income_value = income_scale.get(income_key, 1)  # Default to 1 if key not found

    # Incrementally increase weight for luxury vehicles based on income
    luxury_multiplier = 1 + (income_value / len(income_scale))
    luxury_mask = vehicle_list_df['MAKE'].isin(luxury_brands)
    weights[luxury_mask] *= luxury_multiplier

    # Normalize the weights
    weights /= weights.sum()
    
    # Ensure one vehicle of the same make is selected
    same_make_indices = vehicle_list_df[vehicle_list_df['MAKE'] == owner_make].index
    if len(same_make_indices) > 0:
        chosen_index_same_make = np.random.choice(same_make_indices, size=1)
    else:
        # Fallback if no vehicle of the same make is found
        chosen_index_same_make = np.random.choice(vehicle_list_df.index, size=1, p=weights)

    # Select two more vehicles based on weights
    chosen_indices_additional = np.random.choice(vehicle_list_df.index, size=2, replace=False, p=weights)

    # Combine indices and fetch vehicles
    chosen_indices = np.concatenate((chosen_index_same_make, chosen_indices_additional))
    recommended_vehicles = vehicle_list_df.loc[chosen_indices]

    return recommended_vehicles[['MAKE', 'MODEL', 'VEHICLE_TYPES']].to_dict('records')

def fetch_data_and_recommend(conn):
    # Execute a database query to fetch required records
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, PresenceOfChildren, AutoOwnerMake, IncomeKey FROM dis.inventory where AutoOwnerMake = 'NISSAN' limit 5"
    cursor.execute(query)
    
    # Fetch all the records from the executed query
    records = cursor.fetchall()

    # Process each record to generate vehicle recommendations
    for record in records:
        # Convert the make to uppercase for consistency
        owner_make = record['AutoOwnerMake'].upper()

        # Fetch the loyalty score for the owner's make, defaulting to 0 if not found
        loyalty_score = loyalty_scores.get(owner_make, 0)
        
        # Determine if the owner's current make is a luxury brand
        is_luxury_owner = owner_make in luxury_brands

        # Check if the owner has children
        presence_of_children = record['PresenceOfChildren'] == 'Yes'

        # Map the income key to a numerical value
        income_key = income_key_mapping.get(record['IncomeKey'].upper(), 0)

        # Get the top 3 vehicle recommendations based on the owner's profile
        top_vehicles = assign_top_vehicles(vehicle_list_df, owner_make, loyalty_score, is_luxury_owner, presence_of_children, income_key)

        # Print the recommendations for the current profile
        pprint(f"Recommendations for profile {record['id']}:")
        
        # Print the owner's current make
        pprint(f"Current vehicle: {owner_make}")
        
        # Print the owner's loyalty score for the current make
        pprint(f"Loyalty score: {loyalty_score}")
        
        # Print whether the owner is a luxury owner
        pprint(f"Luxury owner: {is_luxury_owner}")
        
        # Print whether the owner has children
        pprint(f"Presence of children: {presence_of_children}")
        
        # Print the owner's income key
        pprint(f"Income key: {income_key}")
        
        
        # Print each recommended vehicle's make, model, and types
        for vehicle in top_vehicles:
            pprint(f"{vehicle['MAKE']} {vehicle['MODEL']} ({vehicle['VEHICLE_TYPES']})")

if __name__ == '__main__':
    local_db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password1',
        'database': 'db'
    }
    work_db_config = {
        'host': "ec2-3-20-141-107.us-east-2.compute.amazonaws.com",
        'user': "kwoods",
        'password': "ybQ7wxusL7sS7qNXBqQL",  # OR "wH@QD%4_VnhWR=eX8#Yq"
        'database': "kwoods"
    }
    conn = mysql.connector.connect(**work_db_config)
    if conn:
        fetch_data_and_recommend(conn)
       
    conn.close()
else:
    print("Failed to establish database connection.")