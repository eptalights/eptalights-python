# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'eptalights-code'
copyright = '2025, Eptalights Research'
author = 'Eptalights Research'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
	'sphinx.ext.autodoc',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme' # 
html_static_path = ['_static']

nitpick_ignore = [
	('py:class', 'type'),
]


def skip_member(app, what, name, obj, skip, options):
    if name == "model_config":
        return True
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip_member)
