# Security Automation

Automating security vulnerability detection and fixes.

## The Problem

- OWASP Top 10 exists
- CVE database has 200k+ entries
- Best practices are documented

Yet vulnerabilities keep appearing in code.

## Claude Code Security Example

AI-powered security gate that:
- Scans code for vulnerabilities
- Uses AI (not just pattern matching)
- Understands component interactions
- Traces data flow
- Multi-stage verification
- Suggests patches
- Nothing without human approval

## Security Rules (Automatable)

### SQL Injection

```
DETECT:
db.query(`SELECT * FROM users WHERE id = ${userId}`)

SUGGEST:
db.query('SELECT * FROM users WHERE id = $1', [userId])
```

### XSS Prevention

```
DETECT:
element.innerHTML = userInput;

SUGGEST:
element.textContent = userInput; // Safe
// OR:
element.innerHTML = sanitize(userInput);
```

### Hardcoded Secrets

```
DETECT:
const API_KEY = 'sk-1234567890abcdef';

SUGGEST:
const API_KEY = process.env.API_KEY;
```

### Command Injection

```
DETECT:
exec(`ls ${directory}`);

SUGGEST:
execFile('ls', [directory]);
```

## Integration Points

```
1. CLI:
   fresh-security --scan

2. Dependency Scanner:
   npm audit, snyk, dependabot

3. CI/CD:
   Block merge if CVEs found

4. IDE:
   Inline warnings + quick fixes
```

---

*Last updated: 2026-03-04*
