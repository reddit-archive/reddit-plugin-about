# reddit skeleton plugin

This plugin is a skeleton to give you an idea about where to start when writting plugins
reddit.

This skeleton is based on the the about plugin found here: https://github.com/reddit/reddit-plugin-about
## installation

First, install the python package:

    python ./setup.py develop

To enable the plugin, you will need to add it to the plugins line of your
reddit .ini file:

    plugins = skeleton

Finally, configure the plugin in your reddit .ini file. The settings will depend on what you are looking
for in your code.

To build static files for production, run `make` in the main reddit repository.
It will detect, build, and merge in the about plugin static files for
deployment.
