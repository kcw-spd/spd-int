import unittest
from unittest.mock import MagicMock
from fast_main import fetch_data_and_recommend

class TestFetchDataAndRecommend(unittest.TestCase):
    def test_fetch_data_and_recommend(self):
        # Mock the database connection
        conn = MagicMock()

        # Mock the cursor and its execute method
        cursor = MagicMock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = [
            {
                'AutoOwnerMake': 'FORD',
                'PresenceOfChildren': 'Yes',
                'IncomeKey': 'A'
            }
        ]

        # Mock the pd.read_csv method
        pd.read_csv = MagicMock(return_value=pd.DataFrame({
            'MAKE': ['FORD', 'TOYOTA'],
            'MODEL': ['F150', 'CAMRY'],
            'SEDAN': [False, True],
            'SUV': [True, False]
        }))

        # Call the function
        fetch_data_and_recommend(conn)

        # Assert that the expected print statements are called
        expected_print_statements = [
            "Recommendations for profile 1:",
            "Owner Make: FORD",
            "Loyalty Score: 0",
            "Is Luxury Owner: False",
            "Presence of Children: True",
            "Income Key: 1",
            "Make, Model (Vehicle Types):",
            "FORD F150 (SUV)",
            "TOYOTA CAMRY (SEDAN)"
        ]
        self.assertEqual(expected_print_statements, [call[0][0] for call in print.call_args_list])

        # Assert that the pd.read_csv method is called with the correct file name
        pd.read_csv.assert_called_with('x_unique_cars_final_types_x_3.csv')

        # Assert that the cursor.execute method is called with the correct query
        cursor.execute.assert_called_with("SELECT id, PresenceOfChildren, AutoOwnerMake, AutoOwnerModel, IncomeKey FROM dis.inventory where AutoOwnerMake = 'FORD' limit 1 ")

if __name__ == '__main__':
    unittest.main()