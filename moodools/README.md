# Moodools package

A package containing small utilities useful for Odoo modules development.

## List of utilities

### deps

Create a directed graph of modules dependencies.
This tool only takes into account packages inside
one directory (and it's subdirs) to avoid bloated
diagrams, this means that dependencies thoward packages
in other directories are intentionally **NOT** included in the diagram.

Use the *-h* option to obtain the usage help:

```bash
python -m moodles.deps -h
```