<!DOCTYPE html>
<html>
    <head>
        <title>SGFC >> {{ title }}</title>
        <link rel="icon" type="image/ico" href="/favicon.ico" />
        <link href='/static/css/style.css' rel='stylesheet' type='text/css'>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
            {{ css }}
        </style>
    </head>

    <body class="paste">
        <div id="container">
            <header>
                {{ title }}
            </header>
            <div id="main">
                <div class="boardlist">[ Characters: {{ length }} / Lines: {{ lines }} / Hits: {{ hits }} / Language: {{ lang }} ]</div>
                {% if not edit %}
                    <div class="boardlist" style="float:right;">[
                            <a href="/paste/{{ url }}/raw">Raw paste</a>
                     ]</div>
                    <div class="allcode">
                        {{ content }}
                    </div>
                {% else %}
                    <div class="allcode">
                        <textarea tabindex="20" rows="22" name="paste_edit_body" id="paste_edit_body" cols="40" class="pastebox">{{ content }}</textarea>
                    </div>
                {% endif %}
            </div>
        </div>
    </body>
</html>