import pandas as pd
import numpy as np
import mysql.connector
from pprint import pprint
import os
import json

# Load the configuration file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Accessing configurations
DB_CONFIG = config["DB_CONFIG"]
LOYALTY_SCORES = config["LOYALTY_SCORES"]
LUXURY_BRANDS = config["LUXURY_BRANDS"]
FF_VEHICLE_TYPES = config["FF_VEHICLE_TYPES"]
INCOME_KEY_MAPPING = config["INCOME_KEY_MAPPING"]


def load_vehicle_data(filepath):
    """
    Load vehicle data from a CSV file into a Pandas DataFrame.
    """
    try:
        vehicle_list_df = pd.read_csv(filepath)
        return vehicle_list_df
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        return None

def setup_database_connection(config):
    """
    Set up a database connection using provided configuration.
    """
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            return conn
        else:
            print("Failed to establish database connection.")
            return None
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None
    
def adjust_for_vehicle_type_preference(weights, vehicle_list_df, vehicle_types): # type: ignore
    # Assuming vehicle_list_df['VEHICLE_TYPES'] contains a string of concatenated types
    for v_type in vehicle_types:
        mask = vehicle_list_df['VEHICLE_TYPES'].str.contains(v_type)
        weights[mask] *= 1.5
    return weights

    def adjust_for_vehicle_type_preference(weights, vehicle_list_df, vehicle_types):
        """
        Adjust weights for current vehicle type preference.
        """
        for idx, row in vehicle_list_df.iterrows():
            if any(v_type in vehicle_types for v_type in row['VEHICLE_TYPES']):
                weights[idx] *= 1.5
        return weights

def adjust_for_luxury_preference(weights, vehicle_list_df, luxury_multiplier, luxury_brands):
    """
    Adjust weights for luxury preference based on income.
    
    :param weights: Numpy array of weights for each vehicle.
    :param vehicle_list_df: DataFrame containing vehicle data.
    :param luxury_multiplier: Multiplier to adjust weights for luxury vehicles.
    :param luxury_brands: List of luxury vehicle brands.
    :return: Updated weights.
    """
    luxury_mask = vehicle_list_df['MAKE'].isin(luxury_brands)
    weights[luxury_mask] *= luxury_multiplier
    return weights
def adjust_for_loyalty(weights, vehicle_list_df, loyalty_factor, owner_make):
    """
    Apply loyalty factor to the current vehicle's make.
    
    :param weights: Numpy array of weights for each vehicle.
    :param vehicle_list_df: DataFrame containing vehicle data.
    :param loyalty_factor: Factor by which to increase weight for the owner's current make.
    :param owner_make: The make of the owner's current vehicle.
    :return: Updated weights.
    """
    if owner_make in vehicle_list_df['MAKE'].unique():
        same_make_mask = vehicle_list_df['MAKE'] == owner_make
        weights[same_make_mask] *= loyalty_factor
    return weights
def assign_top_vehicles(vehicle_list_df, owner_vehicle_info, presence_of_children, income_key):
    """
    Determine the top vehicle recommendations based on various preferences and factors.
    
    :param vehicle_list_df: DataFrame containing vehicle data.
    :param owner_vehicle_info: Dictionary containing the owner's current vehicle make and types.
    :param presence_of_children: Boolean indicating if the owner has children.
    :param income_key: Income level key of the vehicle owner.
    :return: Dictionary of recommended vehicles.
    """
    owner_make = owner_vehicle_info['MAKE'].upper()
    current_vehicle_types = owner_vehicle_info['VEHICLE_TYPES']  # List of current vehicle types

    loyalty_score = LOYALTY_SCORES.get(owner_make, 0)
    loyalty_factor = 2 * loyalty_score + 1
    income_value = INCOME_KEY_MAPPING.get(income_key, 1) # Default to 1 if key not found



    def adjust_for_family_friendly(weights, vehicle_list_df, presence_of_children, family_friendly_vehicle_types):
        """
        Adjust weights for family-friendly preference based on the presence of children.
        """
        if presence_of_children:
            family_friendly_mask = vehicle_list_df['VEHICLE_TYPES'].isin(family_friendly_vehicle_types)
            weights[family_friendly_mask] *= 1.2
        return weights

    luxury_multiplier = 1 + (income_value / 18)  # Adjusted for 18 income levels

    # Initialize weights
    weights = np.ones(len(vehicle_list_df))

    # Adjust weights based on various factors
    weights = adjust_for_vehicle_type_preference(weights, vehicle_list_df, current_vehicle_types)
    weights = adjust_for_family_friendly(weights, vehicle_list_df, presence_of_children, FF_VEHICLE_TYPES)
    weights = adjust_for_luxury_preference(weights, vehicle_list_df, luxury_multiplier, LUXURY_BRANDS)
    weights = adjust_for_loyalty(weights, vehicle_list_df, loyalty_factor, owner_make)

    # Normalize the weights
    weights /= weights.sum()

    # Vehicle selection logic
    chosen_indices = select_vehicles_based_on_weights(vehicle_list_df, weights, owner_make)

    # Fetch and return recommended vehicles
    recommended_vehicles = vehicle_list_df.loc[chosen_indices]
    return recommended_vehicles[['MAKE', 'MODEL', 'VEHICLE_TYPES']].to_dict('records')


def select_vehicles_based_on_weights(vehicle_list_df, weights, owner_make):
    chosen_indices = []

    # Normalize the weights
    normalized_weights = weights / weights.sum()

    # Select a vehicle of the same make if available
    same_make_indices = vehicle_list_df[vehicle_list_df['MAKE'] == owner_make].index
    if len(same_make_indices) > 0:
        chosen_index_same_make = np.random.choice(same_make_indices, size=1, p=normalized_weights[same_make_indices])
        chosen_indices.append(chosen_index_same_make[0])

    # Exclude already chosen vehicles and re-normalize weights
    remaining_weights = np.delete(normalized_weights, chosen_indices)
    remaining_weights /= remaining_weights.sum()

    # Select two more vehicles based on updated weights
    remaining_indices = [i for i in vehicle_list_df.index if i not in chosen_indices]
    if len(remaining_indices) > 2:
        chosen_indices_additional = np.random.choice(remaining_indices, size=2, replace=False, p=remaining_weights)
        chosen_indices.extend(chosen_indices_additional)

    return chosen_indices


    def adjust_weights_for_preferences(vehicle_list_df, current_vehicle_types, has_children, luxury_multiplier, loyalty_factor, owner_make):
            weights = np.ones(len(vehicle_list_df))

            # Adjust for current vehicle type preference
            for vehicle_type in current_vehicle_types:
                type_mask = vehicle_list_df[vehicle_type] == 1
                weights[type_mask] *= 1.5  # Increase the weight for preferred types
                print(f"Weights after adjusting for vehicle type {vehicle_type} preference:", weights[type_mask][:10])  # Print first 10 for brevity

            # Adjust for presence of children
            if has_children:
                family_friendly_types = ['SUV', 'MINIVAN', 'LARGE_CAR']  # Define family-friendly vehicle types
                for ff_type in family_friendly_types:
                    family_friendly_mask = vehicle_list_df[ff_type] == 1
                    weights[family_friendly_mask] *= 1.2  # Slightly increase the weight for family-friendly vehicles
                    print(f"Weights after adjusting for family-friendly type {ff_type}:", weights[family_friendly_mask][:10])

            # Adjust for luxury preference based on income
            luxury_mask = vehicle_list_df['MAKE'].isin(LUXURY_BRANDS)
            weights[luxury_mask] *= luxury_multiplier
            print("Weights after adjusting for luxury preference:", weights[luxury_mask][:10])

            # Apply loyalty factor to the current vehicle's make
            same_make_mask = vehicle_list_df['MAKE'] == owner_make
            weights[same_make_mask] *= loyalty_factor
            print(f"Weights after applying loyalty factor for {owner_make}:", weights[same_make_mask][:10])

            return weights

    def extract_vehicle_types(vehicle_list_df):
        vehicle_types_columns = [col for col in vehicle_list_df.columns if col not in ['MAKE', 'MODEL']]
        vehicle_list_df['VEHICLE_TYPES'] = vehicle_list_df[vehicle_types_columns].apply(
            lambda x: '|'.join(x.index[x.astype(bool)]), axis=1
        )
        return vehicle_list_df

    def fetch_data_and_recommend(conn):
        cursor = conn.cursor(dictionary=True)
        query = ("SELECT id, PresenceOfChildren, AutoOwnerMake, AutoOwnerModel, IncomeKey "
                "FROM dis.inventory where AutoOwnerMake = 'FORD' limit 1 ")
        cursor.execute(query)
        records = cursor.fetchall()

    # Rest of your code...
        cursor = conn.cursor(dictionary=True)
        query = ("SELECT id, PresenceOfChildren, AutoOwnerMake, AutoOwnerModel, IncomeKey "
                "FROM dis.inventory where AutoOwnerMake = 'FORD' limit 1 ")
        cursor.execute(query)
        records = cursor.fetchall()

        for record in records:
            owner_make = record['AutoOwnerMake'].upper()
            loyalty_score = LOYALTY_SCORES.get(owner_make, 0)
            is_luxury_owner = owner_make in LUXURY_BRANDS
            presence_of_children = record['PresenceOfChildren'] == 'Yes'
            income_key = INCOME_KEY_MAPPING.get(record['IncomeKey'].upper(), 0)

            # Load the master vehicle list into a Pandas DataFrame
            vehicle_list_df = pd.read_csv('x_unique_cars_final_types_x_3.csv')

            # Extracting vehicle types columns
            vehicle_list_df = extract_vehicle_types(vehicle_list_df)

            top_vehicles = assign_top_vehicles(vehicle_list_df, owner_make, presence_of_children, income_key)

            pprint(f"Recommendations for profile {record['id']}:")
            pprint(f"Owner Make: {owner_make}")
            pprint(f"Loyalty Score: {loyalty_score}")
            pprint(f"Is Luxury Owner: {is_luxury_owner}")
            pprint(f"Presence of Children: {presence_of_children}")
            pprint(f"Income Key: {income_key}")
            pprint("Make, Model (Vehicle Types):")

            for vehicle in top_vehicles:
                print("Vehicle data:", vehicle)
                vehicle_type = vehicle.get('VEHICLE_TYPES', 'Unknown Type')
                pprint(f"{vehicle['MAKE']} {vehicle['MODEL']} ({vehicle_type})")

        cursor.close()

def main():
        # Load vehicle data
        vehicle_list_df = load_vehicle_data('x_unique_cars_final_types_x_3.csv')
        if vehicle_list_df is not None:
            vehicle_list_df = extract_vehicle_types(vehicle_list_df)

        # Database connection setup
        db_config = {
            'host': "ec2-3-20-141-107.us-east-2.compute.amazonaws.com",
            'user': "kwoods",
            'password': "ybQ7wxusL7sS7qNXBqQL",
            'database': "kwoods"
        }
        conn = setup_database_connection(db_config)
        if conn:
            fetch_data_and_recommend(conn)
            conn.close()
        else:
            print("Failed to establish database connection.")

if __name__ == '__main__':
    main()
"""_summary_ = """