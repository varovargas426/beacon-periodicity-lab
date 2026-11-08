import unittest
from beacon import candidates


def flow(times):
    return [dict(source="192.0.2.1", destination="198.51.100.1", port=443, epoch_seconds=t)
            for t in times]


class TimingTests(unittest.TestCase):
    def test_jitter_and_missing_sample(self):
        item, = candidates(flow([360, 120, 0, 60, 179, 300]))
        self.assertEqual(item["support"], 1)
        self.assertEqual(item["period_seconds"], 60)
        self.assertIn(121, item["gaps"])

    def test_irregular_and_sparse(self):
        self.assertEqual(candidates(flow([0, 10, 38, 80, 150, 159])), [])
        self.assertEqual(candidates(flow([0, 60, 120] * 5)), [])

    def test_distinct_destinations_do_not_merge(self):
        rows = flow([0, 60, 120, 180, 240, 300])
        rows[-1]["destination"] = "203.0.113.9"
        self.assertEqual(candidates(rows), [])
