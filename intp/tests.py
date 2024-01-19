import unittest
import pandas as pd
import numpy as np
from main_2 import (
    load_vehicle_data,
    setup_database_connection,
    adjust_for_vehicle_type_preference,
    adjust_for_family_friendly,
    adjust_for_luxury_preference,
    adjust_for_loyalty,
    assign_top_vehicles,
)

class TestMainFunctions(unittest.TestCase):
    def setUp(self):
        self.filepath = 'vehicle_data.csv'
        self.vehicle_list_df = pd.DataFrame({
            'MAKE': ['FORD', 'TOYOTA', 'HONDA'],
            'MODEL': ['F150', 'CAMRY', 'CIVIC'],
            'VEHICLE_TYPES': [['SUV'], ['SEDAN'], ['SEDAN']],
        })
        self.weights = np.ones(len(self.vehicle_list_df))

    def test_load_vehicle_data(self):
        vehicle_list_df = load_vehicle_data(self.filepath)
        self.assertIsNotNone(vehicle_list_df)
        self.assertIsInstance(vehicle_list_df, pd.DataFrame)

    def test_setup_database_connection(self):
        config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'password',
            'database': 'test_db',
        }
        conn = setup_database_connection(config)
        self.assertIsNotNone(conn)
        self.assertTrue(conn.is_connected())

    def test_adjust_for_vehicle_type_preference(self):
        config = {
            'VEHICLE_TYPE_COLUMN': ['SEDAN', 'SUV'],
        }
        auto_owner_model = 'F150'
        adjusted_weights = adjust_for_vehicle_type_preference(
            self.weights, self.vehicle_list_df, config, auto_owner_model
        )
        expected_weights = np.array([1.5, 1.0, 1.0])
        np.testing.assert_array_equal(adjusted_weights, expected_weights)

    def test_adjust_for_family_friendly(self):
        presence_of_children = True
        family_friendly_types = ['SEDAN']
        adjusted_weights = adjust_for_family_friendly(
            self.weights, self.vehicle_list_df, presence_of_children, family_friendly_types
        )
        expected_weights = np.array([1.0, 1.2, 1.0])
        np.testing.assert_array_equal(adjusted_weights, expected_weights)

    def test_adjust_for_luxury_preference(self):
        luxury_multiplier = 1.5
        luxury_brands = ['FORD']
        adjusted_weights = adjust_for_luxury_preference(
            self.weights, self.vehicle_list_df, luxury_multiplier, luxury_brands
        )
        expected_weights = np.array([1.5, 1.0, 1.0])
        np.testing.assert_array_equal(adjusted_weights, expected_weights)

    def test_adjust_for_loyalty(self):
        loyalty_factor = 2.0
        owner_make = 'FORD'
        adjusted_weights = adjust_for_loyalty(
            self.weights, self.vehicle_list_df, loyalty_factor, owner_make
        )
        expected_weights = np.array([2.0, 1.0, 1.0])
        np.testing.assert_array_equal(adjusted_weights, expected_weights)

    def test_assign_top_vehicles(self):
        owner_vehicle_info = {
            'MAKE': 'FORD',
            'VEHICLE_TYPES': ['SUV'],
        }
        presence_of_children = True
        income_key = 'A'
        recommended_vehicles = assign_top_vehicles(
            self.vehicle_list_df, owner_vehicle_info, presence_of_children, income_key
        )
        expected_vehicles = [
            {'MAKE': 'FORD', 'MODEL': 'F150', 'VEHICLE_TYPES': ['SUV']},
            {'MAKE': 'TOYOTA', 'MODEL': 'CAMRY', 'VEHICLE_TYPES': ['SEDAN']},
            {'MAKE': 'HONDA', 'MODEL': 'CIVIC', 'VEHICLE_TYPES': ['SEDAN']},
        ]
        self.assertEqual(recommended_vehicles, expected_vehicles)

if __name__ == '__main__':
    unittest.main()