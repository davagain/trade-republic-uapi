import unittest
from trade_republic_uapi.access_policy import allowed
class AccessTest(unittest.TestCase):
    def test_queries_with_post_are_allowed(self):
        self.assertTrue(allowed('/api/instrument'))
        self.assertTrue(allowed('/api/portfolio'))
    def test_mutations_and_unknown_routes_are_denied(self):
        for p in ['/api/place-order','/api/cancel-order','/api/set-price-alarm','/api/delete-price-alarm','/api/future-endpoint']:
            self.assertFalse(allowed(p))
    def test_execution_requires_explicit_opt_in(self):
        self.assertTrue(allowed('/api/place-order',allow_writes=True))
