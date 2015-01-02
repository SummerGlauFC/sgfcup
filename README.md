sgfcup
======

New codebase for the SGFC file uploader.

### Dependencies:
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

The program is run like so:

    python runserver.py <port>
