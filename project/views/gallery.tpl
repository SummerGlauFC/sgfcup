{% macro render_pagination(pagination) %}
    {% if pagination.has_prev %}
        <a href="{{ url_for_page(pagination.page - 1)
          }}">&laquo;</a>
    {% endif %}
    {%- for page in pagination.iter_pages() %}
        {% if page %}
            <a href="{{ url_for_page(page) }}">
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
        <a href="{{ url_for_page(pagination.page + 1) }}">&raquo;</a>
    {% endif %}
{% endmacro %}
{% macro write_ext(file) %}{% if show_ext %}{{ file.url }}.{{ file.ext }}{% else %}{{ file.url }}{% endif %}{% endmacro %}
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
                        Gallery
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
                                        {% endif %}
                                            </a>
                                            <span class="info">
                                                <input type="checkbox" name="delete_this" value="{{ file.url }}" class="checkbawks" />
                                                {% if file.type == types.file %}File:{% endif %}
                                                <a title="{{ file.url }}" href="/{{ write_ext(file) }}">{{ hl(file.original) }}</a>
                                                <br />
                                            </span>
                                            <span class="info details">
                                                <span style="color:rgba(0, 0, 0, 0.5);">Size:</span> {{ file.size }} ({{ file.resolution[0] }}x{{ file.resolution[1] }})
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
                        $(document).on('click','#pages a',function(e){
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