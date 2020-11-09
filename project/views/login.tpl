{% extends "base.tpl" %}
{% from "utils.tpl" import login_form with context %}
{% block title %}Login{% endblock %}
{% block content %}
  <form class="flex-full" method="post" action="{{ "/logout" if current_user.is_authenticated else "" }}">
    {{ form.hidden_tag() }}
    <div class="middle">
      <p>
        If the provided account does not exist, it will be created.
      </p>
      {{ login_form(form) }}
    </div>
    <div class="bottom">
      <p>
        {% if current_user.is_authenticated %}
          <input type="submit" value="Sign out" />
        {% else %}
          <input type="submit" value="Sign in" />
        {% endif %}
      </p>
    </div>
  </form>
{% endblock %}