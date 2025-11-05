# Security Policy

## Supported Versions

We actively maintain and provide security updates for the following versions:

| Version | Supported          | Status                                        |
| ------- | ------------------ | --------------------------------------------- |
| 1.x.x   | :white_check_mark: | Active development, receives security updates |
| < 1.0   | :x:                | Pre-release, no security support              |

## Security Update Policy

- **Critical vulnerabilities**: Patched within 24-48 hours
- **High-severity vulnerabilities**: Patched within 7 days
- **Medium/Low vulnerabilities**: Addressed in the next scheduled release

Security patches are released as patch versions (e.g., 1.0.1 → 1.0.2) and applied to all supported major versions.

## Reporting a Vulnerability

We take security vulnerabilities seriously and appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, report security vulnerabilities via email to:

📧 **bibhumohanty034@gmail.com**

### What to Include

Please include the following information in your report:

- **Description**: A clear description of the vulnerability
- **Impact**: Potential impact and severity assessment
- **Steps to Reproduce**: Detailed steps to reproduce the vulnerability
- **Proof of Concept**: Code or commands demonstrating the issue (if applicable)
- **Affected Versions**: Which versions are affected
- **Suggested Fix**: Any recommendations for remediation (optional)
- **Your Contact Information**: So we can follow up with questions

### Response Timeline

- **Initial Response**: Within 48 hours of receipt
- **Status Updates**: Every 3-5 days until resolved
- **Resolution**: Timeline depends on severity (see Security Update Policy)

### Disclosure Policy

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will provide regular updates on our progress
- We will notify you when the vulnerability is fixed
- We ask that you do not publicly disclose the vulnerability until we have released a patch
- We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices for Users

### Environment Variables

- Never commit `.env` files or secrets to version control
- Use strong, unique passwords for all services
- Rotate secrets regularly (at least every 90 days)

### Dependencies

- Keep dependencies up to date using Dependabot alerts
- Review and merge security updates promptly
- Run `pip-audit` regularly to check for known vulnerabilities

### Database Security

- Use strong PostgreSQL passwords (minimum 16 characters, mixed case + symbols)
- Enable SSL/TLS for database connections in production
- Restrict database access to application servers only
- Enable PostgreSQL audit logging for compliance

### API Security

- Use HTTPS in production (enforced via Caddy reverse proxy)
- Implement rate limiting for API endpoints
- Enable CORS only for trusted domains
- Use JWT tokens with short expiration times (15-60 minutes)
- Store refresh tokens securely and rotate them regularly

### Container Security

- Keep base images updated (use Watchtower for automated updates)
- Run containers as non-root users
- Scan images for vulnerabilities with `docker scan` or Trivy
- Use specific image tags (avoid `:latest` in production)

### Deployment Security

- Use GitHub Environments with required reviewers for production
- Enable branch protection rules on `main` branch
- Use SSH keys instead of passwords for server access
- Regularly rotate SSH keys and GitHub tokens
- Enable audit logging for all deployment activities

## Known Security Considerations

### JWT Authentication

- Tokens are stateless; revocation requires additional infrastructure (Redis/database)
- Token expiration is set to 30 minutes by default
- Consider implementing refresh token rotation for enhanced security

### Database Migrations

- Alembic migrations run with full database privileges
- Review all migrations before applying to production
- Test migrations on staging environment first

### Dependencies

- We use `pip-audit` and Dependabot to monitor for vulnerabilities
- Security updates are applied automatically when possible
- Breaking changes are evaluated before merging dependency updates

## Security Tooling

This project uses the following security tools in CI/CD:

- **Bandit**: Static analysis for Python security issues
- **pip-audit**: Vulnerability scanning for Python dependencies
- **Dependabot**: Automated dependency updates
- **GitHub Code Scanning**: Automated security analysis (if enabled)
- **Docker Scan**: Container image vulnerability scanning

## Compliance

This project follows security best practices including:

- OWASP Top 10 protection
- SQL injection prevention (via SQLAlchemy parameterized queries)
- XSS protection (via FastAPI automatic escaping)
- CSRF protection (for stateful operations)
- Rate limiting (configurable)
- Security headers (via Caddy reverse proxy)

## Contact

For security-related questions or concerns, contact:

📧 bibhumohanty034@gmail.com

For general issues or feature requests, please use GitHub Issues.

---

**Last Updated**: November 6, 2025
