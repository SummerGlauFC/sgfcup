<!DOCTYPE html>

<html>

<head>
    <title>SGFC >> Settings</title>
    <link rel="icon" type="image/ico" href="/favicon.ico" />
    <link href='/static/css/style.css' rel='stylesheet' type='text/css'>
    <link href='/static/css/settings.css' rel='stylesheet' type='text/css'>
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
        #main a {
            text-decoration: underline !important;
        }
        .rightcol label {
            padding-left: 0px !important;
        }
        .rightcol input {
            margin-left: 0;
        }
    </style>
</head>

<body class="settings">
    <table id="maintb" cellpadding="0" cellspacing="0">
        <tr>
            <td id="maintd">
                <header>
                    Settings
                </header>
                <div id="main">
                    <form action="" method="post">
                        Enter your present details in order to make changes
                        <p style="float:right;margin:3px 0;">You can find your current details at <a href="/keys">/keys</a>
                        </p>
                        <br/>
                        <br/>
                        <label>Present key:</label>
                        <input type="text" class="textbox rightcol" value="{{ key }}" name="confirm_key">
                        <br />
                        <label>Present password:</label>
                        <input type="text" class="textbox rightcol" value="{{ password }}" name="confirm_pass">
                        <br />
                        <br />
                        <h2>Change key details</h2>
                        <label for="password">New Password:</label><span class="rightcol"><input type="text" class="textbox" value="" name="password"></span>
                        <br />
                        {% for key, val in settings.groups.items() %}
                            <h2>{{ key }}</h2>
                            {% for item in val %}
                                {% set value = settings[item] %}
                                <label>{{ value.name }}:</label>
                                    {% if value.type == "radio" %}
                                        <ul class="rightcol">
                                        {%- for option in value.options %}
                                            <li>
                                                <label>
                                                    <input type="radio" name="{{ item }}" value="{{ loop.index0 }}"
                                                    {%- if value.value == loop.index0 %} checked {% endif -%}
                                                    /> {{ option }}
                                                </label>
                                            </li>
                                        {% endfor -%}
                                        </ul>
                                    {% else %}
                                        <span class="rightcol">
                                            <input class="textbox" type="{{ value.type }}" name="{{ item }}" value="{{ value.value }}" />
                                            {% if value.notes %}
                                                <p>{{ value.notes }}</p>
                                            {% endif %}
                                        </span>
                                    {% endif %}
                                {% if not loop.last %}<br />{% endif %}
                            {% endfor %}
                            <br />
                        {% endfor %}
                        <input type="submit" value="Save Changes" class="button" style="float:right;">
                        <br />
                    </form>
                </div>
            </td>
        </tr>
    </table>
</body>

</html>