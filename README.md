# reddit postcards and advertising plugin

This plugin adds a couple pages to reddit - a postcards page and an 
advertising page.

## installation

First, install the python package:

    python ./setup.py develop

To enable the plugin, you will need to add it to the plugins line of your
reddit .ini file:

    plugins = about

To build static files for production, run `make` in the main reddit repository.
It will detect, build, and merge in the plugin static files for deployment.
