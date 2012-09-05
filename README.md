# reddit about pages plugin

This plugin adds a series of /about/ pages to reddit containing quotes, photos,
postcards, stats, and the reddit team bios.

## installation

First, install the python package:

    python ./setup.py develop

To enable the plugin, you will need to add it to the plugins line of your
reddit .ini file:

    plugins = about

Finally, configure the plugin in your reddit .ini file:

    # set which subreddits the about page pulls its source data from
    # make sure you create the subreddits as well, otherwise you'll get an error
    about_sr_quotes = about_quotes
    about_sr_images = about_images
    
    # these options place a size limit on the slideshow
    about_images_count = 50
    about_images_min_score = 1

To build static files for production, run `make` in the main reddit repository.
It will detect, build, and merge in the about plugin static files for
deployment.
