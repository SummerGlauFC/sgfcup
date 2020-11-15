{% extends "base.tpl" %}
{% from "utils.tpl" import login_form with context %}
{% block title %}Link Account{% endblock %}
{% block content %}
  <form class="flex-full" method="post" action="">
    {{ form.hidden_tag() }}
    <div class="middle">
      {{ login_form(form) }}
      {% if not current_user.is_authenticated %}
        <p>
          If the provided account does not exist, it will be created.
        </p>
      {% endif %}
    </div>
    <div class="bottom">
      <p>
        {{ form.link() }}
      </p>
    </div>
  </form>
{% endblock %}