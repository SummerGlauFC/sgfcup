{% macro render_pagination(pagination) %}
    {% if pagination.has_prev %}
        <a href="{{ url_for_page(pagination.page - 1)
          }}" data-page="{{ page }}">&laquo;</a>
    {% endif %}
    {%- for page in pagination.iter_pages() %}
        {% if page %}
            <a href="{{ url_for_page(page) }}" data-page="{{ page }}">
            {% if page != pagination.page %}
                {{ page }}
            {% else %}
                <span style="color: #090910;font-weight: bold !important;">{{ page }}</span>
            {% endif %}
            </a>
        {% else %}
            <a><span style="color: #090910"> .. </span></a>
        {% endif %}
    {%- endfor %}
    {% if pagination.has_next %}
        <a href="{{ url_for_page(pagination.page + 1) }}" data-page="{{ page }}">&raquo;</a>
    {% endif %}
{% endmacro %}
{% macro write_ext(file) %}{% if info.show_ext == 1 %}{{ file.url }}{{ file.ext }}{% elif info.show_ext == 2 %}{{ file.url }}/{{ file.original }}{% else %}{{ file.url }}{% endif %}{% endmacro %}
{% if not error %}
    {% if not info.pjax %}
        <!DOCTYPE html>
        <html>
            <head>
                <link href="data:image/x-icon;base64,AAABAAEAEBAQAAAAAAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAA//36AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAREREREQAAABERERERAAAAAAAAAAAAAAAAABEAAAAAAAABERAAAAAAABEREQAAAAABEREREAAAABERERERAAAAAAEREAAAAAAAAREQAAAAAAABERAAAAAAAAEREAAAAAAAAREQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" rel="icon" type="image/x-icon" />
                <link href='/static/css/style.css' rel='stylesheet' type='text/css'>
                <link href='/static/css/gallery.css' rel='stylesheet' type='text/css'>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>SGFC >> {{ info.key }}'{% if info.key[-1] != "s" %}s{% endif %} Gallery</title>
                <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
                <script src="//browserstate.github.io/history.js/scripts/bundled/html4+html5/jquery.history.js"></script>
            </head>

            <body class="gallery">
                <div id="container">
                    <header>
                        <a href="/">Gallery</a>
                    </header>
                    <div id="main">
    {% endif %}
                        <h2>{{ info.usage }} used ({{ info.entries }} items)</h2>
                        <h2 class="debug pages" style="position:relative;">
                            {{ render_pagination(info.pages) }}
                        </h2>
                        <script>
                            window.current_page = {{ info.pages.page }};
                        </script>
                        <h2 class="debug top">
                            <form class="sorty" action="" method="get" style="display: block;margin-top: 3px;text-align: center;">
                                <select name="sort" id="sort">
                                    {% for mode in info.sort.list %}
                                        <option value="{{ loop.index0 }}" {% if loop.index0 == info.sort.current -%} selected {%- endif %}>
                                            {{ mode[0] }}
                                        </option>
                                    {% endfor %}
                                </select>
                                <input type="submit" value="Sort" />

                                <div style="margin:10px auto 20px;position:relative">
                                    <span class="case" style="display: inline-block; position: absolute; top: 25px; left: auto; margin-left: -4px;">
                                        <input style="vertical-align: middle; margin-top: 3px;" type="checkbox" name="case" value="1" {% if info.search.case -%} checked {%- endif %} />Case-sensitive search
                                    </span>
                                    <input type="text" name="query" placeholder="search query" value="{{ info.search.query }}" />
                                        in
                                    <select name="in">
                                        {% for mode in info.search.modes %}
                                            <option value="{{ loop.index0 }}" {% if loop.index0 == info.search.in -%} selected {%- endif %}>
                                                {{ mode[0] }}
                                            </option>
                                        {% endfor %}
                                    </select>
                                    <input type="submit" value="Search" />
                                </div>
                            </form>
                        </h2>
                        <div class='loader' style="display:none;">
                        </div>
                        <form action="/gallery/delete" method="post" class="main_form" onsubmit="return confirm('Do you really want to delete your files?');">
                            <input type="hidden" name="key" value="{{ info.key }}" />
                            {% for file in info.files %}
                                <div class="wrapper">
                                    <div class="img" {% if file.type == types.IMAGE -%} style="background-image: url('/api/thumb/{{ file.url }}')" {%- endif %}>
                                        {% if file.type == types.FILE %}
                                            <a title="{{ file.original|e }}" href="/{{ write_ext(file) }}" style="height: 200px; position: absolute; width: 200px;font-size:92px;line-height:200px">
                                                FILE
                                        {% elif file.type == types.IMAGE %}
                                            <a target="_blank" title="{{ file.original|e }}" href="/{{ write_ext(file) }}" style="height: 200px; position: absolute; width: 200px;">
                                                <img width="100%" height="100%" src="data:image/gif;base64,R0lGODlhAQABAID/AMDAwAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" style="opacity: 0">
                                        {% elif file.type == types.PASTE %}
                                            <a title="{{ file.name }}" href="/paste/{{ file.url }}" style="height: 200px; position: absolute; width: 200px;">
                                                <span class="paste">
                                                    {{ file.content|truncate(1000, True)|e }}
                                                </span>
                                                <img width="100%" height="100%" src="data:image/gif;base64,R0lGODlhAQABAID/AMDAwAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" style="opacity: 0;position: relative;top: -203px;">
                                        {% endif %}
                                            </a>
                                            <span class="info">
                                                <input type="checkbox" name="delete_this" value="{{ file.url }}" class="checkbawks" />
                                                {% if file.type == types.FILE %}File:{% elif file.type == types.PASTE %}Paste:{%  endif %}
                                                {% if file.type != types.PASTE %}
                                                    <a title="{{ file.url }}" href="/{{ write_ext(file) }}">{{ hl(file.original|e) }}</a>
                                                {% else %}
                                                    <a title="{{ file.url }}" href="/paste/{{ file.url }}">{{ hl(file.name|e) }} {% if file.name != file.url %}({{ file.url }}){% endif %}</a>
                                                {% endif %}
                                                <br />
                                            </span>
                                            <span class="info details">
                                                <span style="color:rgba(0, 0, 0, 0.5);">Size:</span> {% if file.type == types.IMAGE %}{{ file.size }} ({{ file.resolution[0] }}x{{ file.resolution[1] }}){% elif file.type == types.PASTE %}{{ file.size }} lines{% else %}{{ file.size }}{% endif %}
                                                <br />
                                                <span style="color:rgba(0, 0, 0, 0.5);">Uploaded:</span> {{ file.time.timestamp }}
                                                <br />
                                                <span style="color:rgba(0, 0, 0, 0.5);">Hits:</span> {{ file.hits }}
                                            </span>
                                    </div>
                                </div>
                            {% endfor %}
                            <h2 class="pages bottom">
                                {{ render_pagination(info.pages) }}
                            </h2>
                            <h2 class="debug">
                                <div>
                                    password: <input type="password" value="" name="password" placeholder="key password" /> <input type="submit" name="type" value="Delete Selected" /> <input type="submit" name="type" value="Delete All" />
                                </div>
                            </h2>
                        </form>
                        <h2 class="debug">
                            <div>
                                <form action="/gallery/delete/advanced" method="get" class="main_form">
                                    <input type="submit" value="Advanced Delete..." />
                                </form>
                            </div>
                        </h2>
    {% if not info.pjax %}
                    </div>
                </div>
                <script src="/static/js/gallery.js"></script>
            </body>
        </html>
    {% endif %}
{% else %}
    <!DOCTYPE HTML>
    <html>
        <head>
            <title>Error: {{ error }}</title>
            <style type="text/css">
              html {background-color: #eee; font-family: sans-serif;}
              body {background-color: #fff; border: 1px solid #ddd;
                    padding: 15px; margin: 15px;}
              pre {background-color: #eee; border: 1px solid #ddd; padding: 5px;}
            </style>
        </head>
        <body>
            <h1>Error: {{ error }}</h1>
            <p>Try again later.</p>
        </body>
    </html>
{% endif %}