# Security Policy

## 🛡️ Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | ✅ Yes            |
| 0.2.x   | ⚠️ Limited        |
| 0.1.x   | ❌ No             |

## 🚨 Reporting a Vulnerability

**Please DO NOT report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in ASURA, please report it responsibly:

### 📧 Reporting Process

1. **Email**: Send details to `parth.ajit7052@gmail.com` (preferred)
   - Alternatively, create a private security advisory on GitHub

2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)
   - Your contact information

3. **Response Time**:
   - Initial acknowledgment: Within 48 hours
   - Status update: Within 7 days
   - Fix timeline: Depends on severity

### 🎯 Severity Levels

We classify vulnerabilities using the following severity levels:

- **Critical**: Immediate attention required (RCE, authentication bypass)
- **High**: Significant risk (SQL injection, XSS, data leakage)
- **Medium**: Moderate risk (CSRF, information disclosure)
- **Low**: Minor risk (minor information leakage)

### 🏆 Responsible Disclosure

We follow coordinated vulnerability disclosure:

1. **Report received**: We acknowledge your report
2. **Investigation**: We verify and assess the vulnerability
3. **Fix development**: We develop and test a fix
4. **Disclosure**: We coordinate public disclosure timing with you
5. **Recognition**: We credit you in the release notes (if desired)

## 🔒 Security Best Practices for Users

### Installation

- Always download ASURA from official sources (GitHub releases)
- Verify checksums when available
- Use virtual environments for Python dependencies

### Configuration

- **Never commit `.env` files** containing API keys
- **Never commit `AsuraDevKey.txt`** or similar sensitive files
- Use strong, unique API keys
- Regularly rotate API keys
- Keep ASURA updated to the latest version

### API Keys

- Store API keys securely in `.env` files
- Never hardcode API keys in source code
- Use environment-specific keys (dev, prod)
- Revoke unused API keys immediately

### Project Scanning

- Only scan code you own or have permission to scan
- Be cautious when scanning projects with sensitive data
- Review scan logs before sharing them
- Delete old scan logs containing sensitive information

### Network Security

- ASURA runs locally by default (good!)
- If exposing the API, use HTTPS
- Implement authentication if multi-user
- Use firewall rules to restrict access

## 🔐 ASURA Security Features

### Privacy First

- ✅ **Local execution**: All scans run on your machine
- ✅ **No telemetry**: We don't collect usage data
- ✅ **Offline capable**: Core features work without internet
- ✅ **Open source**: Full code transparency

### Optional AI Features

- ⚠️ **AI is optional**: Core scanning works without AI
- ⚠️ **Network calls**: AI features require internet
- ⚠️ **Data transmission**: Vulnerability details sent to AI API
- ✅ **Redaction**: Sensitive data should be redacted before AI analysis

### Data Storage

- ✅ **Local database**: SQLite stored on your machine
- ✅ **No cloud sync**: Data never leaves your computer
- ✅ **User control**: You own and control all data

## 🛠️ Security Hardening

### For Production Deployments

If you deploy ASURA for team use:

1. **Use HTTPS**: Never use HTTP in production
2. **Add authentication**: Implement user authentication
3. **Rate limiting**: Already implemented (60 req/min)
4. **Input validation**: Already implemented for paths
5. **Regular updates**: Keep dependencies updated
6. **Secure database**: Set proper file permissions on `asura.db`
7. **Log monitoring**: Review logs regularly
8. **Backup data**: Regular database backups

### Environment Variables

```bash
# Use strong secrets in production
SECRET_KEY=<generate-random-32-char-string>

# Restrict CORS origins
CORS_ORIGINS=https://your-domain.com

# Set appropriate log level
LOG_LEVEL=WARNING  # or ERROR in production
```

## 🧪 Security Testing

We welcome security testing of ASURA:

- ✅ **Allowed**: Testing on your own ASURA instance
- ✅ **Allowed**: Reporting vulnerabilities responsibly
- ❌ **Not allowed**: Testing on others' instances without permission
- ❌ **Not allowed**: Public disclosure before coordination

### Self-Assessment

Run security scanners on ASURA itself:

```bash
# Scan ASURA backend
cd backend
python -m bandit -r app/ -f json
 
# Check dependencies
python -m safety check --file requirements.txt
```

### Running Asura on Itself

ASURA practices what it preaches by running its own security scanners on its own codebase. This self-scanning process ensures we maintain high security standards.

**To scan Asura with Asura:**

```bash
# 1. Start the Asura application
start.bat  # Windows
# or
./start.sh  # Linux/Mac

# 2. Access the web UI at http://localhost:5173

# 3. Create a project pointing to Asura's backend:
#    Name: "Asura Self-Scan"
#    Path: C:\path\to\Asura\backend  (use absolute path)

# 4. Run a security scan

# 5. Review results - expect mostly LOW severity findings
```

**Understanding Self-Scan Results:**

When you scan Asura with itself, you'll see:

1. **B101 (Assert in Tests)**: ~67 occurrences - **FALSE POSITIVES**
   - These are in test files (`tests/`)
   - Using `assert` in tests is standard pytest practice
   - Safe to ignore - already suppressed in `.bandit` config
   
2. **B603/B404 (Subprocess Usage)**: ~15 occurrences - **SAFE**
   - All subprocess calls use controlled inputs:
     - `sys.executable` (Python interpreter path)
     - Hardcoded tool names (bandit, safety, semgrep)
     - Validated file paths from path_validator.py
   - No `shell=True` usage
   - No user-controllable input reaches subprocess calls
   - See inline `# nosec B603` comments for justification

3. **B110 (Try/Except/Pass)**: 2 occurrences - **FIXED**
   - Updated to use proper logging instead of silent failures
   - See [SECURITY_AUDIT.md](SECURITY_AUDIT.md) for details

**Overall Security Posture**:
- ✅ No CRITICAL or HIGH severity issues
- ✅ No SQL injection vulnerabilities (uses SQLAlchemy ORM)
- ✅ No XSS vulnerabilities (CSP headers implemented)
- ✅ All subprocess usage is safe and documented
- ✅ Input validation implemented for file paths

For detailed analysis of Asura's self-scan, see [docs/SECURITY_AUDIT.md](SECURITY_AUDIT.md)

### Self-Assessment (Deprecated - Use "Running Asura on Itself" above)

Run security scanners on ASURA itself:

```bash
# Scan ASURA backend (with Bandit configuration)
cd backend
python -m bandit -r app/ -c ../.bandit -f json

# Check dependencies
python -m safety check --file requirements.txt
```

**Note**: The `.bandit` configuration file suppresses false positives for test files while maintaining security checks

## 📚 Security Resources

### OWASP Top 10 Coverage

ASURA's scanners detect:
1. Injection (SQL, Command)
2. Broken Authentication
3. Sensitive Data Exposure
4. XML External Entities (XXE)
5. Broken Access Control
6. Security Misconfiguration
7. Cross-Site Scripting (XSS)
8. Insecure Deserialization
9. Using Components with Known Vulnerabilities
10. Insufficient Logging & Monitoring

### Security Scanner Documentation

- [Bandit](https://bandit.readthedocs.io/)
- [Safety](https://pyup.io/safety/)
- [Semgrep](https://semgrep.dev/docs/)

## 🤝 Security Contributors

We maintain a list of security contributors:

- [List will be maintained here]

Thank you for helping keep ASURA secure!

## 📋 Past Security Advisories

None yet (project launched October 2025)

## 📞 Contact

- **Security Email**: parth.ajit7052@gmail.com
- **General Issues**: [GitHub Issues](https://github.com/ParthSalunkhe7052/Asura-Security-Scan/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ParthSalunkhe7052/Asura-Security-Scan/discussions)

---

**Last Updated**: November 3, 2025
**Version**: 0.3.0
