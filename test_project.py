import unittest
import analysis

class AnalysisTests(unittest.TestCase):
    def test_cleans_invalid_and_duplicate_rates(self):
        clean, quality = analysis.clean_rates(analysis.make_demo_rates())
        self.assertEqual(quality["invalid_rates"], 1)
        self.assertEqual(quality["duplicates_removed"], 2)
        self.assertTrue((clean["rate"] > 0).all())

    def test_benchmarks_and_bootstrap(self):
        clean, _ = analysis.clean_rates(analysis.make_demo_rates())
        payer = analysis.payer_price_index(clean)
        outliers = analysis.hospital_outliers(clean)
        rural = analysis.bootstrap_rural_difference(clean, draws=200)
        self.assertTrue(payer["median_price_index"].gt(0).all())
        self.assertTrue(outliers["relative_to_benchmark"].ge(1.5).all())
        self.assertLess(rural["ci_low"], rural["ci_high"])

if __name__ == "__main__":
    unittest.main()
