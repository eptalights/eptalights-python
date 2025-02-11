# eptalights-python

The **Eptalights Python Library** is a powerful Python package designed to help hackers, researchers, and developers effortlessly perform code analysis, discover bugs, conduct variant analysis, and more.

Easily access functions, callsites, variables, control flow graphs (CFG), and other code elements in a simple, Pythonic way. Think of it as Binary Ninja but for source code.

## Documentation

For detailed documentation, please visit [Eptalights Documentation](https://eptalights.readthedocs.io/).

You can also check out this [blog post](https://eptalights.com/blog/01-introduction-to-eptalights-technology/) for an introduction to Eptalights Technology.

## Supported Languages

Eptalights currently supports the following languages, with more on the way:

- **C/C++** (via [GCC GIMPLE](https://github.com/eptalights/gimple-extractor))
- **PHP** (via [PHP Opcode](#))

## Installation

install the Python package eptalights with the recommended method via pip:
```
pip install eptalights
```

Alternatively, if you are interested in the latest functionality not yet released through pip, you may clone the code from GitHub and build from source (git assumed to be available):

```
pip install git+https://github.com/eptalights/eptalights-python.git
```

## Setting up a Development Environment

The latest code under development is available on GitHub at https://github.com/eptalights/eptalights-python.
To obtain this version for experimental features or for development:

```bash
git clone https://github.com/eptalights/eptalights-python.git
cd eptalights-python
pip install -e ".[dev]"
```

To run tests and styling checks:

```bash
pytest
flake8 src tests
black --check src tests
```

## Building Documentation

We use the Sphinx framework. The documentation source files are in `docs/`.
The public documentation is accessible at https://eptalights.readthedocs.io.
The doc build is configured by `.readthedocs.yaml`. 

To build the documentation locally (for testing and development),
install the full doc-related dependencies: `pip install -r docs/requirements.txt`,
then run `sphinx-build -b html docs/ docs/build/`.

## Contributing

See `CONTRIBUTING.md` for information about contributing to this project.

## License

See `LICENSE` for details.
