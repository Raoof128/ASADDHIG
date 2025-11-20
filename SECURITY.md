# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Considerations

### Data Sovereignty

This gateway is designed to enforce Australian data sovereignty by routing sensitive prompts to local LLMs. However, users must:

- **Never** send classified or highly sensitive data through this gateway without proper authorization
- **Verify** that local LLM models meet your organization's security requirements
- **Audit** all routing decisions through the compliance logs
- **Configure** appropriate PII thresholds for your use case

### API Security

#### Current Implementation

- **CORS**: Currently allows all origins (`*`) - **MUST be restricted in production**
- **Authentication**: Not implemented - **MUST be added for production**
- **Rate Limiting**: Not implemented - **RECOMMENDED for production**
- **Input Validation**: Basic validation via Pydantic models
- **Request Size Limits**: Not enforced - **RECOMMENDED for production**

#### Production Hardening Checklist

- [ ] Implement authentication (API keys, OAuth2, JWT)
- [ ] Restrict CORS to specific origins
- [ ] Add rate limiting (e.g., using `slowapi`)
- [ ] Enforce request size limits
- [ ] Enable HTTPS/TLS
- [ ] Implement request signing/verification
- [ ] Add IP whitelisting (if applicable)
- [ ] Set up WAF (Web Application Firewall)
- [ ] Regular security audits

### Secrets Management

**NEVER** commit secrets to the repository:

- OpenAI API keys
- Database credentials
- JWT secrets
- Other sensitive configuration

Use environment variables or secrets management systems:
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes Secrets
- Docker Secrets

### Audit Logging

- Audit logs contain metadata but **NOT** prompt content (privacy-preserving)
- Logs are stored in `sovereign_audit.log` (ensure proper access controls)
- In production, consider:
  - Encrypting logs at rest
  - Shipping logs to secure SIEM
  - Setting log retention policies
  - Restricting log access

### Docker Security

- Use official base images
- Keep images updated
- Run containers as non-root user (if possible)
- Use read-only filesystems where applicable
- Scan images for vulnerabilities

### Network Security

- Use Docker networks for service isolation
- Restrict external access to services
- Use reverse proxy (nginx, traefik) for production
- Implement network policies (Kubernetes)

## Reporting a Vulnerability

### How to Report

If you discover a security vulnerability, please **DO NOT** open a public issue. Instead:

1. **Email** security concerns to: [security@example.com] (replace with actual contact)
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity

### Severity Levels

- **Critical**: Immediate action required (data breach, RCE)
- **High**: Fix within 7 days (authentication bypass, privilege escalation)
- **Medium**: Fix within 30 days (information disclosure, DoS)
- **Low**: Fix in next release (minor issues, best practices)

## Security Best Practices for Users

### Deployment

1. **Never** expose services directly to the internet without authentication
2. **Use** reverse proxy with TLS termination
3. **Restrict** network access using firewalls
4. **Monitor** logs for suspicious activity
5. **Keep** all dependencies updated

### Configuration

1. **Set** appropriate PII thresholds
2. **Configure** CORS for your specific origins
3. **Use** strong API keys/secrets
4. **Enable** audit logging
5. **Review** audit logs regularly

### Local LLM Security

1. **Verify** model sources and integrity
2. **Keep** Ollama and models updated
3. **Restrict** Ollama API access
4. **Monitor** model behavior
5. **Consider** model fine-tuning for your use case

## Known Limitations

### Current Security Gaps

1. **No Authentication**: API endpoints are unauthenticated
2. **Open CORS**: Allows all origins
3. **No Rate Limiting**: Vulnerable to abuse
4. **No Request Size Limits**: Potential DoS vector
5. **Basic Input Validation**: May need enhancement

### Planned Improvements

- [ ] OAuth2/JWT authentication
- [ ] Rate limiting middleware
- [ ] Request size limits
- [ ] Enhanced input validation
- [ ] Security headers (HSTS, CSP, etc.)
- [ ] Request signing
- [ ] IP whitelisting

## Compliance

This gateway is designed to support:
- **ISO 27001** - Information Security Management
- **ASD Essential 8** - Australian Cyber Security Centre guidelines
- **Privacy Act 1988** - Australian privacy legislation
- **APRA CPS 234** - Information Security (Financial Services)

However, **compliance is the responsibility of the deploying organization**. This tool provides mechanisms (audit logging, routing decisions) but does not guarantee compliance on its own.

## Security Updates

Security updates will be:
- Released as patch versions (1.0.x)
- Documented in CHANGELOG.md
- Announced via GitHub releases
- Tagged with security labels

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [ASD Essential 8](https://www.cyber.gov.au/acsc/view-all-content/essential-eight)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**Remember**: Security is a shared responsibility. Report vulnerabilities responsibly, and help us keep the Sovereign AI Gateway secure for all users.

