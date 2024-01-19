# main_2.py
import pandas as pd
import numpy as np
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pandas.io.sql import DatabaseError
import pymysql
import mysql.connector

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
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}")
        raise
    except json.JSONDecodeError:
        logging.error("Invalid JSON format in configuration file.")
        raise


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
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}")
        raise
    except json.JSONDecodeError:
        logging.error("Invalid JSON format in configuration file.")
        raise

def print_fetched_data(dataframe):
    try:
        if dataframe.empty:
            print("No data fetched from the database.")
        else:
            print("Fetched Data:")
            print(dataframe)
    except AttributeError:
        logging.error("Invalid input, expected a Pandas DataFrame.")
        raise
    def print_fetched_data(dataframe):
        try:
            if dataframe.empty:
                print("No data fetched from the database.")
            else:
                print("Fetched Data:")
                print(dataframe)
        except AttributeError:
            logging.error("Invalid input, expected a Pandas DataFrame.")
            raise

# Define other functions like adjust_for_vehicle_type_preference here
# (Add error handling similarly in each function)

def fetch_data_and_recommend(engine, config):
    try:
        vehicle_query = config.get('vehicle_query')
        if not vehicle_query:
            raise ValueError("Vehicle query not found in configuration.")

        vehicle_list_df = pd.read_sql(vehicle_query, engine)
        print_fetched_data(vehicle_list_df)

        weights = pd.DataFrame(index=vehicle_list_df.index)
        weights['weight'] = 1.0

        # Adjust weights based on various criteria and print weights at each step
        weights = adjust_for_luxury_preference(weights, vehicle_list_df, config, config.get("LUXURY_MULTIPLIER", 1.0))
        print("Weights after adjusting for luxury preference:")
        print(weights.head())

        weights = adjust_for_vehicle_type_preference(weights, vehicle_list_df, config, 'SomeAutoOwnerModel')
        print("Weights after adjusting for vehicle type preference:")
        print(weights.head())

        weights = adjust_for_family_friendly(weights, vehicle_list_df, config, True)
        print("Weights after adjusting for family friendly:")
        print(weights.head())

        weights = adjust_for_loyalty(weights, vehicle_list_df, config, 2.0, 'SomeOwnerMake')
        print("Weights after adjusting for loyalty:")
        print(weights.head())

        recommended_vehicles = select_vehicles_based_on_weights(vehicle_list_df, weights['weight'])
        logging.info("Recommended vehicles:")
        print(recommended_vehicles)

    except DatabaseError as e:
        logging.error(f"Database error occurred: {e}")
        raise
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred in fetch_data_and_recommend: {e}")
        raise

def adjust_for_vehicle_type_preference(weights, vehicle_list_df, config, auto_owner_model):
    try:
        if config["VEHICLE_TYPE_COLUMN"] not in vehicle_list_df.columns:
            raise ValueError(f"Column {config['VEHICLE_TYPE_COLUMN']} not found in DataFrame.")

        vehicle_types = get_vehicle_types_based_on_model(auto_owner_model)
        for idx, row in vehicle_list_df.iterrows():
            row_vehicle_types = extract_vehicle_types(row, config["VEHICLE_TYPE_COLUMN"])
            if set(vehicle_types).intersection(set(row_vehicle_types)):
                weights[idx] *= 1.5


    except KeyError as e:
        logging.error(f"Configuration error: {e}")
        raise
    except Exception as e:
        logging.error(f"Error in adjust_for_vehicle_type_preference: {e}")
        raise
def select_vehicles_based_on_weights(vehicle_list_df, weights):
    try:
        normalized_weights = weights / np.sum(weights)
        cumulative_distribution = np.cumsum(normalized_weights)
        chosen_indices = np.searchsorted(cumulative_distribution, np.random.rand(3))
        return vehicle_list_df.iloc[chosen_indices]
    except Exception as e:
        logging.error(f"Error in select_vehicles_based_on_weights: {e}")
        raise
def extract_vehicle_types(row, vehicle_type_columns):
    try:
        vehicle_types = set()
        for col in vehicle_type_columns:
            if pd.isna(row[col]) or row[col] == 0:
                continue
            if isinstance(row[col], str):
                types = row[col].split('|')
                vehicle_types.update(types)
            elif row[col] == 1:
                vehicle_types.add(col)
        return list(vehicle_types)
    except Exception as e:
        logging.error(f"Error in extract_vehicle_types: {e}")
        raise
def get_vehicle_types_based_on_model(auto_owner_model):
    try:
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
    except Exception as e:
        logging.error(f"Error in get_vehicle_types_based_on_model: {e}")
        raise
def adjust_for_family_friendly(weights, vehicle_list_df, config, presence_of_children):
    try:
        if config["FF_VEHICLE_TYPES"] not in vehicle_list_df.columns:
            raise ValueError(f"Column {config['FF_VEHICLE_TYPES']} not found in DataFrame.")

        if presence_of_children:
            family_friendly_mask = vehicle_list_df[config["FF_VEHICLE_TYPES"]] == '1'
            weights[family_friendly_mask] *= 1.2
        return weights
    except KeyError as e:
        logging.error(f"Configuration error: {e}")
        raise
    except Exception as e:
        logging.error(f"Error in adjust_for_family_friendly: {e}")
        raise
def adjust_for_luxury_preference(weights, vehicle_list_df, config, luxury_multiplier):
    try:
        if 'MAKE' not in vehicle_list_df.columns:
            raise ValueError("'MAKE' column not found in DataFrame.")

        luxury_mask = vehicle_list_df['MAKE'].isin(config["LUXURY_BRANDS"])
        luxury_multiplier = float(luxury_multiplier)
        if luxury_multiplier < 0:
            raise ValueError("Luxury multiplier must be greater than or equal to 0.")

        weights[luxury_mask] *= luxury_multiplier
        return weights
    except ValueError as e:
        logging.error(f"Value error: {e}")
        raise
    except Exception as e:
        logging.error(f"Error in adjust_for_luxury_preference: {e}")
        raise
def adjust_for_loyalty(weights, vehicle_list_df, config, loyalty_factor, owner_make):
    try:
        if 'MAKE' not in vehicle_list_df.columns:
            raise ValueError("'MAKE' column not found in DataFrame.")

        same_make_mask = vehicle_list_df['MAKE'].str.upper() == owner_make.upper()
        weights[same_make_mask] *= loyalty_factor
        return weights
    except Exception as e:
        logging.error(f"Error in adjust_for_loyalty: {e}")
        raise
    
def fetch_data_and_recommend(engine, config):
    try:
        # Fetch data from the database
        vehicle_query = config.get('vehicle_query')
        if not vehicle_query:
            raise ValueError("Vehicle query not found in configuration.")

        vehicle_list_df = pd.read_sql(vehicle_query, engine)
        print_fetched_data(vehicle_list_df)

        # Initialize weights
        weights = pd.DataFrame(index=vehicle_list_df.index)
        weights['weight'] = 1.0

        # Apply various adjustments to weights
        # Note: Ensure all these functions are defined and include error handling
        if 'LUXURY_MULTIPLIER' in config and 'LUXURY_BRANDS' in config:
            luxury_multiplier = config['LUXURY_MULTIPLIER']
            weights = adjust_for_luxury_preference(weights, vehicle_list_df, config, luxury_multiplier)
        # Include other weight adjustments here, such as for vehicle type preference, family-friendliness, and loyalty

        # Make recommendations based on weights
        recommended_vehicles = select_vehicles_based_on_weights(vehicle_list_df, weights['weight'])
        logging.info(f"Recommended vehicles: {recommended_vehicles}")

    except DatabaseError as e:
        logging.error(f"Database error occurred: {e}")
        raise
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred in fetch_data_and_recommend: {e}")
        raise

def main():
    setup_logging()
    try:
        config = load_config()

        logging.debug("Connecting to database...")
        db_connection = config.get('db_connection')
        if db_connection is None:
            raise ValueError("Database connection settings not found in configuration.")

        engine = create_engine(f"mysql+mysqldb://{db_connection['user']}:{db_connection['password']}@{db_connection['host']}/{db_connection['database']}", pool_size=10, max_overflow=20)

        try:
            fetch_data_and_recommend(engine, config)
        finally:
            engine.dispose()
            logging.debug("Database connection closed.")
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")

if __name__ == '__main__':
    main()