{% extends "base.tpl" %}
{% from "utils.tpl" import flashed_messages, errors, login_status with context %}
{% block head %}
  <link href='/static/css/settings.css' rel='stylesheet' type='text/css'>
{% endblock %}
{% block title %}Settings{% endblock %}
{% block other %}
  <header>
    <a href="/">Settings</a>
  </header>
{% endblock %}
{% macro settings_error(field) %}
  <div class="form-field">
    {{ errors(field, class="right-col textbox") }}
  </div>
{% endmacro %}
{% block wrapper %}
  <div>
    <div class="form-field">
      {{ flashed_messages(break=True) }}
    </div>
    {{ login_status(show_button=True) }}
    <form action="" method="post">
      {{ form.hidden_tag() }}
      {% if not current_user.is_authenticated %}
        <p>Enter your present details in order to make changes.</p>
        {{ settings_error(form.key) }}
        <p class="form-field">
          {{ form.key.label }}
          {{ form.key(class="right-col textbox") }}
        </p>
        <p class="form-field">
          {{ form.password.label }}
          {{ form.password(class="right-col textbox", autocomplete="current-password") }}
        </p>
      {% endif %}
      <h2>Change key details</h2>
      {{ settings_error(form.new_password) }}
      <p class="form-field">
        {{ form.new_password.label }}
        {{ form.new_password(class="right-col textbox", autocomplete="new-password") }}
      </p>
      <p class="form-field">
        {{ form.confirm_new_password.label }}
        {{ form.confirm_new_password(class="right-col textbox", autocomplete="new-password") }}
      </p>
      {% for key, val in settings.groups.items() %}
        <h2>{{ key }}</h2>
        {% for item in val %}
          {% set setting = form[item] %}
          {% set value = settings[item] %}
          {{ settings_error(setting) }}
          <div class="form-field">
            <label for="{{ setting.label.field_id }}">{{ setting.label.text|safe }}</label>
            {% if value.type == "radio" %}
              <ul class="right-col">
                {% for option in setting %}
                  <li>
                    {{ option }}
                    <label for="{{ option.label.field_id }}">{{ option.label.text|safe }}</label>
                  </li>
                {% endfor %}
              </ul>
            {% else %}
              {{ setting(class="right-col textbox") }}
            {% endif %}
            {% if value.notes %}
              <p class="right-col notes">{{ value.notes|safe }}</p>
            {% endif %}
          </div>
        {% endfor %}
      {% endfor %}
      <div class="cf save-button-container">
        <input type="submit" class="button" value="Save Changes">
      </div>
    </form>
  </div>
{% endblock %}