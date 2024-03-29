import pandas as pd
import numpy as np
import mysql.connector
from pprint import pprint
import os
import json
from sqlalchemy import create_engine
import pymysql


# Load the configuration file
try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("Error: File not found - config.json")
    config = None

# Accessing configurations
DB_CONFIG = config["DB_CONFIG"]
LOYALTY_SCORES = config["LOYALTY_SCORES"]
LUXURY_BRANDS = config["LUXURY_BRANDS"]
FF_VEHICLE_TYPES = config["FF_VEHICLE_TYPES"]
INCOME_KEY_MAPPING = config["INCOME_KEY_MAPPING"]

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
"""
Locally weighted linear regression, also called local regression, is a type of
non-parametric linear regression that prioritizes data closest to a given
prediction point. The algorithm estimates the vector of model coefficients β
using weighted least squares regression:

β = (XᵀWX)⁻¹(XᵀWy),

where X is the design matrix, y is the response vector, and W is the diagonal
weight matrix.

This implementation calculates wᵢ, the weight of the ith training sample, using
the Gaussian weight:

wᵢ = exp(-‖xᵢ - x‖²/(2τ²)),

where xᵢ is the ith training sample, x is the prediction point, τ is the
"bandwidth", and ‖x‖ is the Euclidean norm (also called the 2-norm or the L²
norm). The bandwidth τ controls how quickly the weight of a training sample
decreases as its distance from the prediction point increases. One can think of
the Gaussian weight as a bell curve centered around the prediction point: a
training sample is weighted lower if it's farther from the center, and τ
controls the spread of the bell curve.

Other types of locally weighted regression such as locally estimated scatterplot
smoothing (LOESS) typically use different weight functions.

References:
    - https://en.wikipedia.org/wiki/Local_regression
    - https://en.wikipedia.org/wiki/Weighted_least_squares
    - https://cs229.stanford.edu/notes2022fall/main_notes.pdf
"""

import matplotlib.pyplot as plt
import numpy as np


def weight_matrix(point: np.ndarray, x_train: np.ndarray, tau: float) -> np.ndarray:
    """
    Calculate the weight of every point in the training data around a given
    prediction point

    Args:
        point: x-value at which the prediction is being made
        x_train: ndarray of x-values for training
        tau: bandwidth value, controls how quickly the weight of training values
            decreases as the distance from the prediction point increases

    Returns:
        m x m weight matrix around the prediction point, where m is the size of
        the training set
    >>> weight_matrix(
    ...     np.array([1., 1.]),
    ...     np.array([[16.99, 10.34], [21.01,23.68], [24.59,25.69]]),
    ...     0.6
    ... )
    array([[1.43807972e-207, 0.00000000e+000, 0.00000000e+000],
           [0.00000000e+000, 0.00000000e+000, 0.00000000e+000],
           [0.00000000e+000, 0.00000000e+000, 0.00000000e+000]])
    """
    m = len(x_train)  # Number of training samples
    weights = np.eye(m)  # Initialize weights as identity matrix
    for j in range(m):
        diff = point - x_train[j]
        weights[j, j] = np.exp(diff @ diff.T / (-2.0 * tau**2))

    return weights


def local_weight(
    point: np.ndarray, x_train: np.ndarray, y_train: np.ndarray, tau: float
) -> np.ndarray:
    """
    Calculate the local weights at a given prediction point using the weight
    matrix for that point

    Args:
        point: x-value at which the prediction is being made
        x_train: ndarray of x-values for training
        y_train: ndarray of y-values for training
        tau: bandwidth value, controls how quickly the weight of training values
            decreases as the distance from the prediction point increases
    Returns:
        ndarray of local weights
    >>> local_weight(
    ...     np.array([1., 1.]),
    ...     np.array([[16.99, 10.34], [21.01,23.68], [24.59,25.69]]),
    ...     np.array([[1.01, 1.66, 3.5]]),
    ...     0.6
    ... )
    array([[0.00873174],
           [0.08272556]])
    """
    weight_mat = weight_matrix(point, x_train, tau)
    weight = np.linalg.inv(x_train.T @ weight_mat @ x_train) @ (
        x_train.T @ weight_mat @ y_train.T
    )

    return weight


def local_weight_regression(
    x_train: np.ndarray, y_train: np.ndarray, tau: float
) -> np.ndarray:
    """
    Calculate predictions for each point in the training data

    Args:
        x_train: ndarray of x-values for training
        y_train: ndarray of y-values for training
        tau: bandwidth value, controls how quickly the weight of training values
            decreases as the distance from the prediction point increases

    Returns:
        ndarray of predictions
    >>> local_weight_regression(
    ...     np.array([[16.99, 10.34], [21.01, 23.68], [24.59, 25.69]]),
    ...     np.array([[1.01, 1.66, 3.5]]),
    ...     0.6
    ... )
    array([1.07173261, 1.65970737, 3.50160179])
    """
    y_pred = np.zeros(len(x_train))  # Initialize array of predictions
    for i, item in enumerate(x_train):
        y_pred[i] = np.dot(item, local_weight(item, x_train, y_train, tau)).item()

    return y_pred


def load_data(
    dataset_name: str, x_name: str, y_name: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load data from seaborn and split it into x and y points
    >>> pass    # No doctests, function is for demo purposes only
    """
    import seaborn as sns

    data = sns.load_dataset(dataset_name)
    x_data = np.array(data[x_name])
    y_data = np.array(data[y_name])

    one = np.ones(len(y_data))

    # pairing elements of one and x_data
    x_train = np.column_stack((one, x_data))

    return x_train, x_data, y_data


def plot_preds(
    x_train: np.ndarray,
    preds: np.ndarray,
    x_data: np.ndarray,
    y_data: np.ndarray,
    x_name: str,
    y_name: str,
) -> None:
    """
    Plot predictions and display the graph
    >>> pass    # No doctests, function is for demo purposes only
    """
    x_train_sorted = np.sort(x_train, axis=0)
    plt.scatter(x_data, y_data, color="blue")
    plt.plot(
        x_train_sorted[:, 1],
        preds[x_train[:, 1].argsort(0)],
        color="yellow",
        linewidth=5,
    )
    plt.title("Local Weighted Regression")
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.show()


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
    
def adjust_for_vehicle_type_preference(weights, vehicle_list_df, config, auto_owner_model):
    vehicle_type_columns = config["VEHICLE_TYPE_COLUMN"]
    if not all(col in vehicle_list_df.columns for col in vehicle_type_columns):
        raise ValueError("One or more vehicle type columns are not found in DataFrame.")

    vehicle_types = get_vehicle_types_based_on_model(auto_owner_model)
    for idx, row in vehicle_list_df.iterrows():
        row_vehicle_types = extract_vehicle_types(row, vehicle_type_columns)
        if set(vehicle_types).intersection(set(row_vehicle_types)):
            weights.loc[idx, 'weight'] *= 1.5

def adjust_for_family_friendly(weights, vehicle_list_df, has_children, family_friendly_types):
    """
    Adjust weights for family-friendly vehicle types if the owner has children.
    
    :param weights: Numpy array of weights for each vehicle.
    :param vehicle_list_df: DataFrame containing vehicle data.
    :param has_children: Boolean indicating if the owner has children.
    :param family_friendly_types: List of family-friendly vehicle types.
    :return: Updated weights.
    """
    if has_children:
        for ff_type in family_friendly_types:
            if ff_type in FF_VEHICLE_TYPES and ff_type in vehicle_list_df.columns:
                family_friendly_mask = vehicle_list_df[ff_type] == 1
                weights[family_friendly_mask] *= 1.2
    return weights


def adjust_for_vehicle_type_preference(weights, vehicle_list_df, config, auto_owner_model):
    vehicle_type_columns = config["VEHICLE_TYPE_COLUMN"]
    if not all(col in vehicle_list_df.columns for col in vehicle_type_columns):
        raise ValueError("One or more vehicle type columns are not found in DataFrame.")

    vehicle_types = get_vehicle_types_based_on_model(auto_owner_model)
    for idx, row in vehicle_list_df.iterrows():
        row_vehicle_types = extract_vehicle_types(row, vehicle_type_columns)
        if set(vehicle_types).intersection(set(row_vehicle_types)):
            weights.loc[idx, 'weight'] *= 1.5

    def adjust_for_family_friendly(weights, vehicle_list_df, config, presence_of_children):
        if presence_of_children:
            # Aligning indices of weights and vehicle_list_df
            aligned_weights = weights.reindex(vehicle_list_df.index)
            family_friendly_mask = vehicle_list_df[config["FF_VEHICLE_TYPES"]].eq(1).any(axis=1)
            aligned_weights.loc[family_friendly_mask, 'weight'] *= 1.2
            return aligned_weights.fillna(1.0)  # Filling NaN values with 1.0 (default weight)
        return weights

    def adjust_for_family_friendly(weights, vehicle_list_df, has_children, family_friendly_types):
        """
        Adjust weights for family-friendly vehicle types if the owner has children.
        
        :param weights: Numpy array of weights for each vehicle.
        :param vehicle_list_df: DataFrame containing vehicle data.
        :param has_children: Boolean indicating if the owner has children.
        :param family_friendly_types: List of family-friendly vehicle types.
        :return: Updated weights.
        """
        if has_children:
            for ff_type in family_friendly_types:
                if ff_type in FF_VEHICLE_TYPES and ff_type in vehicle_list_df.columns:
                    family_friendly_mask = vehicle_list_df[ff_type] == 1
                    weights[family_friendly_mask] *= 1.2
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
        import numpy as np
        import pandas as pd
        from pprint import pprint

        # Constants
        LOYALTY_SCORES = {'FORD': 0}  # Example loyalty scores
        LUXURY_BRANDS = ['BMW', 'Mercedes-Benz']  # Example luxury brands
        INCOME_KEY_MAPPING = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}  # Example income key mapping
        FF_VEHICLE_TYPES = ['SUV', 'MINIVAN', 'LARGE_CAR']  # Example family-friendly vehicle types

        def adjust_for_vehicle_type_preference(weights, vehicle_list_df, vehicle_types):
            """
            Adjust weights for current vehicle type preference.
            """
            for row in vehicle_list_df.itertuples():
                if any(v_type in vehicle_types for v_type in row.VEHICLE_TYPES):
                    weights[row.Index] *= 1.5
            return weights

        def adjust_for_family_friendly(weights, vehicle_list_df, presence_of_children, family_friendly_types):
            """
            Adjust weights for family-friendly vehicle types.
            """
            if presence_of_children:
                for ff_type in family_friendly_types:
                    family_friendly_mask = vehicle_list_df[ff_type] == 1
                    weights[family_friendly_mask] *= 1.2
            return weights

        def adjust_for_luxury_preference(weights, vehicle_list_df, luxury_multiplier, luxury_brands):
            """
            Adjust weights for luxury vehicle preference based on income.
            """
            luxury_mask = vehicle_list_df['MAKE'].isin(luxury_brands)
            weights[luxury_mask] *= luxury_multiplier
            return weights

        def adjust_for_loyalty(weights, vehicle_list_df, loyalty_factor, owner_make):
            """
            Apply loyalty factor to the current vehicle's make.
            """
            if owner_make in vehicle_list_df['MAKE'].unique():
                same_make_mask = vehicle_list_df['MAKE'] == owner_make
                weights[same_make_mask] *= loyalty_factor
            return weights

        def assign_top_vehicles(vehicle_list_df, owner_vehicle_info, presence_of_children, income_key):
            """
            Determine the top vehicle recommendations based on various preferences and factors.
            """
            owner_make = owner_vehicle_info['MAKE'].upper()
            current_vehicle_types = owner_vehicle_info['VEHICLE_TYPES']

            loyalty_score = LOYALTY_SCORES.get(owner_make, 0)
            loyalty_factor = 2 * loyalty_score + 1
            income_value = INCOME_KEY_MAPPING.get(income_key, 1)
            luxury_multiplier = 1 + (income_value / 18)

            weights = np.ones(len(vehicle_list_df))

            weights = adjust_for_vehicle_type_preference(weights, vehicle_list_df, current_vehicle_types)
            weights = adjust_for_family_friendly(weights, vehicle_list_df, presence_of_children, FF_VEHICLE_TYPES)
            weights = adjust_for_luxury_preference(weights, vehicle_list_df, luxury_multiplier, LUXURY_BRANDS)
            weights = adjust_for_loyalty(weights, vehicle_list_df, loyalty_factor, owner_make)

            weights /= weights.sum()

            chosen_indices = select_vehicles_based_on_weights(vehicle_list_df, weights, owner_make)

            recommended_vehicles = vehicle_list_df.loc[chosen_indices]
            return recommended_vehicles[['MAKE', 'MODEL', 'VEHICLE_TYPES']].to_dict('records')

        def select_vehicles_based_on_weights(vehicle_list_df, weights, owner_make):
            """
            Select vehicles based on calculated weights.
            """
            chosen_indices = []

            if weights.size > 0 and weights.sum() > 0:
                weights /= weights.sum()

                same_make_indices = vehicle_list_df[vehicle_list_df['MAKE'] == owner_make].index
                if same_make_indices.size > 0:
                    chosen_index_same_make = np.random.choice(same_make_indices, size=1)
                    chosen_indices.append(chosen_index_same_make[0])

                weights[chosen_indices] = 0
                weights /= weights.sum()

                if weights.sum() > 0:
                    chosen_indices_additional = np.random.choice(vehicle_list_df.index, size=2, replace=False, p=weights)
                    chosen_indices.extend(chosen_indices_additional)

            return chosen_indices

        def load_vehicle_data(file_path):
            """
            Load vehicle data from a CSV file.
            """
            try:
                vehicle_list_df = pd.read_csv(file_path)
                return vehicle_list_df
            except FileNotFoundError:
                print(f"File not found: {file_path}")
                return None

        def setup_database_connection(db_config):
            """
            Set up a database connection.
            """
            try:
                conn = None  # Replace with actual database connection setup
                return conn
            except Exception as e:
                print(f"Failed to establish database connection: {e}")
                return None

        def fetch_data_and_recommend(conn):
            """
            Fetch data from the database and recommend vehicles.
            """
            cursor = conn.cursor(dictionary=True)
            query = ("SELECT id, PresenceOfChildren, AutoOwnerMake, AutoOwnerModel, IncomeKey "
                    "FROM dis.inventory where AutoOwnerMake = 'FORD' limit 1 ")
            cursor.execute(query)
            records = cursor.fetchall()

            for record in records:
                owner_make = record['AutoOwnerMake'].upper()
                vehicle_list_df = load_vehicle_data('x_unique_cars_final_types_x_3.csv')
                if vehicle_list_df is not None:
                    vehicle_list_df = extract_vehicle_types(vehicle_list_df)

                loyalty_score = LOYALTY_SCORES.get(owner_make, 0)
                is_luxury_owner = owner_make in LUXURY_BRANDS
                presence_of_children = record['PresenceOfChildren'] == 'Yes'
                income_key = INCOME_KEY_MAPPING.get(record['IncomeKey'].upper(), 0)

                top_vehicles = assign_top_vehicles(vehicle_list_df, owner_make, presence_of_children, income_key)

                pprint(f"Recommendations for profile {record['id']}:")
                pprint(f"Owner Make: {owner_make}")
                pprint(f"Loyalty Score: {loyalty_score}")
                pprint(f"Is Luxury Owner: {is_luxury_owner}")
                pprint(f"Presence of Children: {presence_of_children}")
                pprint(f"Income Key: {income_key}")
                pprint("Make, Model (Vehicle Types):")

                for vehicle in top_vehicles:
                    vehicle_type = vehicle.get('VEHICLE_TYPES', 'Unknown Type')
                    pprint(f"{vehicle['MAKE']} {vehicle['MODEL']} ({vehicle_type})")

            cursor.close()

        def main():
            vehicle_list_df = load_vehicle_data('x_unique_cars_final_types_x_3.csv')
            if vehicle_list_df is not None:
                vehicle_list_df = extract_vehicle_types(vehicle_list_df)

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

        def extract_vehicle_types(vehicle_list_df):
            """
            Extract vehicle types from the vehicle list DataFrame.
            """
            vehicle_types_columns = [col for col in vehicle_list_df.columns if col not in ['MAKE', 'MODEL']]
            vehicle_list_df['VEHICLE_TYPES'] = vehicle_list_df[vehicle_types_columns].apply(
                lambda x: '|'.join(x.index[x.astype(bool)]), axis=1
            )
            return vehicle_list_df

        if __name__ == '__main__':
            main()

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

    def adjust_for_vehicle_type_preference(weights, vehicle_list_df, vehicle_types):
        """
        Adjust weights for current vehicle type preference.
        """
        for row in vehicle_list_df.itertuples():
            if any(v_type in vehicle_types for v_type in row.VEHICLE_TYPES):
                weights[row.Index] *= 1.5
        return weights

    def select_vehicles_based_on_weights(vehicle_list_df, weights, owner_make):
        """
        Select vehicles based on calculated weights.
        """
        chosen_indices = []

        # Ensure the weights array is not empty and properly normalized
        if weights.size > 0 and weights.sum() > 0:
            weights /= weights.sum()

            # Select a vehicle of the same make if available
            same_make_indices = vehicle_list_df[vehicle_list_df['MAKE'] == owner_make].index
            if same_make_indices.size > 0:
                chosen_index_same_make = np.random.choice(same_make_indices, size=1)
                chosen_indices.append(chosen_index_same_make[0])

            # Select two more vehicles based on weights
            weights[chosen_indices] = 0  # Setting weights of chosen vehicles to 0 to avoid re-selection
            weights /= weights.sum()  # Re-normalize after modifying weights

            if weights.sum() > 0:  # Check if there are still valid weights left
                chosen_indices_additional = np.random.choice(vehicle_list_df.index, size=2, replace=False, p=weights)
                chosen_indices.extend(chosen_indices_additional)

        return chosen_indices

    def adjust_weights_for_preferences(vehicle_list_df, current_vehicle_types, has_children, luxury_multiplier, loyalty_factor, owner_make):
        """
        Adjusts the weights of vehicles in the vehicle list based on user preferences.

        Parameters:
        - vehicle_list_df (pd.DataFrame): The DataFrame containing the vehicle list.
        - current_vehicle_types (list): The list of current vehicle types preferred by the user.
        - has_children (bool): Indicates whether the user has children.
        - luxury_multiplier (float): The multiplier to adjust the weights of luxury vehicles.
        - loyalty_factor (float): The factor to adjust the weights of vehicles based on loyalty to the current make.
        - owner_make (str): The make of the user's current vehicle.

        Returns:
        - weights (np.array): The adjusted weights of the vehicles in the vehicle list.
        """
        weights = np.ones(len(vehicle_list_df))

        # Adjust for current vehicle type preference
        for vehicle_type in current_vehicle_types:
            type_mask = vehicle_list_df[vehicle_type] == 1
            weights[type_mask] *= 1.5  # Increase the weight for preferred types

        # Adjust for presence of children
        if has_children:
            family_friendly_types = ['SUV', 'MINIVAN', 'LARGE_CAR']  # Define family-friendly vehicle types
            for ff_type in family_friendly_types:
                family_friendly_mask = vehicle_list_df[ff_type] == 1
                weights[family_friendly_mask] *= 1.2  # Slightly increase the weight for family-friendly vehicles

        # Adjust for luxury preference based on income
        luxury_mask = vehicle_list_df['MAKE'].isin(LUXURY_BRANDS)
        weights[luxury_mask] *= luxury_multiplier

        # Apply loyalty factor to the current vehicle's make
        same_make_mask = vehicle_list_df['MAKE'] == owner_make
        weights[same_make_mask] *= loyalty_factor

        return weights

    def extract_vehicle_types(row, vehicle_types_columns):
        return '|'.join(row.index[row.astype(bool)])


def fetch_data_and_recommend(conn):
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

        top_vehicles = assign_top_vehicles(vehicle_list_df, owner_make, presence_of_children, income_key)
        # insert_recommendations(conn, record['id'], top_vehicles)

        pprint(f"Recommendations for profile {record['id']}:")
        
        # Print all of the individual's relevant information
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

    for record in records:
        owner_make = record['AutoOwnerMake'].upper()
        vehicle_list_df = load_vehicle_data('x_unique_cars_final_types_x_3.csv')
        if vehicle_list_df is not None:
            vehicle_list_df = extract_vehicle_types(vehicle_list_df)

        loyalty_score = LOYALTY_SCORES.get(owner_make, 0)
        is_luxury_owner = owner_make in LUXURY_BRANDS
        presence_of_children = record['PresenceOfChildren'] == 'Yes'
        income_key = INCOME_KEY_MAPPING.get(record['IncomeKey'].upper(), 0)


        pprint(f"Recommendations for profile {record['id']}:")
                
        # Print all of the individual's relevant information
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

    cursor.close()

if __name__ == '__main__':
    main()

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

