sgfcup
======
New codebase for the SGFC file uploader.

Dependencies
------------
* bottle (dev version): https://github.com/bottlepy/bottle
* jinja2
* python-magic
* pillow
* pygments
* jsonmerge
* bjoern

Dependencies can be installed via:

    pip install git+https://github.com/bottlepy/bottle.git jinja2 python-magic pillow pygments jsonmerge bjoern
    
Please edit `project/config.example.py`, and rename it to `config.py`,
then run `database.sql` on the database you've put in `config.py`.

The directories `img/p/` and `img/t/` have to be created in the root of the project.


Running the app
---------------
The program is run like so:

    python runserver.py <port>


Notes
-----
The app also has the ability to serve a file through [nginx's XSendfile](http://wiki.nginx.org/XSendfile). To use this, nginx must have a location block for `/get_image/`, like so:
    
    location /get_image/ {
        internal;
        alias /path/to/project/img/p/; # note the trailing slash
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

