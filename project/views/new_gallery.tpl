{% macro render_pagination(pagination) %}
    {% if pagination.has_prev %}
        <a class="pages" href="{{ url_for_page(pagination.page - 1)
          }}" data-page="{{ page }}">&laquo;</a>
    {% endif %}
    {%- for page in pagination.iter_pages() %}
        {% if page %}
            <a class="pages" href="{{ url_for_page(page) }}" data-page="{{ page }}">
            {% if page != pagination.page %}
                {{ page }}
            {% else %}
                <span style="color: #090910;font-weight: bold !important;">{{ page }}</span>
            {% endif %}
            </a>
        {% else %}
            <a class="pages"><span style="color: #090910"> .. </span></a>
        {% endif %}
    {%- endfor %}
    {% if pagination.has_next %}
        <a class="pages" href="{{ url_for_page(pagination.page + 1) }}" data-page="{{ page }}">&raquo;</a>
    {% endif %}
{% endmacro %}
{% macro write_ext(file) %}{% if info.show_ext %}{{ file.url }}{{ file.ext }}{% else %}{{ file.url }}{% endif %}{% endmacro %}
{% if not error %}
    {% if not info.pjax %}
        <!DOCTYPE html>
        <html>
            <head>
                <link href="data:image/x-icon;base64,AAABAAEAEBAQAAAAAAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAA//36AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAREREREQAAABERERERAAAAAAAAAAAAAAAAABEAAAAAAAABERAAAAAAABEREQAAAAABEREREAAAABERERERAAAAAAEREAAAAAAAAREQAAAAAAABERAAAAAAAAEREAAAAAAAAREQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" rel="icon" type="image/x-icon" />
                <!-- <link href='/static/css/style.css' rel='stylesheet' type='text/css'> -->
                <meta name="viewport" content="width=device-width, maximum-scale=1">
                <title>SGFC >> {{ info.key }}'{% if info.key[-1] != "s" %}s{% endif %} Gallery</title>
                <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
                <script src="//browserstate.github.io/history.js/scripts/bundled/html4+html5/jquery.history.js"></script>
                <style type="text/css">
                    #error { padding: 20px; }
                    .highlight { background: yellow; }
                </style>
                <style>
                    /*  Authors     Craig Rozynski craigrozynski.com, dinosaurswithlaserz.com
                                                Marco Lago marcolago.com
                            Version     2.0 2011-07-15 */

                    /* CSS Reset (customised) */

                    html, body, div, span, h1, h2, h3, h4, h5, h6, p, em, img, small, strong {
                        margin: 0;
                        padding: 0;
                        border: 0;
                        font: inherit;
                        vertical-align: baseline;
                    }
                    body { display: block; }
                    html { overflow-y: scroll; }
                    a:hover, a:active { outline: none; }
                    small { font-size: 85%; }
                    strong, th { font-weight: bold; }
                    ::-moz-selection{ background: #3b7cbf; color: #fff; text-shadow: none; }
                    ::selection { background: #3b7cbf; color: #fff; text-shadow: none; }
                    a:link { -webkit-tap-highlight-color: #3b7cbf; }
                    .ie7 img { -ms-interpolation-mode: bicubic; }
                    h1, h2, h3, h4, h5, h6 { font-weight: bold; }

                    /* Primary Styles */

                    body {
                        padding: 10px;
                        font: 1em "HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", sans-serif;
                        color: #515047;
                        background: url("//sgfc.co/SAgXV") repeat scroll 0 0%, linear-gradient(to bottom, rgba(239,239,239,1) 0%,rgba(158,158,158,1) 100%) repeat scroll 0 0 rgba(0, 0, 0, 0);
                    }
                    a:not(.pages), a:not(.pages):link, a:not(.pages):visited, a:not(.pages):active, .title, .category {
                        float: left;
                        width: 100%;
                        height: auto;
                        margin-bottom: 30px;
                        text-decoration: none;
                    }
                    h1, h2, h3 { font-size: 3em; word-wrap: break-word; }
                    h1 {
                        color: #515047;
                        line-height: 0.8;
                        letter-spacing: -0.05em;
                    }
                    h2 {
                        color: #d4d3c0;
                        line-height: 0.9;
                        letter-spacing: -0.05em;
                    }
                    h3 {
                        color: #3b7cbf;
                        line-height: 0.9;
                        letter-spacing: -0.05em;
                    }
                    p {
                        font-size: 1.25em;
                        line-height: 1.15;
                        margin: 0.75em 0;
                        color: #b9b8a4;
                    }
                    small {
                        font-size: 1em;
                        color: #3b7cbf;
                    }
                    img { max-width: 100%; }

                    a:not(.pages) {
                        background: #fff;
                    }

                    /* Media Queries */

                    /* Column Control Media Queries */

                    @media screen and (min-width:500px) {
                        body {
                            max-width: 1600px;
                            margin: 0 auto;
                            padding: 40px;
                            overflow: hidden;
                        }
                        a:not(.pages) {
                            -webkit-transition: background-color .3s linear;
                            -moz-transition: -color .3s linear;
                            transition: background-color .3s linear;
                        }
                        a:not(.pages), a:not(.pages):link, a:not(.pages):visited, a:not(.pages):active, .title, .category {
                            position: relative;
                            top: 0;
                            overflow: hidden;
                        }
                        div, h2 { position: absolute; }
                    }

                    /* Two Column */

                    @media screen and (min-width:500px) {
                        a:not(.pages), a:not(.pages):link, a:not(.pages):visited, a:not(.pages):hover, a:not(.pages):active, .title, .category {
                            width: 47%;
                            margin: 0 3% 20px 0;
                            padding-bottom: 47%;
                        }
                    }

                    /* Three Column */

                    @media screen and (min-width:800px) {
                        .title, .category, a:not(.pages), a:not(.pages):link, a:not(.pages):visited, a:not(.pages):hover, a:not(.pages):active {
                            width: 31%;
                            margin: 0 2% 20px 0;
                            padding-bottom: 31%;
                        }
                    }

                    /* Four Column */

                    @media screen and (min-width:1200px) {
                        .title, .category, a:not(.pages), a:not(.pages):link, a:not(.pages):visited, a:not(.pages):hover, a:not(.pages):active {
                            width: 23%;
                            margin: 20px 2% 0 0;
                            padding-bottom: 23%;
                        }
                    }

                    /* Font Size Control Media Queries */

                    @media screen and (min-width:500px) {
                        h1, h2, h3 { font-size: 2em; }
                        p { font-size: 1em; line-height: 1.2; }
                    }
                    @media screen and (min-width:600px) {
                        h1, h2, h3 { font-size: 2.5em; }
                    }
                    @media screen and (min-width:700px) {
                        h1, h2, h3 { font-size: 3em; }
                        p { font-size: 1.25em; }
                    }
                    @media screen and (min-width:800px) {
                        h1, h2, h3 { font-size: 2.5em; }
                        p { font-size: 1em; }
                    }
                    @media screen and (min-width:1000px) {
                        h1, h2, h3 { font-size: 3.25em; }
                        p { font-size: 1.25em; }
                    }
                    @media screen and (min-width:1200px) {
                        p { font-size: 1em; }
                    }
                    @media screen and (min-width:1400px) {
                        p { font-size: 1.25em; }
                    }
                    @media screen and (min-width:1600px) {
                        h1, h2, h3 { font-size: 4em; }
                    }
                    small a {
                        background: none repeat scroll 0 0 #CCCCCC;
                        border: 1px dashed #AAAAAA;
                        display: inline-block;
                        font-size: 16px !important;
                        margin: 1px 1px 4px;
                        padding: 5px;
                        width: 20px;
                    }
                    .category {
                        padding-bottom: 1%;
                    }
                    .title > div {
                        position: relative;
                    }
                    .info {
                        background: rgba(0,0,0,0.8);
                        color: #fff;
                        width: 100%;
                        z-index: 1;
                    }
                    a.file .info {
                        padding-bottom: 100%;
                    }
                    .hl {
                        font-weight: bold;
                        background-color: yellow;
                    }
                    .preview.paste {
                        position: absolute;
                        z-index: 0;
                        color: rgba(0, 0, 0, 0.5);
                        bottom: 0;
                    }
                </style>
            </head>

            <body class="gallery">
    {% endif %}
                <form class="sorty" action="" method="get">
                    <div class="category">
                        <h1>Gallery</h1>
                        <p>
                            <select name="sort" id="sort">
                                {% for mode in info.sort.list %}
                                    <option value="{{ loop.index0 }}" {% if loop.index0 == info.sort.current -%} selected {%- endif %}>
                                        {{ mode[0] }}
                                    </option>
                                {% endfor %}
                            </select>
                            <input type="submit" value="Sort" />
                            <span class="case" style="display: inline-block;">
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
                            </select><br />
                            <input type="submit" value="Search" />
                        </p>
                        <small>{{ render_pagination(info.pages) }}</small>
                    </div>
                </form>
                <script>
                    var current_page = {{ info.pages.page }};
                </script>
                <div class='loader' style="display:none;">
                    <img src="data:image/gif;base64,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" style="margin: 50px;" />
                </div>
                    <form action="/gallery/delete" method="post" class="main_form">
                        <input type="hidden" name="key" value="{{ info.key }}" />
                        {% for file in info.files %}
                        <a href="{% if file.type == types.paste %}/paste/{{ file.url }}{% else %}/{{ write_ext(file) }}{% endif %}" class="title {{ types.keys()[types.values().index(file.type)] }}" style="{% if file.type == types.image %}background-image: url('/api/thumb/{{ file.url }}'); {% endif %}background-size: cover;">
                            <div>
                                <div class="info">
                                    <h3>
                                        {% if file.type != types.paste %}
                                            {{ hl(file.original|truncate(20, True)) }}
                                        {% else %}
                                            {{ hl(file.name) }}{% if file.name != file.url %} ({{ file.url }}){% endif %}
                                        {% endif %}
                                    </h3>
                                    <span>Size:</span> {% if file.type == types.image %}{{ file.size }} ({{ file.resolution[0] }}x{{ file.resolution[1] }}){% elif file.type == types.paste %}{{ file.size }} lines{% else %}{{ file.size }}{% endif %}
                                    <br />
                                    <span>Uploaded:</span> {{ file.time.timestamp }}
                                    <br />
                                    <span>Hits:</span> {{ file.hits }}
                                </div>
                            </div>
                            <div class="preview paste">
                                {% if file.type == types.paste %}
                                    {{ file.content|truncate(1000, True) }}
                                {% endif %}
                            </div>
                        </a>
                        {% endfor %}
                        <div class="category">
                            <h1>pages</h1>
                            <p>
                                <small>{{ render_pagination(info.pages) }}</small>
                            </p>
                        </div>
                    </form>
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
                                    $("body").html(result);
                                }
                            });
                            current_page = State.data.state;
                            console.log(current_page);
                        });

                        $(document).ready(function() {
                            $(document).on('click','small a',function(e){
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
    {% if not info.pjax %}
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