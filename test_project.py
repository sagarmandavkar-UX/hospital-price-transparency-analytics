import unittest
import analysis

class AnalysisTests(unittest.TestCase):
    def test_cleans_invalid_and_duplicate_rates(self):
        clean, quality = analysis.clean_rates(analysis.make_demo_rates())
        self.assertEqual(quality["invalid_rates"], 1)
        self.assertEqual(quality["duplicates_removed"], 2)
        self.assertTrue((clean["rate"] > 0).all())

if __name__ == "__main__":
    unittest.main()
