import pandas as pd
import numpy as np
import json
import logging
from sqlalchemy import create_engine
import pymysql


def setup_logging():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(config_path='config.json'):
    # Load the configuration file
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            logging.info("Configuration file loaded successfully.")
            return config
        
    except Exception as e:
        logging.error(f"An error occurred while loading the configuration file: {e}")
        raise


def adjust_for_vehicle_type_preference(weights, vehicle_list_df, config, auto_owner_model):
    if config["VEHICLE_TYPE_COLUMN"] in vehicle_list_df.columns:
        vehicle_types = get_vehicle_types_based_on_model(auto_owner_model)
        for idx, row in vehicle_list_df.iterrows():
            row_vehicle_types = extract_vehicle_types(row, config["VEHICLE_TYPE_COLUMN"])  # Fix: Pass the correct argument
            # Check if there's an overlap between the user's preferred vehicle types and the row's vehicle types
            if set(vehicle_types).intersection(set(row_vehicle_types)):
                weights[idx] *= 1.5
    else:
        print(f"Column {config['VEHICLE_TYPE_COLUMN']} not found in DataFrame.")
        # handle the error

# Optimized function for selecting vehicles based on weights
def select_vehicles_based_on_weights(vehicle_list_df, weights):
    normalized_weights = weights / np.sum(weights)
    cumulative_distribution = np.cumsum(normalized_weights)
    chosen_indices = np.searchsorted(cumulative_distribution, np.random.rand(3))
    return vehicle_list_df.iloc[chosen_indices]


def fetch_data_and_recommend(engine, config):
    # Fetch data
    vehicle_list_df = pd.read_sql(config, engine)
    # inventory_df = pd.read_sql(engine, config)

    # Initialize weights
    weights = pd.DataFrame(index=vehicle_list_df.index)
    weights['weight'] = 1.0

    # Adjust weights
    luxury_multiplier = config.get("LUXURY_MULTIPLIER", 1.0)
    weights = adjust_for_luxury_preference(weights, vehicle_list_df, config, luxury_multiplier)

    logging.debug("Fetching vehicle data from MySQL table.")
    query = "SELECT * FROM mods.master_vehicle_types"
    vehicle_list_df = pd.read_sql(query, engine)
    vehicle_list_df.replace('', np.nan, inplace=True)

    if vehicle_list_df.isnull().any().any():
        logging.warning("Null values found in the vehicle data.")

        logging.info("Vehicle data fetched and checked for sanity.")
        
        # Continue with the rest of the function...
        return vehicle_list_df

        

def adjust_for_family_friendly(weights, vehicle_list_df, config, presence_of_children):
    if presence_of_children:
        family_friendly_mask = vehicle_list_df[config["FF_VEHICLE_TYPES"]] == '1'
        weights[family_friendly_mask] *= 1.2
    return weights

def adjust_for_luxury_preference(weights, vehicle_list_df, config, luxury_multiplier):
    if weights is None:
        logging.error("Weights is None.")
        raise ValueError("Weights is None.")
    luxury_mask = vehicle_list_df['MAKE'].isin(config["LUXURY_BRANDS"])
    try:
        luxury_multiplier = float(luxury_multiplier)
        if luxury_multiplier < 0:
            raise ValueError("Luxury multiplier must be greater than or equal to 0.")
        weights[luxury_mask] *= luxury_multiplier
    except ValueError:
        logging.error("Luxury multiplier must be a number.")
        raise
    return weights

def adjust_for_loyalty(weights, vehicle_list_df, config, loyalty_factor, owner_make):
    same_make_mask = vehicle_list_df['MAKE'].str.upper() == owner_make.upper()
    weights[same_make_mask] *= loyalty_factor
    return weights

def extract_vehicle_types(row, vehicle_type_columns):
    vehicle_types = set()
    for col in vehicle_type_columns:
        if pd.isna(row[col]) or row[col] == 0:
            continue
        if isinstance(row[col], str):
            # Assuming the string contains pipe-delimited vehicle types
            types = row[col].split('|')
            vehicle_types.update(types)
        elif row[col] == 1:
            # Binary column, the column name is the vehicle type
            vehicle_types.add(col)
    return list(vehicle_types)

# Define get_vehicle_types_based_on_model() here
def get_vehicle_types_based_on_model(auto_owner_model):
    if auto_owner_model == 'Sedan':
        return ['Sedan', 'Coupe', 'Hatchback']
    elif auto_owner_model == 'SUV':
        return ['SUV', 'Crossover']
    elif auto_owner_model == 'Truck':
        return ['Truck']
    elif auto_owner_model == 'Van':
        return ['Van']
    else:
        return []
    # use the json file to get the db user info
    # Remove the redundant function definition
    # def fetch_data_and_recommend(engine, config):
        # Fetch data
    vehicle_list_df = pd.read_sql(config, engine)
    
    # Initialize weights
    weights = pd.DataFrame(index=vehicle_list_df.index)
    weights['weight'] = 1.0

    # Adjust weights
    luxury_multiplier = config.get("LUXURY_MULTIPLIER", 1.0)
    weights = adjust_for_luxury_preference(weights, vehicle_list_df, config, luxury_multiplier)

    # Continue with the rest of the function...
    logging.debug("Fetching inventory data from MySQL table.")
    inventory_df = pd.read_sql("SELECT * FROM dis.inventory LIMIT 10", engine)

    if inventory_df.empty:
        logging.info("No records found.")
        return

    for _, record in inventory_df.iterrows():
        owner_make = record['AutoOwnerMake'].upper()
        loyalty_score = config["LOYALTY_SCORES"].get(owner_make, 0)
        loyalty_factor = 2 * loyalty_score + 1
        presence_of_children = record['PresenceOfChildren'] == 'Yes'
        income_key = config["INCOME_KEY_MAPPING"].get(record['IncomeKey'].upper(), 0)
        luxury_multiplier = 1 + (income_key / 18)  # Adjusted for 18 income levels

        weights = np.ones(len(vehicle_list_df))
        weights = adjust_for_vehicle_type_preference(weights, vehicle_list_df, config, record['AutoOwnerModel'])
        weights = adjust_for_family_friendly(weights, vehicle_list_df, config, presence_of_children)
        weights = adjust_for_luxury_preference(weights, vehicle_list_df, config, luxury_multiplier)
        weights = adjust_for_loyalty(weights, vehicle_list_df, config, loyalty_factor, owner_make)

        chosen_indices = select_vehicles_based_on_weights(vehicle_list_df, weights)
        recommended_vehicles = vehicle_list_df.loc[chosen_indices]

        logging.info(f"Recommendations for profile {record['id']}: {recommended_vehicles[['MAKE', 'MODEL']].to_dict('records')}")


def main():
    setup_logging()
    config = load_config()
    # load the DB_URI from the config file
    logging.debug("Connecting to database...")

    # load db uri
    # establish a default connection to the database
    db_connection = {
    "host": "ec2-3-20-141-107.us-east-2.compute.amazonaws.com",
    "user": "kwoods",
    "password": "ybQ7wxusL7sS7qNXBqQL",
    "database": "mods"
    }
    # create the engine
    engine = create_engine("mysql+mysqldb://{user}:{password}@{host}/{database}".format(**db_connection), pool_size=10, max_overflow=20)

    logging.debug("Database connection created.")

    try:
        fetch_data_and_recommend(engine, config)
    finally:
        engine.dispose()  # Properly close the database connection
        logging.debug("Database connection closed.")


if __name__ == '__main__':
    main()