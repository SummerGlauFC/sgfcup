{% extends "base.tpl" %}
{% block title %}{{ title }}{% endblock %}
{% block extra %}
  {{ extra|safe }}
  <p><a href="/">Return to homepage...</a></p>
{% endblock %}
{% block content %}
  {{ content|safe }}
{% endblock %}