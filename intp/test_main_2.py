import unittest
from unittest.mock import MagicMock
from main_2 import (
    load_vehicle_data,
    setup_database_connection,
    adjust_for_vehicle_type_preference,
    adjust_for_family_friendly,
    adjust_for_luxury_preference,
    adjust_for_loyalty,
    assign_top_vehicles,
    select_vehicles_based_on_weights,
    fetch_data_and_recommend
)

class TestMain2(unittest.TestCase):
    def test_load_vehicle_data(self):
        # Test when file exists
        filepath = 'test_data.csv'
        expected_df = pd.DataFrame({'MAKE': ['FORD', 'TOYOTA'], 'MODEL': ['F150', 'CAMRY']})
        actual_df = load_vehicle_data(filepath)
        pd.testing.assert_frame_equal(expected_df, actual_df)

        # Test when file does not exist
        filepath = 'nonexistent_file.csv'
        actual_df = load_vehicle_data(filepath)
        self.assertIsNone(actual_df)

    def test_setup_database_connection(self):
        # Test when connection is successful
        config = {'host': 'localhost', 'user': 'root', 'password': 'password', 'database': 'test_db'}
        conn = setup_database_connection(config)
        self.assertIsNotNone(conn)
        self.assertTrue(conn.is_connected())

        # Test when connection fails
        config = {'host': 'localhost', 'user': 'root', 'password': 'wrong_password', 'database': 'test_db'}
        conn = setup_database_connection(config)
        self.assertIsNone(conn)

    def test_adjust_for_vehicle_type_preference(self):
        # Mock data
        weights = pd.DataFrame({'weight': [1.0, 1.0, 1.0]})
        vehicle_list_df = pd.DataFrame({'MAKE': ['FORD', 'TOYOTA', 'HONDA'], 'VEHICLE_TYPES': [['SUV'], ['SEDAN'], ['SUV']]})
        config = {'VEHICLE_TYPE_COLUMN': ['VEHICLE_TYPES']}
        auto_owner_model = 'SEDAN'

        # Call the function
        adjust_for_vehicle_type_preference(weights, vehicle_list_df, config, auto_owner_model)

        # Assert the weights are adjusted correctly
        expected_weights = pd.DataFrame({'weight': [1.0, 1.5, 1.0]})
        pd.testing.assert_frame_equal(expected_weights, weights)

    def test_adjust_for_family_friendly(self):
        # Mock data
        weights = pd.DataFrame({'weight': [1.0, 1.0, 1.0]})
        vehicle_list_df = pd.DataFrame({'SUV': [1, 0, 1]})
        has_children = True
        family_friendly_types = ['SUV']

        # Call the function
        adjust_for_family_friendly(weights, vehicle_list_df, has_children, family_friendly_types)

        # Assert the weights are adjusted correctly
        expected_weights = pd.DataFrame({'weight': [1.2, 1.0, 1.2]})
        pd.testing.assert_frame_equal(expected_weights, weights)

    def test_adjust_for_luxury_preference(self):
        # Mock data
        weights = pd.DataFrame({'weight': [1.0, 1.0, 1.0]})
        vehicle_list_df = pd.DataFrame({'MAKE': ['FORD', 'BMW', 'TOYOTA']})
        luxury_multiplier = 1.5
        luxury_brands = ['BMW']

        # Call the function
        adjust_for_luxury_preference(weights, vehicle_list_df, luxury_multiplier, luxury_brands)

        # Assert the weights are adjusted correctly
        expected_weights = pd.DataFrame({'weight': [1.0, 1.5, 1.0]})
        pd.testing.assert_frame_equal(expected_weights, weights)

    def test_adjust_for_loyalty(self):
        # Mock data
        weights = pd.DataFrame({'weight': [1.0, 1.0, 1.0]})
        vehicle_list_df = pd.DataFrame({'MAKE': ['FORD', 'TOYOTA', 'FORD']})
        loyalty_factor = 2
        owner_make = 'FORD'

        # Call the function
        adjust_for_loyalty(weights, vehicle_list_df, loyalty_factor, owner_make)

        # Assert the weights are adjusted correctly
        expected_weights = pd.DataFrame({'weight': [2.0, 1.0, 2.0]})
        pd.testing.assert_frame_equal(expected_weights, weights)

    def test_assign_top_vehicles(self):
        # Mock data
        vehicle_list_df = pd.DataFrame({'MAKE': ['FORD', 'TOYOTA', 'HONDA'], 'VEHICLE_TYPES': [['SUV'], ['SEDAN'], ['SUV']]})
        owner_vehicle_info = {'MAKE': 'FORD', 'VEHICLE_TYPES': ['SUV']}
        presence_of_children = True
        income_key = 'LOW'

        # Call the function
        recommended_vehicles = assign_top_vehicles(vehicle_list_df, owner_vehicle_info, presence_of_children, income_key)

        # Assert the recommended vehicles are correct
        expected_vehicles = [{'MAKE': 'FORD', 'MODEL': 'F150', 'VEHICLE_TYPES': ['SUV']}, {'MAKE': 'HONDA', 'MODEL': 'CIVIC', 'VEHICLE_TYPES': ['SUV']}]
        self.assertEqual(expected_vehicles, recommended_vehicles)

    def test_select_vehicles_based_on_weights(self):
        # Mock data
        vehicle_list_df = pd.DataFrame({'MAKE': ['FORD', 'TOYOTA', 'HONDA']})
        weights = np.array([0.2, 0.5, 0.3])
        owner_make = 'FORD'

        # Call the function
        chosen_indices = select_vehicles_based_on_weights(vehicle_list_df, weights, owner_make)

        # Assert the chosen indices are correct
        expected_indices = [1]  # Randomly chosen index based on weights
        self.assertEqual(expected_indices, chosen_indices)

    def test_fetch_data_and_recommend(self):
        # Mock data
        conn = MagicMock()
        cursor = MagicMock()
        conn.cursor.return_value = cursor
        cursor.execute.return_value = None

        # Call the function
        fetch_data_and_recommend(conn)

        # Assert that the cursor.execute method is called with the correct query
        cursor.execute.assert_called_with("SELECT id, PresenceOfChildren, AutoOwnerMake, AutoOwnerModel, IncomeKey FROM dis.inventory where AutoOwnerMake = 'FORD' limit 1 ")

if __name__ == '__main__':
    unittest.main()