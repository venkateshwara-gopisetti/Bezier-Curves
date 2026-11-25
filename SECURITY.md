# Security policy

## Supported versions

Security fixes go into the latest release only.

## Reporting a vulnerability

Please **don't open a public issue** for security problems. Report them privately through GitHub instead: on the repository's **Security** tab, choose **Report a vulnerability** ([direct link](https://github.com/venkateshwara-gopisetti/Bezier-Curves/security/advisories/new)).

Please include what you found, how to reproduce it, and which version you used. You should get a reply within a week. Once a fix is released, you'll be credited in the advisory unless you'd rather stay anonymous.

beziervis makes no network requests and runs no code from its inputs. The most likely issues are in file writing (`save()`) or in dependencies.
