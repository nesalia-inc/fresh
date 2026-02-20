"""Tests for scraper.http module."""

from unittest import mock

import httpx

from fresh.scraper import http as http_module


class TestFetch:
    """Tests for fetch function."""

    def setup_method(self):
        """Reset the HTTP client before each test."""
        http_module._client = None

    @mock.patch("fresh.scraper.http.get_client")
    def test_successful_fetch(self, mock_get_client):
        """Successful fetch should return response."""
        mock_response = mock.MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_client = mock.MagicMock()
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = http_module.fetch("https://example.com")

        assert result is not None
        mock_client.get.assert_called_once()

    @mock.patch("fresh.scraper.http.get_client")
    def test_http_error_returns_none(self, mock_get_client):
        """HTTP errors should return None."""
        mock_response = mock.MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_client = mock.MagicMock()
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found",
            request=mock.MagicMock(),
            response=mock_response,
        )

        result = http_module.fetch("https://example.com/notfound")

        assert result is None

    @mock.patch("fresh.scraper.http.get_client")
    def test_connection_error_returns_none(self, mock_get_client):
        """Connection errors should return None."""
        mock_client = mock.MagicMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        mock_get_client.return_value = mock_client

        result = http_module.fetch("https://example.com")

        assert result is None


class TestFetchWithRetry:
    """Tests for fetch_with_retry function."""

    def setup_method(self):
        """Reset the HTTP client before each test."""
        http_module._client = None

    @mock.patch("fresh.scraper.http.get_client")
    def test_successful_fetch(self, mock_get_client):
        """Successful fetch should return text."""
        mock_response = mock.MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.text = "Hello World"
        mock_client = mock.MagicMock()
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = http_module.fetch_with_retry("https://example.com")

        assert result == "Hello World"

    @mock.patch("fresh.scraper.http.get_client")
    def test_retry_on_failure(self, mock_get_client):
        """Should retry on failure."""
        mock_response = mock.MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_client = mock.MagicMock()

        # First two calls fail, third succeeds
        mock_client.get.side_effect = [
            httpx.HTTPError("Failed"),
            httpx.HTTPError("Failed"),
            mock_response,
        ]
        mock_get_client.return_value = mock_client

        result = http_module.fetch_with_retry(
            "https://example.com",
            max_retries=3,
            backoff=0.01,
        )

        assert result == "Success"
        assert mock_client.get.call_count == 3

    @mock.patch("fresh.scraper.http.get_client")
    def test_return_response_object(self, mock_get_client):
        """Should return response object when requested."""
        mock_response = mock.MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.text = "Hello"
        mock_client = mock.MagicMock()
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = http_module.fetch_with_retry(
            "https://example.com",
            return_response=True,
        )

        assert isinstance(result, httpx.Response)

    @mock.patch("fresh.scraper.http.get_client")
    def test_all_retries_fail(self, mock_get_client):
        """Should return None when all retries fail."""
        mock_client = mock.MagicMock()
        mock_client.get.side_effect = httpx.HTTPError("Failed")
        mock_get_client.return_value = mock_client

        result = http_module.fetch_with_retry(
            "https://example.com",
            max_retries=3,
            backoff=0.01,
        )

        assert result is None


class TestHTTPClient:
    """Tests for HTTPClient class."""

    def setup_method(self):
        """Reset the HTTP client before each test."""
        http_module._client = None

    @mock.patch("fresh.scraper.http.get_client")
    def test_context_manager(self, mock_get_client):
        """Should work as context manager."""
        mock_client = mock.MagicMock(spec=httpx.Client)
        mock_get_client.return_value = mock_client

        with http_module.HTTPClient() as client:
            assert client is mock_client

    @mock.patch("fresh.scraper.http.get_client")
    def test_get_client_method(self, mock_get_client):
        """get_client method should return the client."""
        mock_client = mock.MagicMock(spec=httpx.Client)
        mock_get_client.return_value = mock_client

        http_client = http_module.HTTPClient()
        assert http_client.get_client() is mock_client


class TestThreadSafety:
    """Tests for thread safety."""

    def setup_method(self):
        """Reset the HTTP client before each test."""
        http_module._client = None

    @mock.patch("fresh.scraper.http.get_client")
    def test_concurrent_access(self, mock_get_client):
        """Concurrent access should be thread-safe."""
        import threading

        mock_client = mock.MagicMock(spec=httpx.Client)
        mock_get_client.return_value = mock_client

        results = []

        def access_client():
            client = http_module.get_client()
            results.append(client)

        threads = [threading.Thread(target=access_client) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should get the same client
        assert len(set(results)) == 1


class TestValidateUrl:
    """Tests for validate_url function."""

    def test_valid_https_url(self):
        """Valid HTTPS URL should be allowed."""
        assert http_module.validate_url("https://example.com/docs")

    def test_valid_http_url(self):
        """Valid HTTP URL should be allowed."""
        assert http_module.validate_url("http://example.com/docs")

    def test_block_file_scheme(self):
        """File scheme should be blocked."""
        assert not http_module.validate_url("file:///etc/passwd")

    def test_block_ftp_scheme(self):
        """FTP scheme should be blocked."""
        assert not http_module.validate_url("ftp://example.com/file")

    def test_block_localhost(self):
        """Localhost should be blocked."""
        assert not http_module.validate_url("http://localhost:8080")
        assert not http_module.validate_url("http://127.0.0.1/admin")
        assert not http_module.validate_url("http://::1/admin")

    def test_block_private_ip(self):
        """Private IPs should be blocked."""
        assert not http_module.validate_url("http://0.0.0.0/admin")

    def test_block_private_ip_ranges(self):
        """Private IP ranges should be blocked."""
        # 10.0.0.0/8
        assert not http_module.validate_url("http://10.0.0.1/admin")
        assert not http_module.validate_url("http://10.255.255.255/admin")
        # 172.16.0.0/12
        assert not http_module.validate_url("http://172.16.0.1/admin")
        assert not http_module.validate_url("http://172.31.255.255/admin")
        # 192.168.0.0/16
        assert not http_module.validate_url("http://192.168.0.1/admin")
        assert not http_module.validate_url("http://192.168.255.255/admin")

    def test_allow_public_ips(self):
        """Public IPs should be allowed."""
        assert http_module.validate_url("http://8.8.8.8/dns")
        assert http_module.validate_url("http://1.1.1.1/dns")

    def test_block_dot_local(self):
        """.local domains should be blocked."""
        assert not http_module.validate_url("http://myserver.local/admin")

    def test_allowed_domains_whitelist(self):
        """Should respect allowed domains whitelist."""
        allowed = ["example.com", "docs.example.com"]
        assert http_module.validate_url("https://example.com/docs", allowed)
        assert http_module.validate_url("https://docs.example.com/api", allowed)
        assert not http_module.validate_url("https://evil.com/docs", allowed)

    def test_invalid_url_returns_false(self):
        """Invalid URLs should return False."""
        assert not http_module.validate_url("not-a-url")


class TestRobotsTxt:
    """Tests for robots.txt functions."""

    def setup_method(self):
        """Reset caches before each test."""
        http_module._robots_cache.clear()

    @mock.patch("fresh.scraper.http.fetch_robots_txt")
    def test_is_allowed_by_robots_no_robots(self, mock_fetch):
        """Should allow when no robots.txt exists."""
        mock_fetch.return_value = None
        result = http_module.is_allowed_by_robots("https://example.com/page")
        assert result is True

    @mock.patch("fresh.scraper.http.fetch_robots_txt")
    def test_is_allowed_by_robots_disallow(self, mock_fetch):
        """Should disallow paths in robots.txt."""
        robots_content = """User-agent: *
Disallow: /admin
Disallow: /private/
"""
        mock_fetch.return_value = robots_content
        result = http_module.is_allowed_by_robots("https://example.com/admin")
        assert result is False

    @mock.patch("fresh.scraper.http.fetch_robots_txt")
    def test_is_allowed_by_robots_allowed_path(self, mock_fetch):
        """Should allow paths not in robots.txt."""
        robots_content = """User-agent: *
Disallow: /admin
"""
        mock_fetch.return_value = robots_content
        result = http_module.is_allowed_by_robots("https://example.com/public")
        assert result is True

    @mock.patch("fresh.scraper.http.fetch_robots_txt")
    def test_is_allowed_by_robots_specific_user_agent(self, mock_fetch):
        """Should respect specific user-agent rules."""
        robots_content = """User-agent: bot
Disallow: /private

User-agent: *
Allow: /
"""
        mock_fetch.return_value = robots_content
        # Default user-agent * should be allowed
        result = http_module.is_allowed_by_robots("https://example.com/private")
        assert result is True

    def test_matches_robots_pattern_simple(self):
        """Simple pattern matching (prefix-based)."""
        assert http_module._matches_robots_pattern("/admin", "/admin")
        assert http_module._matches_robots_pattern("/admin/", "/admin")
        # Uses prefix matching, so /administration also matches /admin
        assert http_module._matches_robots_pattern("/administration", "/admin")

    def test_matches_robots_pattern_wildcard(self):
        """Wildcard pattern matching."""
        assert http_module._matches_robots_pattern("/admin/page", "/admin/*")
        assert http_module._matches_robots_pattern("/admin", "/admin*")
        # Uses prefix matching for wildcards too
        assert http_module._matches_robots_pattern("/adminpage", "/admin*")

    def test_matches_robots_pattern_end_anchor(self):
        """End anchor pattern matching."""
        assert http_module._matches_robots_pattern("/admin", "/admin$")
        assert not http_module._matches_robots_pattern("/admin/page", "/admin$")

    @mock.patch("fresh.scraper.http.fetch_robots_txt")
    def test_fetch_robots_txt(self, mock_fetch):
        """Test fetch_robots_txt function."""
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = "User-agent: *\nDisallow: /admin"
        mock_client = mock.MagicMock()
        mock_client.get.return_value = mock_response
        mock_fetch.return_value = mock_response.text

        with mock.patch("fresh.scraper.http.get_client", return_value=mock_client):
            result = http_module.fetch_robots_txt("https://example.com")

        assert result is not None
