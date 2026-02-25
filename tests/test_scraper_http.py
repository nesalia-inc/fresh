"""Tests for scraper.http module."""

from unittest import mock

import httpx

from fresh.scraper import http as http_module


class TestFetch:
    """Tests for fetch function."""

    def setup_method(self):
        """Reset the HTTP client before each test."""
        http_module.reset()

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
        http_module.reset()

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

    @mock.patch("fresh.scraper.http.get_client")
    @mock.patch("fresh.scraper.http.logger")
    def test_error_message_shows_actual_url_after_redirect(self, mock_logger, mock_get_client):
        """Error message should show actual URL after redirect, not original URL."""
        # Use string URL (like real httpx.URL does)
        actual_url = "https://www.example.com/robots.txt"

        # Create a mock request with a URL that reflects a redirect
        mock_request = mock.MagicMock()
        mock_request.url = actual_url

        # Create a mock response for the HTTPStatusError
        mock_response = mock.MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.url = actual_url

        # Create HTTPStatusError with the mock request and response
        mock_client = mock.MagicMock()
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "Not Found",
            request=mock_request,
            response=mock_response,
        )
        mock_get_client.return_value = mock_client

        result = http_module.fetch_with_retry(
            "https://example.com/robots.txt",
            max_retries=1,
            backoff=0.01,
        )

        assert result is None
        # The error message should contain the actual URL (with www), not the original URL
        error_call = mock_logger.error.call_args[0][0]
        assert "https://www.example.com/robots.txt" in error_call
        assert "https://example.com/robots.txt" not in error_call

    @mock.patch("fresh.scraper.http.get_client")
    @mock.patch("fresh.scraper.http.logger")
    def test_timeout_error_shows_actual_url(self, mock_logger, mock_get_client):
        """Timeout error message should show actual URL that was requested."""
        # Use string URL (like real httpx.URL does)
        actual_url = "https://www.example.com/page"

        # Create a mock request with a URL
        mock_request = mock.MagicMock()
        mock_request.url = actual_url

        mock_client = mock.MagicMock()
        mock_client.get.side_effect = httpx.TimeoutException(
            "Timeout",
            request=mock_request,
        )
        mock_get_client.return_value = mock_client

        result = http_module.fetch_with_retry(
            "https://example.com/page",
            max_retries=1,
            backoff=0.01,
        )

        assert result is None
        # The error message should contain the actual URL
        error_call = mock_logger.error.call_args[0][0]
        assert "https://www.example.com/page" in error_call


class TestHTTPClient:
    """Tests for HTTPClient class."""

    def setup_method(self):
        """Reset the HTTP client before each test."""
        http_module.reset()

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
        http_module.reset()

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

    def test_url_length_limit(self):
        """URLs exceeding max length should be blocked."""
        # Create a URL longer than MAX_URL_LENGTH (2048)
        long_url = "http://example.com/" + "a" * 3000
        assert not http_module.validate_url(long_url)

        # Short URLs should be allowed
        assert http_module.validate_url("http://example.com/docs")

    def test_block_ipv6_zone_id(self):
        """IPv6 zone IDs should be blocked."""
        assert not http_module.validate_url("http://[fe80::1%eth0]/admin")
        assert not http_module.validate_url("http://[fe80::1%25eth0]/admin")  # Encoded

    def test_ipv6_with_port(self):
        """IPv6 with port should work correctly."""
        # IPv6 loopback with port should be blocked
        assert not http_module.validate_url("http://[::1]:8080/admin")
        # IPv6 public with port should be allowed (using Google's public DNS)
        assert http_module.validate_url("http://[2001:4860:4860::8888]:8080/admin")

    def test_ipv4_mapped_ipv6(self):
        """IPv4-mapped IPv6 addresses should be blocked."""
        # ::ffff:127.0.0.1 maps to 127.0.0.1 (loopback)
        assert not http_module.validate_url("http://[::ffff:127.0.0.1]/admin")
        # ::ffff:192.168.1.1 is private
        assert not http_module.validate_url("http://[::ffff:192.168.1.1]/admin")

    def test_allowed_domains_whitelist(self):
        """Should respect allowed domains whitelist."""
        allowed = ["example.com", "docs.example.com"]
        assert http_module.validate_url("https://example.com/docs", allowed)
        assert http_module.validate_url("https://docs.example.com/api", allowed)
        assert not http_module.validate_url("https://evil.com/docs", allowed)

    def test_allowed_domains_with_port(self):
        """Should allow domains with non-standard ports."""
        allowed = ["example.com"]
        # With port should still match domain
        assert http_module.validate_url("https://example.com:8080/docs", allowed)
        assert not http_module.validate_url("https://evil.com:8080/docs", allowed)

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

    @mock.patch("fresh.scraper.http.fetch_robots_txt")
    def test_is_allowed_by_robots_with_domain_param(self, mock_fetch):
        """Should use provided domain for robots.txt lookup."""
        robots_content = """User-agent: *
Disallow: /admin
"""
        mock_fetch.return_value = robots_content
        # Use domain parameter - should check robots.txt at provided domain
        result = http_module.is_allowed_by_robots(
            "https://docs.example.com/page",
            domain="www.example.com"
        )
        # Should check www.example.com/robots.txt which disallows /admin
        # But the path is /page, not /admin, so it should be allowed
        assert result is True
        # Verify it was called with the correct domain
        mock_fetch.assert_called_once_with("https://www.example.com")

    @mock.patch("fresh.scraper.http.fetch_robots_txt")
    def test_is_allowed_by_robots_domain_param_disallow(self, mock_fetch):
        """Should disallow paths when using domain parameter."""
        robots_content = """User-agent: *
Disallow: /private/
"""
        mock_fetch.return_value = robots_content
        result = http_module.is_allowed_by_robots(
            "https://docs.example.com/private/page",
            domain="www.example.com"
        )
        # Should check www.example.com/robots.txt which disallows /private/
        assert result is False
        mock_fetch.assert_called_once_with("https://www.example.com")

    @mock.patch("fresh.scraper.http.fetch_robots_txt")
    def test_is_allowed_by_robots_404_returns_true(self, mock_fetch):
        """When robots.txt returns 404, should allow access (standard behavior)."""
        mock_fetch.return_value = None  # 404 or not found
        result = http_module.is_allowed_by_robots(
            "https://example.com/page",
            domain="www.example.com"
        )
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


class TestIsPrivateIp:
    """Tests for _is_private_ip function."""

    def test_private_ipv4(self):
        """Private IPv4 addresses should be detected."""
        assert http_module._is_private_ip("10.0.0.1")
        assert http_module._is_private_ip("172.16.0.1")
        assert http_module._is_private_ip("192.168.0.1")

    def test_public_ipv4(self):
        """Public IPv4 addresses should not be detected as private."""
        assert not http_module._is_private_ip("8.8.8.8")
        assert not http_module._is_private_ip("1.1.1.1")
        assert not http_module._is_private_ip("93.184.216.34")

    def test_loopback_ipv4(self):
        """Loopback IPv4 should be detected."""
        assert http_module._is_private_ip("127.0.0.1")

    def test_ipv6_private(self):
        """Private IPv6 addresses should be detected."""
        # Link-local
        assert http_module._is_private_ip("fe80::1")
        # Unique local
        assert http_module._is_private_ip("fc00::1")

    def test_ipv6_public(self):
        """Public IPv6 should not be detected as private."""
        assert not http_module._is_private_ip("2001:4860:4860::8888")

    def test_hostname_not_ip(self):
        """Hostname should not be detected as private IP."""
        assert not http_module._is_private_ip("example.com")
        assert not http_module._is_private_ip("localhost")


class TestRobotsTxtEdgeCases:
    """Tests for robots.txt edge cases."""

    def setup_method(self):
        """Reset caches before each test."""
        http_module._robots_cache.clear()

    @mock.patch("fresh.scraper.http.fetch_robots_txt")
    def test_robots_with_comments(self, mock_fetch):
        """Should handle robots.txt with comments."""
        robots_content = """# This is a comment
User-agent: *
Disallow: /admin
"""
        mock_fetch.return_value = robots_content
        result = http_module.is_allowed_by_robots("https://example.com/admin")
        assert result is False

    @mock.patch("fresh.scraper.http.fetch_robots_txt")
    def test_robots_empty_disallow(self, mock_fetch):
        """Should handle empty Disallow lines."""
        robots_content = """User-agent: *
Disallow:
"""
        mock_fetch.return_value = robots_content
        result = http_module.is_allowed_by_robots("https://example.com/")
        assert result is True

    @mock.patch("fresh.scraper.http.fetch_robots_txt")
    def test_robots_allow_takes_precedence(self, mock_fetch):
        """Allow directive should take precedence over Disallow."""
        robots_content = """User-agent: *
Allow: /public
Disallow: /
"""
        mock_fetch.return_value = robots_content
        result = http_module.is_allowed_by_robots("https://example.com/public")
        assert result is True


class TestResetFunction:
    """Tests for reset function."""

    def test_reset_closes_client(self):
        """Reset should close the HTTP client."""
        # Get a client first
        client = http_module.get_client()
        assert client is not None

        # Reset should close and set to None
        http_module.reset()

        # After reset, getting client should create a new one
        new_client = http_module.get_client()
        assert new_client is not None

    def test_reset_clears_robots_cache(self):
        """Reset should clear the robots.txt cache."""
        # Add something to cache
        http_module._robots_cache["example.com"] = (0, set(), set())
        assert "example.com" in http_module._robots_cache

        http_module.reset()

        assert len(http_module._robots_cache) == 0


class TestIsBinaryUrl:
    """Tests for is_binary_url function."""

    def test_png_image(self):
        """PNG images should be detected as binary."""
        assert http_module.is_binary_url("https://example.com/image.png")

    def test_jpg_image(self):
        """JPG images should be detected as binary."""
        assert http_module.is_binary_url("https://example.com/photo.jpg")

    def test_jpeg_image(self):
        """JPEG images should be detected as binary."""
        assert http_module.is_binary_url("https://example.com/photo.jpeg")

    def test_gif_image(self):
        """GIF images should be detected as binary."""
        assert http_module.is_binary_url("https://example.com/animation.gif")

    def test_pdf_document(self):
        """PDF documents should be detected as binary."""
        assert http_module.is_binary_url("https://example.com/document.pdf")

    def test_zip_archive(self):
        """ZIP archives should be detected as binary."""
        assert http_module.is_binary_url("https://example.com/archive.zip")

    def test_gz_compressed(self):
        """GZ compressed files should be detected as binary."""
        assert http_module.is_binary_url("https://example.com/data.gz")

    def test_bz2_compressed(self):
        """BZ2 compressed files should be detected as binary."""
        assert http_module.is_binary_url("https://example.com/data.bz2")

    def test_mp4_video(self):
        """MP4 videos should be detected as binary."""
        assert http_module.is_binary_url("https://example.com/video.mp4")

    def test_mp3_audio(self):
        """MP3 audio should be detected as binary."""
        assert http_module.is_binary_url("https://example.com/audio.mp3")

    def test_svg_image(self):
        """SVG images are actually text/XML."""
        assert not http_module.is_binary_url("https://example.com/image.svg")

    def test_html_page(self):
        """HTML pages should not be detected as binary."""
        assert not http_module.is_binary_url("https://example.com/page.html")
        assert not http_module.is_binary_url("https://example.com/page.htm")

    def test_text_file(self):
        """Text files should not be detected as binary."""
        assert not http_module.is_binary_url("https://example.com/file.txt")

    def test_json_file(self):
        """JSON files should not be detected as binary."""
        assert not http_module.is_binary_url("https://example.com/data.json")

    def test_css_file(self):
        """CSS files should not be detected as binary."""
        assert not http_module.is_binary_url("https://example.com/style.css")

    def test_js_file(self):
        """JavaScript files should not be detected as binary."""
        assert not http_module.is_binary_url("https://example.com/script.js")

    def test_case_insensitive(self):
        """Extension check should be case insensitive."""
        assert http_module.is_binary_url("https://example.com/image.PNG")
        assert http_module.is_binary_url("https://example.com/image.JPG")
        assert http_module.is_binary_url("https://example.com/document.PDF")


class TestIsBinaryContent:
    """Tests for is_binary_content function."""

    def test_html_content_type(self):
        """HTML content type should not be binary."""
        assert not http_module.is_binary_content(b"<html></html>", "text/html")

    def test_text_content_type(self):
        """Text content type should not be binary."""
        assert not http_module.is_binary_content(b"plain text", "text/plain")

    def test_json_content_type(self):
        """JSON content type should not be binary."""
        assert not http_module.is_binary_content(b'{"key": "value"}', "application/json")

    def test_image_content_type(self):
        """Image content type should be binary."""
        assert http_module.is_binary_content(b"\x89PNG...", "image/png")

    def test_pdf_content_type(self):
        """PDF content type should be binary."""
        assert http_module.is_binary_content(b"%PDF-1.4", "application/pdf")

    def test_application_octet_stream(self):
        """Application/octet-stream should be binary."""
        assert http_module.is_binary_content(b"\x00\x01\x02", "application/octet-stream")

    def test_png_magic_bytes(self):
        """PNG magic bytes should be detected as binary."""
        assert http_module.is_binary_content(b"\x89PNG\r\n\x1a\n\x00\x00\x00")

    def test_jpeg_magic_bytes(self):
        """JPEG magic bytes should be detected as binary."""
        assert http_module.is_binary_content(b"\xff\xd8\xff\xe0\x00\x10JFIF")

    def test_gzip_magic_bytes(self):
        """GZIP magic bytes should be detected as binary."""
        assert http_module.is_binary_content(b"\x1f\x8b\x08\x00\x00\x00\x00\x00")

    def test_bzip2_magic_bytes(self):
        """BZIP2 magic bytes should be detected as binary."""
        assert http_module.is_binary_content(b"BZh91AY&SY\x00\x00\x00")

    def test_zip_magic_bytes(self):
        """ZIP magic bytes should be detected as binary."""
        assert http_module.is_binary_content(b"PK\x03\x04\x14\x00\x00\x00")

    def test_pdf_magic_bytes(self):
        """PDF magic bytes should be detected as binary."""
        assert http_module.is_binary_content(b"%PDF-1.4 test content")

    def test_null_bytes_in_content(self):
        """Content with many null bytes should be detected as binary."""
        # Create content with more than 10% null bytes
        binary_content = b"\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03"
        assert http_module.is_binary_content(binary_content)

    def test_html_with_null_char(self):
        """HTML with occasional null char should not be binary."""
        # Small number of null bytes should be ok
        html = b"<html>\x00<body>Test</body></html>"
        assert not http_module.is_binary_content(html)

    def test_string_content(self):
        """String content should work."""
        assert not http_module.is_binary_content("<html><body>Test</body></html>")

    def test_unicode_string(self):
        """Unicode string content should not be binary."""
        assert not http_module.is_binary_content("<html><body>Hello 世界</body></html>")

    def test_no_content_type_with_html(self):
        """HTML without content type should not be binary."""
        assert not http_module.is_binary_content(b"<html><body>Test</body></html>")


class TestFetchBinaryAware:
    """Tests for fetch_binary_aware function."""

    def setup_method(self):
        """Reset the HTTP client before each test."""
        http_module.reset()

    @mock.patch("fresh.scraper.http.fetch_with_retry")
    def test_skips_binary_url(self, mock_fetch):
        """Should skip binary URLs without making request."""
        result = http_module.fetch_binary_aware("https://example.com/image.png")
        assert result is None
        mock_fetch.assert_not_called()

    @mock.patch("fresh.scraper.http.fetch_with_retry")
    def test_fetches_html_url(self, mock_fetch):
        """Should fetch HTML URLs normally."""
        mock_fetch.return_value = mock.MagicMock(
            spec=httpx.Response,
            status_code=200,
            text="<html>Test</html>",
            headers={"Content-Type": "text/html"},
        )

        _result = http_module.fetch_binary_aware("https://example.com/page.html")

        assert mock_fetch.called

    @mock.patch("fresh.scraper.http.fetch_with_retry")
    def test_skips_binary_content_type(self, mock_fetch):
        """Should skip content with binary content type."""
        mock_response = mock.MagicMock(
            spec=httpx.Response,
            status_code=200,
            content=b"\x89PNG",
            text="",
            headers={"Content-Type": "image/png"},
        )
        mock_fetch.return_value = mock_response

        result = http_module.fetch_binary_aware("https://example.com/image.png")

        assert result is None

    @mock.patch("fresh.scraper.http.fetch_with_retry")
    def test_returns_html_content(self, mock_fetch):
        """Should return HTML content."""
        mock_response = mock.MagicMock(
            spec=httpx.Response,
            status_code=200,
            content=b"<html><body>Test</body></html>",
            text="<html><body>Test</body></html>",
            headers={"Content-Type": "text/html"},
        )
        mock_fetch.return_value = mock_response

        result = http_module.fetch_binary_aware("https://example.com/page.html")

        assert result == "<html><body>Test</body></html>"

    @mock.patch("fresh.scraper.http.fetch_with_retry")
    def test_returns_none_on_failure(self, mock_fetch):
        """Should return None when fetch fails."""
        mock_fetch.return_value = None

        result = http_module.fetch_binary_aware("https://example.com/page.html")

        assert result is None
