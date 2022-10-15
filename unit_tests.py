import unittest
from main import *


def is_between(a, val, b):
    return a < val < b


class Option_Tests(unittest.TestCase):
    def test_create_option(self):
        option = Option(10, 11, 1, 0.4, 0.03, lambda x, E: max(x-E, 0))
        self.assertIsInstance(option, Option)

    def test_check_option_values(self):
        option = Option(10, 11, 1, 0.4, 0.03, lambda x, E: max(x-E, 0))
        self.assertEqual(10, option.spot_price)
        self.assertEqual(11, option.strike_price)
        self.assertEqual(0.4, option.volatility)
        self.assertEqual(0.03, option.interest_rate)

    def test_option_return_parameters(self):
        option = Option(10, 11, 1, 0.4, 0.03, lambda x, E: max(x - E, 0))
        self.assertEqual((10, 11, 0.03, 0.4, 0, 1), option.return_parameters())

    def test_create_invalid_barrier_option(self):
        """
        checks if making an option with a lower barrier above an upper barrier throws an exception
        """
        option_creation_failed = False
        try:
            option = Option(11, 12, 1, 0.35, 0.02, lambda x, E: max(x-E, 0), is_american=False, lower_barrier=15,
                            upper_barrier=10)
        except Exception:
            option_creation_failed = True
        self.assertTrue(option_creation_failed)

class Tree_Tests(unittest.TestCase):
    def test_european_option_binomial(self):
        option = Option(12, 10, 1, 0.35, 0.02, lambda x, E: max(x-E, 0))
        estimated_value = k_nomial(option,"lr",100,2)
        self.assertTrue(is_between(2.85,estimated_value,2.86))

    def test_european_option_trinomial(self):
        option = Option(12, 10, 1, 0.35, 0.02, lambda x, E: max(x-E, 0))
        estimated_value = k_nomial(option,"lr",100,3)
        self.assertTrue(is_between(2.85,estimated_value,2.86))

    def test_european_option_200_branches(self):
        option = Option(12, 10, 1, 0.35, 0.02, lambda x, E: max(x-E, 0))
        estimated_value = k_nomial(option,"lr",1,200)
        self.assertTrue(is_between(2.85,estimated_value,2.86))

    def test_american_call_option_binomial(self):
        #should be the same vlaue as a european call as there are no dividends
        option = Option(12, 10, 1, 0.35, 0.02, lambda x, E: max(x-E, 0), is_american=True)
        estimated_value = k_nomial(option,"lr",200,2)
        self.assertTrue(is_between(2.85,estimated_value,2.86))


    def test_american_put_option_binomial(self):
        option = Option(12, 10, 1, 0.35, 0.02, lambda x, E: max(E-x, 0), is_american=True)
        estimated_value = k_nomial(option,"lr",200,2)
        self.assertTrue(is_between(0.66,estimated_value,0.67))


class Finite_Difference_Tests(unittest.TestCase):
    def test_european_call_option_implicit(self):
        option = Option(12, 10, 1, 0.35, 0.02, lambda x, E: max(x-E, 0), is_american=False)
        fdm_obj = FDM(option, 200, mode="implicit")
        estimated_value = fdm_obj.get_value_estimation_at_start(12)
        self.assertTrue(is_between(2.85,estimated_value,2.86))

    def test_european_call_option_cn(self):
        option = Option(12, 10, 1, 0.35, 0.02, lambda x, E: max(x-E, 0), is_american=False)
        fdm_obj = FDM(option, 200, mode="cn")
        estimated_value = fdm_obj.get_value_estimation_at_start(12)
        self.assertTrue(is_between(2.85,estimated_value,2.86))

    def test_american_put_option_implict(self):
        option = Option(12, 10, 1, 0.35, 0.02, lambda x, E: max(E-x, 0), is_american=True)
        fdm_obj = FDM(option, 300, mode="implicit")
        estimated_value = fdm_obj.get_value_estimation_at_start(12)
        self.assertTrue(is_between(0.66,estimated_value,0.67))

    def test_american_put_option_cn(self):
        option = Option(12, 10, 1, 0.35, 0.02, lambda x, E: max(E-x, 0), is_american=True)
        fdm_obj = FDM(option, 200, mode="cn")
        estimated_value = fdm_obj.get_value_estimation_at_start(12)
        self.assertTrue(is_between(0.66,estimated_value,0.67))


class Barrier_Test(unittest.TestCase):
    def test_binomial_lower_barrier(self):
        option = Option(11, 12, 1, 0.35, 0.02, lambda x, E: max(x-E, 0), is_american=False, lower_barrier=10)
        tree_val = k_nomial(option, "lr", 2000, 2)
        fdm_obj = FDM(option, 2000, mode="cn")
        fdm_val = fdm_obj.get_value_estimation_at_start(11)
        self.assertTrue(abs(tree_val - fdm_val)/fdm_val < 0.1)

    def test_binomial_upper_barrier(self):
        option = Option(11, 12, 1, 0.35, 0.02, lambda x, E: max(x-E, 0), is_american=False, upper_barrier=15)
        tree_val = k_nomial(option, "lr", 2000, 2)
        fdm_obj = FDM(option, 2000, mode="cn")
        fdm_val = fdm_obj.get_value_estimation_at_start(11)
        self.assertTrue(abs(tree_val - fdm_val)/fdm_val < 0.1)

    def test_binomial_two_barriers(self):
        option = Option(11, 12, 1, 0.35, 0.02, lambda x, E: max(x-E, 0), is_american=False, lower_barrier=10, upper_barrier=15)
        tree_val = k_nomial(option, "lr", 2000, 2)
        fdm_obj = FDM(option, 2000, mode="cn")
        fdm_val = fdm_obj.get_value_estimation_at_start(11)
        self.assertTrue(abs(tree_val - fdm_val)/fdm_val < 0.5)



if __name__ == '__main__':
    unittest.main()
