import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import unittest
from agent import build_plan, parse_prompt
from mock_qloo import MockQlooClient

C = MockQlooClient()


class TestAgent(unittest.TestCase):
    def test_parse(self):
        p = parse_prompt("romantic Bollywood evening in Los Angeles for 2, cheap")
        self.assertIn("bollywood", p["seeds"])
        self.assertIn("romantic", p["seeds"])
        self.assertEqual(p["budget"], 1)
        self.assertEqual(p["group"], 2)

    def test_jazz_plan_has_cross_domain_stops(self):
        plan, trace = build_plan(C, "Jazz evening in Los Angeles, cheap, for 4 friends")
        self.assertNotIn("error", plan)
        domains = {s["domain"] for s in plan["stops"]}
        self.assertTrue(len(domains) >= 2, domains)
        self.assertTrue(all(s["why"] for s in plan["stops"]))

    def test_budget_critic_filters_expensive(self):
        plan, _ = build_plan(C, "romantic evening in Los Angeles, cheap")
        self.assertNotIn("error", plan)
        # Rooftop (price 3) must not appear on a cheap plan; all picks come
        # from the mock catalog, so check no stop name contains 'Perch'.
        self.assertFalse(any("Perch" in s["name"] for s in plan["stops"]))

    def test_no_seed_is_honest_error_not_invention(self):
        plan, _ = build_plan(C, "plan something nice")
        self.assertIn("error", plan)

    def test_no_duplicates(self):
        plan, _ = build_plan(C, "dreamy indie night in Los Angeles")
        names = [s["name"] for s in plan["stops"]]
        self.assertEqual(len(names), len(set(names)))

    def test_mock_search_and_insights(self):
        self.assertTrue(C.search("jazz"))
        seeds = [e["id"] for e in C.search("jazz")[:1]]
        recs = C.insights(seeds, target_domain="dining")
        self.assertTrue(recs and recs[0]["affinity"] >= 0.55)


if __name__ == "__main__":
    unittest.main()
