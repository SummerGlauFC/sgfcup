sgfcup
======
New codebase for the SGFC file uploader.

Dependencies
------------
* bottle (dev version): https://github.com/bottlepy/bottle
* cymysql
* jinja2
* python-magic (need libmagic on your system)
* pillow
* pygments
* jsonmerge
* bottle-beaker
* beaker
* ghdiff
* tornado (for serving the app)

Install these if you are using a version of Python below 3.4:
* enum34
* future (for python2/3 compatibility)

Dependencies for Python >= 3.4 can be installed via:

    pip install git+https://github.com/bottlepy/bottle.git cymysql jinja2 python-magic pillow pygments jsonmerge tornado bottle-beaker beaker ghdiff

Dependencies for Python < 3.4 can be installed via:

    pip install git+https://github.com/bottlepy/bottle.git cymysql jinja2 python-magic pillow pygments jsonmerge tornado bottle-beaker beaker ghdiff enum34 future

Please edit `project/config.example.py`, and rename it to `config.py`,
then run `database.sql` on the database you've put in `config.py`.

The directories `img/p/` and `img/t/` have to be created in the root of the project.


Running the app
---------------
The program is run like so:

    python runserver.py <port>


Notes
-----
The app also has the ability to serve a file through [nginx's X-Accel](https://www.nginx.com/resources/wiki/start/topics/examples/x-accel/). To use this, nginx must have a location block for `/get_image/`, like so:

    location /get_image/ {
        internal;
        alias /path/to/project/img/; # note the trailing slash
    }

Then in `project/config.py`:

    {
        "use_nginx_sendfile": False,
        ...
    }


LICENSE
-------
        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

    Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

    Everyone is permitted to copy and distribute verbatim or modified
    copies of this license document, and changing it is allowed as long
    as the name is changed.

                DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
        TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

    0. You just DO WHAT THE FUCK YOU WANT TO.

