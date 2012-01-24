# reddit about pages plugin

This plugin adds a series of /about/ pages to reddit containing quotes, photos,
postcards, stats, and the reddit team bios.

## installation

First, install the python package:

    python ./setup.py develop

To build static files for production, run `make` in the main reddit repository.
It will detect, build, and merge in the about plugin static files for
deployment.
