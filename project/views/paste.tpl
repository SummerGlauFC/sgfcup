<!DOCTYPE html>
<html>
    <head>
        <title>SGFC >> {{ title }}</title>
        <link rel="icon" type="image/ico" href="/favicon.ico" />
        <link href='/static/css/style.css' rel='stylesheet' type='text/css'>
        <link href='/static/css/paste.css' rel='stylesheet' type='text/css'>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
            html,
            body {
                width: 100%;
                height: 100%;
                background: url("//sgfc.co/SAgXV") repeat fixed 0 0%, linear-gradient(to bottom, #485563 0%, #29323c 100%) repeat fixed 0 0 rgba(0, 0, 0, 0);
            }
            #main {
                background: url("//sgfc.co/TQUet") repeat fixed 0 0 #ffffff !important;
                box-shadow: none !important;
                border: none !important;
            }

            {{ css }}

            textarea, #commit {
                width: 100%;
            }

            #commit {
                padding: 4px 3px;
            }

            .diff {
                border: 1px solid #cccccc;
                font-family: 'InconsolataMedium',Consolas,Monaco,"Liberation Mono",Courier,monospace;
                font-size: 13px;
                line-height: 1.2;
                white-space: normal;
                background: none repeat scroll 0 0 #f8f8f8;
                word-wrap: break-word;
            }

            .diff div:hover {
                background-color: #ffc;
            }

            .diff .control {
                color: #999999;
                background-color: #eaf2f5;
            }

            .diff .insert {
                color: #000000;
                background-color: #ddffdd;
            }

            .diff .insert .highlight {
                color: #000000;
                background-color: #aaffaa;
            }

            .diff .delete {
                color: #000000;
                background-color: #ffdddd;
            }

            .diff .delete .highlight {
                color: #000000;
                background-color: #ffaaaa;
            }
        </style>
    </head>

    <body class="paste">
        <div id="container">
            <header>
                {{ title }}
            </header>
            <div id="main">
                <div class="boardlist">[ Characters: {{ length }} | Lines: {{ lines }} | Hits: {{ hits }} | Language: {{ lang }} ]
                <br />[ Revisions:
                    {% if revisions -%}
                        {%- for _revision in revisions[-5:]|reverse -%}
                            {%- if _revision.commit != revision.commit -%}<a href="/paste/{{ url }}.{{ _revision.commit }}" title="{{ _revision.message }}">{%- endif %}
                                {{ _revision.commit }}
                                {% if _revision.commit != revision.commit -%}</a>{%- endif -%}
                            {%- if not loop.last %}
                                /
                            {% else -%}
                                / {% if revision.commit %}<a href="/paste/{{ url }}">{% endif %}base{% if revision.commit %}</a>{% endif %}
                            {%- endif -%}
                        {%- endfor -%}
                    {%- else -%}
                    base
                    {%- endif -%}
                {% if revision.parent != revision.pasteid %}| Parent: <a href="/paste/{{ revision.parent_url }}">{{ revision.parent_url }}</a>{% endif %} ]</div>
                {% if not edit %}
                    <div class="boardlist" style="float: right; text-align: right;">[
                            <a href="/paste/{{ url }}{% if revision.commit %}.{{ revision.commit }}{% endif %}/raw">View raw paste</a> |
                            <a href="/paste/{{ url }}{% if revision.commit %}.{{ revision.commit }}{% endif %}/edit">{%- if is_owner %}Edit{% else %}Fork{% endif %} paste</a>
                     ]
                     {% if revision.commit %}
                     <br />
                     [ View: {% if flag != "diff" %}<a href="/paste/{{ url }}.{{ revision.commit }}/diff">{% endif %}Diff{% if flag != "diff" %}</a>{% endif %} / {% if flag == "diff" %}<a href="/paste/{{ url }}.{{ revision.commit }}">{% endif %}Normal{% if flag == "diff" %}</a>{% endif %} ]
                     {% endif %}
                    </div>
                    {% if revision.message %}
                        <h2 style="text-align:center">Message: {{ revision.message|e }}</h2>
                    {% endif %}
                    {% if use_wrapper %}
                        <div class="allcode">
                            {{ content }}
                        </div>
                    {% else %}
                        {{ content }}
                    {% endif %}
                {% else %}
                    <form action="/api/edit/paste" method="POST">
                        <div class="allcode">
                            <input type="text" id="commit" name="commit" value="" placeholder="commit message" />
                            <br /><br />
                            <textarea tabindex="20" rows="22" name="paste_edit_body" id="paste_edit_body" class="pastebox">{{ raw_paste }}</textarea>
                        </div>

                        <div style="text-align:center; margin-top:15px">
                            <div id="message" style="display: none">Uploading...</div>
                            <div id="identification">
                                <p class="unimportant">You do not have to change these values.
                                    <br>Clear the fields to upload anonymously.
                                    <br>
                                    <br>
                                    <button id="clear-fields" type="button">Clear Fields</button>
                                </p>
                                <label for="key">Key</label>&nbsp;
                                <input type="text" id="key" name="key" value="{{ key }}" size="20">
                                <br>
                                <label for="password">Pass</label>&nbsp;
                                <input type="password" id="password" name="password" value="{{ password }}" size="20">
                                <br><br>
                            </div>
                            <input type="hidden" name="id" value="{{ id }}" />
                            <input type="submit" name="submit" value="
                            {%- if is_owner %}Edit{% else %}Fork{% endif -%}" />
                        </div>
                    </form>
                    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js" type="text/javascript"></script>
                    <script>
                        $('#clear-fields').on('click', function () {
                            $('#key').get(0).setAttribute('value', '');
                            $('#password').get(0).setAttribute('value', '');
                        });
                        $("form").submit(function () {
                            var url = "/api/edit/paste";
                            $("textarea").hide();
                            $.ajax({
                                type: "POST",
                                url: url,
                                data: $("form").serialize(),
                                success: function (data) {
                                    // data = JSON.parse(data);
                                    console.log(data);
                                    if (data.success) {
                                        $("#message").html('<a href="' + data.url + '">' + data.base + data.url + '</a>');
                                    } else {
                                        $("#message").html(data.error);
                                    }
                                    $("#message").fadeIn(250);
                                }
                            });
                            return false;
                        });
                    </script>
                {% endif %}
            </div>
        </div>
    </body>
</html>
