

def load_config(config_path='config.json', vehicle_type_json_path='path_to_json_file'):
    # Load the configuration file
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        logging.info("Configuration file loaded successfully.")
        
        # Load the vehicle type data from JSON
        with open(vehicle_type_json_path, 'r') as json_file:
            vehicle_type_data = json.load(json_file)
        config['vehicle_type_data'] = vehicle_type_data
        logging.info("Vehicle type data loaded successfully.")

        return config
    except FileNotFoundError:
        logging.error("Configuration file not found.")
        raise
    except json.JSONDecodeError:
        logging.error("Configuration file contains invalid JSON.")
        raise
    except Exception as e:
        logging.error(f"An error occurred while loading the configuration file: {e}")
        raise
