# Deploying the OQ3 Python AST

You need:
- permission to push tags to `openqasm/openqasm`
- a reviewer to approve a PR to the branch

Most of the deployment is automated by the GitHub workflows:
- `/.github/workflows/build-ast.yml`
- `/.github/workflows/deploy-ast.yml`
which do what they say on the tin.

The "deploy" workflow uses the organisation-level secret `OPENQASM_BOT_PYPI_TOKEN`, which is an API token for the PyPI user `openqasm-bot` currently owned by Jake Lishman (`jake.lishman@ibm.com`).
PyPI's authorisation policies may need us to change how we handle that in the future, if they bring in some of their proposed changes around API tokens and 2FA.

## Procedure

1. Decide the versions of the ANTLR compiler that should be used to build the ANTLR parser files.
   See the "ANTLR considerations" section below for some notes on this.
   Modify `/source/openqasm/ANTLR_VERSIONS.txt` if you want to add/remove versions.
2. Make a PR to that branch that bumps the version numbers of the Python package to the desired value, if it isn't already.
   At the time of writing, the only place needing to be updated is `/source/openqasm/openqasm3/__init__.py:__version__`; everywhere else pulls that in dynamically.
   You will likely need to add a release note (see also `CONTRIBUTING.md`).
3. Tag the desired commit, most likely the version-bump one, as `ast-py/v<version>`.
   `<version>` must match the Python-package version string exactly (it's a sanity check in the CD pipeline).
   For example, if releasing version `0.5.0`, set the `__init__.py:__version__` attribute to `"0.5.0"`, and make the tag `ast-py/v0.5.0`.
   Pre-release markers (e.g. `0.5.0b1`) should work fine.
   I prefer to PGP sign tags that trigger releases on packages I maintain, but it's not enforced.
4. Push the tag to `github.com/openqasm/openqasm`.
   This triggers the CD and deploys the package to PyPI.


## ANTLR considerations

If we just generated one version of the ANTLR parser, the `openqasm3` Python package would only be compatible with the matching minor version of `antlr4-python3-runtime`.
This causes problems when people want to use our package in conjunction with another ANTLR-generated parsing package, which may have used a different version of ANTLR.
`openqasm3` has a dynamic import system for its ANTLR-generated components that chooses from the versions of those files the one that matches the installed version of `antrl4-python3-runtime`.
The wheel-build action `build-ast.yml` uses the file `/source/openqasm/ANTLR_VERSIONS.txt` to decide which versions of the ANTLR compiler it should use to generate ANTLR files in the wheel.

The Python ANTLR runtime is compatible with all releases of ANTLR that share the same `major.minor` version, and potentially differ in the patch number.
For example, if version 4.11.1 of the ANTLR compiler (the Java bit) was used, the generated files will be compatible with versions 4.11.0, 4.11.1 and 4.11.2 (etc) of `antlr4-python3-runtime`, but versions 4.10.1 or 4.12.0 would not be.

There's little harm in supporting ANTLR as far back as the grammar allows, nor as recent as ANTLR has released; the wider range we allow, the more packages we can coexist with, and the extra weight in the pure-Python wheel from the generated files from a new version is only on the order of 500kB.
The versions need to form a contiguous set of minor releases (e.g. `4.1; 4.2; 4.3` is allowed, but `4.1; 4.3` is not) because Python-packaging requirements mean we need to have a range, not a discrete set.

I approximately tried to have the package be compatible with the ANTLR range `>=4.7,<5`.
The lower bound is somewhat arbitrary assuming it can still handle the grammar - I didn't try to find the breaking point. 
ANTLR 4.6 was already over 5 years old when I first made the dynamic-import system, so I just stopped at 4.7.
