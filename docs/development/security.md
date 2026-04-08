# Security

## Reporting vulnerabilities

Please **do not** open public issues for undisclosed security vulnerabilities.

**Preferred:** use [GitHub **Security advisories**](https://github.com/DevStrikerTech/oris/security/advisories) for a private report.

**Full policy:** [`SECURITY.md` on GitHub](https://github.com/DevStrikerTech/oris/blob/dev/SECURITY.md) (supported versions, secret handling, coordinated disclosure expectations).

## Guidelines (summary)

- Never commit **secrets**; use environment variables or a secret manager.  
- Provider YAML uses **`api_key_env`** to name variables—never embed key material.  
- Configuration is loaded with **`yaml.safe_load`** only.

## Next

- [**Contributing**](contributing.md)  
- [**Code of Conduct**](code-of-conduct.md)  
