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
{% macro write_ext(file) %}{% if info.show_ext %}{{ file.url }}{{ file.ext }}{% else %}{{ file.url }}{% endif %}{% endmacro %}
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
                <style type="text/css">
                    #error { padding: 20px; }
                    .highlight { background: yellow; }
                </style>
                <style>
                    html,
                    body {
                        background: url("//sgfc.co/SAgXV") repeat fixed 0 0%, linear-gradient(to bottom, #485563 0%, #29323c 100%) repeat fixed 0 0 rgba(0, 0, 0, 0);
                    }
                    .info
                    {
                        background: none repeat scroll 0 0 #FFFFFF;
                        box-shadow: 0 0 1px rgba(0, 0, 0, 0.8) inset, 0 2px 0 rgba(255, 255, 255, 0.5) inset, 0 -1px 0 rgba(0, 0, 0, 0.4) inset;
                        color: #000000;
                        display: inline-block;
                        font-size: 75%;
                        margin-top: 2px;
                        overflow: hidden;
                        padding: 2px 4px;
                        text-align: right;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                        width: 192px;
                        position: relative;
                        top: 201px;
                    }

                    body.gallery .wrapper {
                        margin-bottom: 60px;
                        height: 240px;
                    }

                    body.gallery h2.debug.top { margin-bottom: 20px }

                    .hl {background:yellow; font-weight:bold}
                </style>
            </head>

            <body class="gallery">
                <div id="container">
                    <header>
                        <a href="/">Gallery</a>
                    </header>
                    <div id="main">
    {% endif %}
                        <h2>{{ info.usage }} Used</h2>
                        <h2 class="debug pages" style="position:relative;">
                            {{ render_pagination(info.pages) }}
                        </h2>
                        <script>
                            var current_page = {{ info.pages.page }};
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
                                    <div class="img" {% if file.type == types.image -%} style="background-image: url('/api/thumb/{{ file.url }}')" {%- endif %}>
                                        {% if file.type == types.file %}
                                            <a title="{{ file.original|e }}" href="/{{ write_ext(file) }}" style="height: 200px; position: absolute; width: 200px;font-size:92px;line-height:200px">
                                                FILE
                                        {% elif file.type == types.image %}
                                            <a target="_blank" title="{{ file.original|e }}" href="/{{ write_ext(file) }}" style="height: 200px; position: absolute; width: 200px;">
                                                <img width="100%" height="100%" src="data:image/gif;base64,R0lGODlhAQABAID/AMDAwAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" style="opacity: 0">
                                        {% elif file.type == types.paste %}
                                            <a title="{{ file.name }}" href="/paste/{{ file.url }}" style="height: 200px; position: absolute; width: 200px;">
                                                <span class="paste">
                                                    {{ file.content|truncate(1000, True)|e }}
                                                </span>
                                                <img width="100%" height="100%" src="data:image/gif;base64,R0lGODlhAQABAID/AMDAwAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" style="opacity: 0;position: relative;top: -203px;">
                                        {% endif %}
                                            </a>
                                            <span class="info">
                                                <input type="checkbox" name="delete_this" value="{{ file.url }}" class="checkbawks" />
                                                {% if file.type == types.file %}File:{% elif file.type == types.paste %}Paste:{%  endif %}
                                                {% if file.type != types.paste %}
                                                    <a title="{{ file.url }}" href="/{{ write_ext(file) }}">{{ hl(file.original|e) }}</a>
                                                {% else %}
                                                    <a title="{{ file.url }}" href="/paste/{{ file.url }}">{{ hl(file.name|e) }} {% if file.name != file.url %}({{ file.url }}){% endif %}</a>
                                                {% endif %}
                                                <br />
                                            </span>
                                            <span class="info details">
                                                <span style="color:rgba(0, 0, 0, 0.5);">Size:</span> {% if file.type == types.image %}{{ file.size }} ({{ file.resolution[0] }}x{{ file.resolution[1] }}){% elif file.type == types.paste %}{{ file.size }} lines{% else %}{{ file.size }}{% endif %}
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
                <script>
                     var current_page;
                     History.Adapter.bind(window,'statechange',function(){
                        var State = History.getState();
                        History.log('statechange:', State.data, State.title, State.url);
                        $('.main_form').fadeOut(100);
                        $('.loader').fadeIn(100);
                        $.ajax({
                            url: State.url,
                            beforeSend: function(jqXHR, settings) {
                                jqXHR.setRequestHeader('X-AJAX', 'true');
                            },
                            success: function(result) {
                                $('.loader').hide();
                                $("#main").html(result);
                            }
                        });
                        current_page = State.data.state;
                        console.log(current_page);
                    });

                    $(document).ready(function() {
                        $(document).on('click','.pages a',function(e){
                            e.preventDefault();
                            console.log('prevented click' + e);
                            if($(this).attr('data-page') !== undefined) {
                                console.log($(this).attr('data-page') + ' != ' + current_page);

                                a_this = $(this)

                                if($(this).attr('data-page') != current_page) {
                                    History.pushState({state:$(this).attr('data-page')}, $(document).attr('title'), $(this).attr('href'));
                                }
                            }
                        })
                    });
                </script>
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