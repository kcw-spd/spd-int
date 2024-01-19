import mysql.connector
import os
import random
from dotenv import load_dotenv
"""

AutoOwnerMake -> Brand Loyalty (BrandLoyalty):

Use the provided brand loyalty scores to influence the likelihood of recommending the same brand. Higher scores mean a higher chance of selecting the same brand.
If a customer owns a brand with a high loyalty score, increase the weighting for that brand in the recommendation.
AutoOwnerMake -> Luxury Status (LuxuryStatus):

For customers who own a brand listed as luxury (e.g., 'ACURA', 'BMW', 'MERCEDES-BENZ'), increase the weighting for luxury vehicle types.
Luxury vehicle types might include 'SEDAN', 'SPORTS_CAR', 'ELECTRIC_VEHICLE', and 'FULL_SIZE_SUV'.
PresenceOfChildren -> Spacious Vehicle (SpaciousVehicle):

If a customer has children ('Yes'), prioritize more spacious vehicle types such as 'SUV', 'MID_SIZE_SUV', 'FULL_SIZE_SUV', and 'MINIVAN'.
Increase the weighting for these vehicle types in the recommendation for customers with children.
Vehicle Weighting Logic:

Start with a base weighting for each vehicle type.
Adjust the weights based on the customer's profile:
If BrandLoyalty is high, increase the weight for the customer's current brand.
If LuxuryStatus is true, favor luxury vehicle types.
If PresenceOfChildren is 'Yes', favor spacious vehicle types.
Random Selection with Weighting:

After adjusting the weights based on the customer's profile, use a weighted random selection to choose the vehicle type.
This allows for some randomness while still respecting the weighting influenced by

"""
# This is how a person's car is defined as Luxury 
luxury_brands = ['ACURA', 'ALFA ROMEO', 'ASTON MARTIN', 'AUDI', 'BENTLEY', 'BUICK', 'BMW', 'CADILLAC', 'FERRARI', 'FIAT', 'FISKER', 'GENESIS', 'HUMMER', 'INFINITI', 'JAGUAR', 'KARMA', 'LAMBORGHINI', 'LAND ROVER', 'LEXUS', 'LINCOLN', 'LOTUS', 'MASERATI', 'MAYBACH', 'MCLAREN', 'MERCEDES-BENZ', 'MINI', 'PININFARINA', 'POLESTAR', 'PORSCHE', 'ROLLS-ROYCE', 'SAAB', 'TESLA', 'VOLVO']

# The values and their corresponding weights for the presence of children
presence_of_children = {
'No': 0,
'': 1,
'Yes': 2
}

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

# These are the vehicle types in the database and their corresponding weights
vehicle_types = {
    "SMALL_CAR": 0,
    "MID_SIZE_CAR": 0,
    "FULL_SIZE_CAR": 0,
    "SEDAN": 0,
    "CONVERTIBLE": 0,
    "HATCHBACK": 0,
    "CROSSOVER": 0,
    "WAGON": 0,
    "COUPE": 0,
    "SMALL_TRUCK": 0,
    "MID_SIZE_TRUCK": 0,
    "FULL_SIZE_TRUCK": 0,
    "PICKUP": 0,
    "SUV": 0,
    "SMALL_SUV": 0,
    "MID_SIZE_SUV": 0,
    "FULL_SIZE_SUV": 0,
    "MINIVAN": 0,
    "FULL_SIZE_VAN": 0,
    "COMMERCIAL_VEHICLE": 0,
    "RV": 0,
    "HYPERCAR": 0,
    "SPORTS_CAR": 0,
    "ELECTRIC_VEHICLE": 0
}

# Load environment variables
load_dotenv()
db_config = {
    'host': os.getenv('db_host'),
    'user': os.getenv('db_username'),
    'password': os.getenv('db_password'),
    'database': os.getenv('db_name')
}
# Adjust the vehicle weights to properly influence the recommendation
def adjust_vehicle_weights(presence_of_children, current_make, vehicle_weights):
    # PresenceOfChildren -> Spacious Vehicle
    if presence_of_children == 'Yes':
        vehicle_weights['SUV'] += 2
        vehicle_weights['MID_SIZE_SUV'] += 2
        vehicle_weights['FULL_SIZE_SUV'] += 2
        vehicle_weights['MINIVAN'] += 2

    # AutoOwnerMake -> Brand Loyalty
    loyalty_score = loyalty_scores.get(current_make.upper(), 0)
    
    # For simplification, we're just using the loyalty score directly, but 
    # you could create a more sophisticated weighting based on this score.
    vehicle_weights[current_make.upper()] = loyalty_score
    
    # AutoOwnerMake -> Luxury Status
    if current_make.upper() in luxury_brands:
        for lux_vehicle in ['SEDAN', 'SPORTS_CAR', 'ELECTRIC_VEHICLE', 'FULL_SIZE_SUV']:
            vehicle_weights[lux_vehicle] += 1  # Increase weight for luxury vehicles
            
def assign_vehicle(presence_of_children, current_make):
    # Initialize weights based on base vehicle types
    vehicle_weights = {vehicle: 1 for vehicle in vehicle_types} # Set base weight to 1 for all vehicle types
    
    # Adjust weights based on customer's profile
    adjust_vehicle_weights(presence_of_children, current_make, vehicle_weights)
    
    # Make a weighted random selection
    selected_vehicle_type = weighted_random_selection(vehicle_weights)
    
    return {'type': selected_vehicle_type, 'luxury': current_make in luxury_brands, 'make': current_make}

# Update fetch_data_and_recommend function to correct the query fields
def fetch_data_and_recommend(conn):
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT PresenceOfChildren, AutoOwnerMake FROM inventory_table"  # Adjust column names as per your table
        cursor.execute(query)
        results = cursor.fetchall()

        for record in results:
            recommendation = assign_vehicle(
                record['PresenceOfChildren'],
                record['AutoOwnerMake']  # Correct field name
            )
            print(f"Profile: {record}, Recommendation: {recommendation}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        
"""# Function for weighted random selection
def weighted_random_selection(weights):
    total = sum(weights.values())
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in weights.items():
        if upto + weight >= r:
            return choice
        upto += weight"""

# Function to assign vehicle
def assign_vehicle(presence_of_children, current_make, income_key):
    
    if presence_of_children == 'Yes':
        vehicle_weights['SUV'] += 2
        vehicle_weights['Minivan'] += 2
    luxury_status = current_make in luxury_brands
    if luxury_status:
        vehicle_weights['SportsCar'] += 1
        vehicle_weights['Electric'] += 1
    selected_vehicle_type = weighted_random_selection(vehicle_weights)
    return {'type': selected_vehicle_type, 'luxury': luxury_status, 'make': current_make}

# Function to create database connection
def create_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Function to fetch data and recommend vehicles
def fetch_data_and_recommend(conn):
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT PresenceOfChildren, AutoOwnerMake, IncomeKey FROM inventory_table"  # Adjust column names as per your table
        cursor.execute(query)
        results = cursor.fetchall()

        for record in results:
            recommendation = assign_vehicle(
                record['PresenceOfChildren'], 
                record['LuxuryStatus'] in luxury_brands,  # Adjust for luxury status check
                record['CurrentMake']
            )
            print(f"Profile: {record}, Recommendation: {recommendation}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

# Main execution logic
if __name__ == "__main__":
    conn = create_db_connection()
    if conn:
        fetch_data_and_recommend(conn)
        conn.close()