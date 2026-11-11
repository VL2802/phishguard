# Security Policy

## Supported versions

Only the latest version on the default branch is supported.

## Reporting a vulnerability

Report suspected vulnerabilities privately through GitHub Security Advisories or
to `[maintainer security contact]`. Do not publish email datasets, personal data,
model files, credentials, exploit details, or other sensitive information in a
public issue.

## Security considerations

- Run the API on localhost unless authentication and rate limiting are added.
- Treat trained model files as trusted local artifacts; `joblib.load` must not be
  used on untrusted files.
- Use only datasets that are appropriately licensed and scrubbed of personal
  information.
- Keep extension assets local and review browser-extension permissions before
  deployment.
- The extension uses system fonts only; it does not contact Google Fonts.
