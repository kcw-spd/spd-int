from main import get_vehicle_types_based_on_model, extract_vehicle_types, load_config
from main import get_vehicle_types_based_on_model, extract_vehicle_types, load_config
# Test the function
sample_config = load_config("config.yml")



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

# Test the further corrected function
weights_ff_aligned = adjust_for_family_friendly(weights, inventory_df, config, presence_of_children)
weights_ff_aligned.head()
# Test the corrected function
adjust_for_vehicle_type_preference(weights, cars_df, sample_config, 'Sedan')
weights.head()

# Test the function
sample_config = load_config("config.yml")



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

# Test the further corrected function
weights_ff_aligned = adjust_for_family_friendly(weights, inventory_df, config, presence_of_children)
weights_ff_aligned.head()
# Test the corrected function
adjust_for_vehicle_type_preference(weights, cars_df, sample_config, 'Sedan')
weights.head()