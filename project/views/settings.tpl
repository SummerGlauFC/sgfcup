<!DOCTYPE html>

<html>

<head>
  <title>SGFC >> Settings</title>
  <link rel="icon" type="image/ico" href="/favicon.ico" />
  <link href='/static/css/main.css' rel='stylesheet' type='text/css'>
  <link href='/static/css/settings.css' rel='stylesheet' type='text/css'>
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body class="settings">
<table id="maintb" cellpadding="0" cellspacing="0">
  <tr>
    <td id="maintd">
      <header>
        Settings
      </header>
      <div id="wrapper">
        <form action="" method="post">
          <div>Enter your present details in order to make changes.</div>
          <br />
          <br />
          <label for="confirm_key">Key:</label>
          <input type="text" class="textbox right-col" value="{{ key }}" name="confirm_key">
          <br />
          <label for="confirm_pass">Password:</label>
          <input type="text" class="textbox right-col" value="{{ password }}" name="confirm_pass">
          <br />
          <br />
          <h2>Change key details</h2>
          <label for="password">New Password:</label>
          <span class="right-col">
            <input type="text" class="textbox" value="" name="password">
          </span>
          <br />
          {% for key, val in settings.groups.items() %}
            <h2>{{ key }}</h2>
            {% for item in val %}
              {% set value = settings[item] %}
              <label>{{ value.name }}:</label>
              {% if value.type == "radio" %}
                <ul class="right-col">
                  {%- for option in value.options %}
                    <li>
                      <label>
                        <input type="radio" name="{{ item }}" value="{{ loop.index0 }}"
                            {%- if value.value == loop.index0 %} checked {% endif -%}
                        /> {{ option|safe }}
                      </label>
                    </li>
                  {% endfor -%}
                </ul>
              {% else %}
                <span class="right-col">
                  <input class="textbox" type="{{ value.type }}" name="{{ item }}" value="{{ value.value }}" />
                </span>
              {% endif %}
              {% if value.notes %}
                <p class="right-col">{{ value.notes|safe }}</p>
              {% endif %}
              {% if not loop.last %}<br />{% endif %}
            {% endfor %}
            <br />
          {% endfor %}
          <div style="margin-bottom: 2em">
            <input type="submit" value="Save Changes" class="button" style="float:right;">
          </div>
        </form>
      </div>
    </td>
  </tr>
</table>
</body>

</html>