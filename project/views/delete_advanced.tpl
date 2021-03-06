{% extends "base.tpl" %}
{% from "utils.tpl" import login_status, window_csrf with context %}
{% block title %}Advanced Delete{% endblock %}
{% block content %}
  <form class="flex-full" method="post" action="/gallery/delete/advanced">
    {{ form.hidden_tag() }}
    <div class="middle mb-none">
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
      {{ login_status(show_button=True) }}
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