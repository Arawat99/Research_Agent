"""Tests for bounded retry behaviour in the retrieval pipeline."""

import unittest
from unittest.mock import Mock

import httpx

from app.tools.retry import is_transient_error, with_retries


class RetryHelperTests(unittest.TestCase):
    def test_transient_network_error_is_identified(self):
        self.assertTrue(is_transient_error(httpx.ConnectError("no connection")))
        self.assertTrue(is_transient_error(httpx.TimeoutException("slow")))
        self.assertTrue(is_transient_error(httpx.ReadTimeout("slow")))

    def test_transient_http_status_is_identified(self):
        for status in (429, 500, 502, 503, 504):
            response = Mock(status_code=status)
            exc = httpx.HTTPStatusError("boom", request=Mock(), response=response)
            self.assertTrue(is_transient_error(exc))

    def test_client_error_is_not_retried(self):
        response = Mock(status_code=404)
        exc = httpx.HTTPStatusError("missing", request=Mock(), response=response)
        self.assertFalse(is_transient_error(exc))
        self.assertFalse(is_transient_error(ValueError("not a network error")))

    def test_with_retries_succeeds_after_transient_failures(self):
        attempts = {"count": 0}

        def flaky():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise httpx.ConnectError("transient")
            return "ok"

        result = with_retries(flaky, attempts=3, base_delay=0)
        self.assertEqual(result, "ok")
        self.assertEqual(attempts["count"], 3)

    def test_with_retries_raises_last_error_when_exhausted(self):
        def always_fails():
            raise httpx.TimeoutException("still down")

        with self.assertRaises(httpx.TimeoutException):
            with_retries(always_fails, attempts=3, base_delay=0)

    def test_with_retries_does_not_swallow_non_transient_error(self):
        def bad_input():
            raise ValueError("bad")

        with self.assertRaises(ValueError):
            with_retries(bad_input, attempts=3, base_delay=0)


if __name__ == "__main__":
    unittest.main()