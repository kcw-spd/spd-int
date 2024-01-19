import pandas as pd
import numpy as np
import random

# Sample data for demonstration
vehicle_list_data = {
    'MAKE': ['Toyota', 'Honda', 'BMW', 'Audi', 'Ford'],
    'MODEL': ['Camry', 'Civic', 'X5', 'A4', 'Focus'],
    'VEHICLE_TYPES': ['Sedan', 'Sedan', 'SUV', 'Sedan', 'Sedan']
}
vehicle_list_df = pd.DataFrame(vehicle_list_data)

# Sample luxury brands and spacious vehicle types
luxury_brands = ['BMW', 'Audi']
spacious_vehicle_types = ['SUV', 'MINIVAN']

# Sample record to demonstrate the recommendation logic
sample_record = {
    'AutoOwnerMake': 'Toyota',
    'PresenceOfChildren': 'Yes',
    'IncomeKey': 'M'  # Assuming 'M' corresponds to a mid-level income
}

# Loyalty scores (simplified for demonstration)
loyalty_scores = {
    'Toyota': 0.5,
    'Honda': 0.4,
    'BMW': 0.6,
    'Audi': 0.6,
    'Ford': 0.3
}


def assign_top_vehicles(vehicle_list_df, owner_make, owner_loyalty_score, is_luxury_owner, presence_of_children, income_key):
    weights = np.ones(len(vehicle_list_df))

    # Adjust weights based on owner's loyalty to the brand
    same_make_mask = (vehicle_list_df['MAKE'] == owner_make)
    weights[same_make_mask] += owner_loyalty_score

    # Double the weight for luxury brands if the owner already owns a luxury brand
    if is_luxury_owner:
        luxury_brand_mask = vehicle_list_df['MAKE'].isin(luxury_brands)
        weights[luxury_brand_mask] *= 2

    # Increase weight by 1.5x for spacious vehicles if the owner has children
    if presence_of_children == 'Yes':
        spacious_mask = vehicle_list_df['VEHICLE_TYPES'].isin(spacious_vehicle_types)
        weights[spacious_mask] *= 1.5

    # Normalize weights to sum to 1
    weights /= weights.sum()

    # Choose top vehicle based on weights
    chosen_index = np.random.choice(vehicle_list_df.index, p=weights)
    recommended_vehicle = vehicle_list_df.loc[chosen_index]

    return recommended_vehicle[['MAKE', 'MODEL', 'VEHICLE_TYPES']].to_dict()

# Using the sample record for a single recommendation
owner_make = sample_record['AutoOwnerMake']
loyalty_score = loyalty_scores.get(owner_make, 0)
is_luxury_owner = owner_make in luxury_brands
presence_of_children = sample_record['PresenceOfChildren']
income_key = income_key_mapping.get(sample_record['IncomeKey'].upper(), 0)

recommended_vehicle = assign_top_vehicles(vehicle_list_df, owner_make, loyalty_score, is_luxury_owner, presence_of_children, income_key)
print("Recommended Vehicle:", recommended_vehicle)
