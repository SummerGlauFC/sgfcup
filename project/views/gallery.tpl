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
                        $if public:
                            text-align: center;
                        $else:
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
                        <h2 class="pages" style="position:relative;">
                            {{ render_pagination(info.pages) }}
                        </h2>
                        <script>
                            var current_page = {{ info.pages.page }};
                        </script>
                        <h2 class="debug top">
                            <form class="sorty" action="" method="get" style="display: block;margin-top: 3px;text-align: center;">
                            <!-- {{ info.sort , info.search }} -->
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
                            <img src="data:image/gif;base64,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" style="margin: 50px;" />
                        </div>
                        <form action="/gallery/delete" method="post" class="main_form">
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
                                    delete selected images: <input type="password" value="" name="password" placeholder="key password" /> <input type="submit" value="Delete" />
                                </div>
                            </h2>
                        </form>
    {% if not info.pjax %}
                    </div>
                </div>
                <script>
                     // $$(this).attr('href')
                     var current_page;
                     History.Adapter.bind(window,'statechange',function(){ // Note: We are using statechange instead of popstate
                        // Log the State
                        var State = History.getState(); // Note: We are using History.getState() instead of event.state
                        History.log('statechange:', State.data, State.title, State.url);
                        $('.main_form').fadeOut(100);
                        $('.loader').fadeIn(100);
                        $.ajax({
                            url: State.url,
                            beforeSend: function(jqXHR, settings) {
                                jqXHR.setRequestHeader('X-AJAX', 'true');
                            },
                            // You need to manually do the equivalent of "load" here
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
                                    History.pushState({state:$(this).attr('data-page')}, $(document).attr('title'), $(this).attr('href')); // logs {state:1}, "State 1", "?state=1"
                                }
                            }
                        })
                    });

                    // $$(document).pjax('#pages a', '#main')
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