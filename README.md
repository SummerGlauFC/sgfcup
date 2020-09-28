# sgfcup

New codebase for the SGFC file uploader.

## Dependencies

Requires Python >= 3.6

Dependencies can be installed using [Poetry](https://python-poetry.org):

    poetry install

## Setup

Please edit `project/config.example.py`, and rename it to `config.py`, then run `database.sql` on the database you've
put in `config.py`.

The specified directories for images and thumbnails must exist, as they will not be automatically created.

# Running the app

The program is run like so:

    python runserver.py <port>

## Notes

The app also has the ability to serve a file
through [nginx's X-Accel](https://www.nginx.com/resources/wiki/start/topics/examples/x-accel/). To use this, nginx must
have a location block for `/get_image/`, like so:

    location /get_image/ {
        internal;
        
        # keep the trailing slash!
        alias /path/to/base/image/directory/; 
        
        # this may need to be customised based on your
        # chosen directory structure.
    }

Then in `project/config.py`:

    {
        "use_nginx_sendfile": True,
        ...
    }

## LICENSE

        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

    Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

    Everyone is permitted to copy and distribute verbatim or modified
    copies of this license document, and changing it is allowed as long
    as the name is changed.

                DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
        TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

    0. You just DO WHAT THE FUCK YOU WANT TO.
