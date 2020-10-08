{% extends "base.tpl" %}
{% from "utils.tpl" import login_form %}
{% block head %}
  <link href='/static/css/settings.css' rel='stylesheet' type='text/css'>
{% endblock %}
{% block title %}Settings{% endblock %}
{% block other %}
  <header>
    Settings
  </header>
{% endblock %}
{% block wrapper %}
  <form action="" method="post">
    <p class="form-field">Enter your present details in order to make changes.</p>
    <p class="form-field">
      <label for="confirm_key">Key</label>
      <input type="text" class="right-col textbox" value="{{ key }}" name="confirm_key">
    </p>
    <p class="form-field">
      <label for="confirm_pass">Password</label>
      <input type="password" class="right-col textbox" value="{{ password }}" name="confirm_pass">
    </p>
    <h2>Change key details</h2>
    <p class="form-field">
      <label for="password">New Password</label>
      <input type="password" class="right-col textbox" value="" name="password">
    </p>
    {% for key, val in settings.groups.items() %}
      <h2>{{ key }}</h2>
      {% for item in val %}
        {% set value = settings[item] %}
        <div class="form-field">
          <label>{{ value.name }}</label>
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
            <input class="right-col textbox" type="{{ value.type }}" name="{{ item }}" value="{{ value.value }}" />
          {% endif %}
          {% if value.notes %}
            <p class="right-col notes">{{ value.notes|safe }}</p>
          {% endif %}
        </div>
      {% endfor %}
    {% endfor %}
    <div class="cf save-button-container">
      <input type="submit" value="Save Changes" class="button">
    </div>
  </form>
{% endblock %}