# Security Policy

## Supported Versions

The following versions of Fresh are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.7.x   | :white_check_mark: |
| 2.6.x   | :white_check_mark: |
| < 2.6   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to **support@nesalia.com**. This allows us to address the issue before it's publicly disclosed.

When reporting, please include:

1. **Description** - A clear description of the vulnerability
2. **Steps to Reproduce** - Detailed steps to reproduce the issue
3. **Impact** - Potential impact of the vulnerability
4. **Affected Version** - Which versions are affected
5. **Suggested Fix** - If you have one (optional)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depending on severity (see below)

### Severity Classification

| Severity | Response Time | Fix Target |
|----------|---------------|------------|
| Critical | 24 hours      | 7 days     |
| High     | 48 hours      | 14 days    |
| Medium   | 7 days        | 30 days    |
| Low      | 30 days       | Next minor release |

## Security Best Practices

When using Fresh, keep these security considerations in mind:

- **Rate Limiting**: Fresh implements per-domain rate limiting to respect server resources
- **SSRF Protection**: Outgoing requests are validated to prevent Server-Side Request Forgery attacks
- **Robots.txt Compliance**: Fresh respects robots.txt rules by default
- **Binary File Detection**: Automatic detection and skipping of binary files

## Acknowledgments

We appreciate responsible disclosure. Contributors who report security issues will be acknowledged (unless preferred otherwise).

## Updates

This policy may be updated periodically. The latest version will always be available in this file.