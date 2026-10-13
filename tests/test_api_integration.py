import os
import unittest
from unittest.mock import patch,AsyncMock
from fastapi.testclient import TestClient
from trade_republic_uapi.api_server import app

class ApiPermissionsTest(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ,{'TR_UAPI_KEY':'local-test-only','TR_UAPI_ALLOW_WRITES':'0'})
        self.env.start();self.addCleanup(self.env.stop)
        self.client=TestClient(app)
        self.headers={'X-API-Key':'local-test-only'}
    def test_missing_or_invalid_key_denied(self):
        self.assertIn(self.client.get('/api/accounts').status_code,(401,403))
        self.assertEqual(self.client.get('/api/accounts',headers={'X-API-Key':'wrong'}).status_code,401)
    def test_read_route_can_execute_without_broker(self):
        with patch('trade_republic_uapi.api_server.get_accounts_data',new=AsyncMock(return_value=[])) as upstream:
            r=self.client.get('/api/accounts',headers=self.headers)
            self.assertEqual(r.status_code,200);upstream.assert_awaited_once()
    def test_mutations_denied_before_any_broker_request(self):
        with patch('trade_republic_uapi.api_server.call_tr_ws_api',new=AsyncMock()) as upstream:
            for path in ['/api/place-order','/api/cancel-order','/api/set-price-alarm','/api/delete-price-alarm']:
                self.assertEqual(self.client.post(path,json={},headers=self.headers).status_code,403)
            upstream.assert_not_called()
