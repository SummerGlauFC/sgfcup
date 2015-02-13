<!DOCTYPE html>
<html>
    <head>
        <title>SGFC >> {{ title }}</title>
        <link rel="icon" type="image/ico" href="/favicon.ico" />
        <link href='/static/css/style.css' rel='stylesheet' type='text/css'>
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
        </style>
    </head>

    <body class="paste">
        <div id="container">
            <header>
                {{ title }}
            </header>
            <div id="main">
                <div class="boardlist">[ Characters: {{ length }} / Lines: {{ lines }} / Hits: {{ hits }} / Language: {{ lang }} ]
                <br />
                [ Revisions:
                    {% if revisions -%}
                        {% for _revision in revisions[-5:]|reverse %}
                            <!-- {{ _revision.commit }}, {{ revision.commit }}-->
                            {% if _revision.commit != revision.commit %}<a href="/paste/{{ url }}/{{ _revision.commit }}">{% endif %}
                                {{ _revision.commit }}
                                {% if _revision.commit != revision.commit %}</a>{% endif %}
                            {% if not loop.last -%}
                                /
                            {% else %}
                                / <a href="/paste/{{ url }}">base</a>
                            {%- endif %}
                        {% endfor %}
                    {% else -%}
                    None.
                    {%- endif %}
                {% if revision.parent != revision.pasteid %}/ Parent: <a href="/paste/{{ revision.parent_url }}">{{ revision.parent_url }}</a>{% endif %} ]</div>
                {% if not edit %}
                    <div class="boardlist" style="float:right;">[
                            <a href="/paste/{{ url }}/raw">View raw paste</a> /
                            <a href="/paste/{{ url }}/edit">{%- if is_owner %}Edit{% else %}Fork{% endif %} paste</a>
                     ]</div>
                    {% if revision.message %}
                        <h2 style="text-align:center">Message: {{ revision.message|e }}</h2>
                    {% endif %}
                    <div class="allcode">
                        {{ content }}
                    </div>
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
                            $('#key').get(0).setAttribute('value', ''); //this works
                            $('#password').get(0).setAttribute('value', ''); //this works
                        });
                        $("form").submit(function () {
                            var url = "/api/edit/paste"; // the script where you handle the form input.
                            $("textarea").hide();
                            $.ajax({
                                type: "POST",
                                url: url,
                                data: $("form").serialize(), // serializes the form's elements.
                                success: function (data) {
                                    data = JSON.parse(data);
                                    console.log(data);
                                    if (data.success) {
                                        $("#message").html('<a href="' + data.url + '">' + data.base + data.url + '</a>');
                                    } else {
                                        $("#message").html(data.error);
                                    }
                                    $("#message").fadeIn(250);
                                }
                            });
                            return false; // avoid to execute the actual submit of the form.
                        });
                    </script>
                {% endif %}
            </div>
        </div>
    </body>
</html>