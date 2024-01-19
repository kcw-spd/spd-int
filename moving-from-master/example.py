import pandas as pd
import numpy as np
import json
from pprint import pprint
import logging
from sqlalchemy import create_engine

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the configuration file
try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    logging.info("Configuration file loaded successfully.")

    # Accessing configurations
    LOYALTY_SCORES = config["LOYALTY_SCORES"]
    LUXURY_BRANDS = config["LUXURY_BRANDS"]
    FF_VEHICLE_TYPES = config["FF_VEHICLE_TYPES"]
    INCOME_KEY_MAPPING = config["INCOME_KEY_MAPPING"]
    DB_CONFIG = config["DB_CONFIG"]

except FileNotFoundError:
    logging.error("Configuration file not found.")
    raise
except json.JSONDecodeError:
    logging.error("Error decoding JSON from the configuration file.")
    raise
except KeyError as e:
    logging.error(f"Missing key in configuration file: {e}")
    raise

# Function to setup database connection
def setup_database_connection(config):
    try:
#        database_url = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
        # this engine can handle up to 30 connections
        engine = create_engine("mysql+pymysql://kwoods:ybQ7wxusL7sS7qNXBqQL@ec2-3-20-141-107.us-east-2.compute.amazonaws.com/kwoods", pool_size=10, max_overflow=20)
        logging.info("Database engine created successfully.")
        return engine
    except Exception as e:
        logging.error(f"Database engine creation error: {e}")
        return None

# Function to load vehicle data
def load_vehicle_data(engine):
    try:
        # vehicle_columns = ', '.join(DB_COLUMNS["vehicle_data_columns"])
        query = "SELECT * from FROM mods.master_vehicle_types"
        vehicle_list_df = pd.read_sql(query, engine)
        vehicle_list_df.replace('', np.nan, inplace=True)

        if vehicle_list_df.isnull().any().any():
            logging.warning("Null values found in the vehicle data.")

        return vehicle_list_df

    except Exception as e:
        logging.error(f"Error loading vehicle data: {e}")
        return None

# Optimized function for selecting vehicles based on weights
def select_vehicles_based_on_weights(vehicle_list_df, weights):
    normalized_weights = weights / np.sum(weights)
    cumulative_distribution = np.cumsum(normalized_weights)
    chosen_indices = np.searchsorted(cumulative_distribution, np.random.rand(3))
    return vehicle_list_df.iloc[chosen_indices]

# Main function for fetching data and recommending vehicles
def fetch_data_and_recommend(engine):
    try:
        vehicle_list_df = load_vehicle_data(engine)
        if vehicle_list_df is None:
            logging.error("Failed to load vehicle data.")
            return

        # Fetch and process inventory data
        with engine.connect() as conn:
            # inventory_columns = ', '.join(DB_COLUMNS["inventory_columns"])
            
            query = "SELECT * from inventory_table limit 1 FROM dis.inventory LIMIT 100"
            result = conn.execute(query)
            records = result.fetchall()

            if not records:
                logging.info("No records found.")
                return

            for record in records:
                # Implement logic for weight adjustments based on record data
                # Example: weights calculation
                weights = np.ones(len(vehicle_list_df))
                
                # Select vehicles based on weights
                chosen_indices = select_vehicles_based_on_weights(vehicle_list_df, weights)

                # Fetch and return recommended vehicles
                recommended_vehicles = vehicle_list_df.loc[chosen_indices]
                pprint(f"Recommendations for profile {record['id']}:")
                pprint(recommended_vehicles[['MAKE', 'MODEL', 'VEHICLE_TYPES']].to_dict('records'))

    except Exception as e:
        logging.error(f"Error in fetch_data_and_recommend: {e}")

# Main execution block
def main():
    logging.debug("Starting main function.")
    db_config = # Database connection details here
    engine = setup_database_connection(db_config)
    if engine:
        fetch_data_and_recommend(engine)
    else:
        logging.error("Failed to establish database connection.")

if __name__ == '__main__':
    main()
