{% extends "base.tpl" %}
{% from "utils.tpl" import login_form, window_csrf with context %}
{% block title %}Advanced Delete{% endblock %}
{% block content %}
  <form class="flex-full" method="post" action="/gallery/delete/advanced">
    {{ form.hidden_tag() }}
    <div class="middle mb-none">
      {{ login_form(form, show_logged_in=True) }}
      <p>
        Delete uploads where:
      </p>
      <div class="padded">
        {{ form.type() }}
        &nbsp;is&nbsp;
        {{ form.operator() }}
        &nbsp;to&nbsp;
        {{ form.threshold(size=10) }}
      </div>
    </div>
    <div class="bottom">
      <p>
        <input type="submit" />
      </p>
    </div>
  </form>
{% endblock %}
{% block script %}
  {{ window_csrf() }}
{% endblock %}