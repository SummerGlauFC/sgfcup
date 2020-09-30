{% extends "base.tpl" %}
{% block title %}Delete Files{% endblock %}
{% block css %}
  ul { text-align: left; }
{% endblock %}
{% block extra %}
  {% if key %}
    <a href="/gallery/{{ key }}">Return to your gallery...</a>
  {% endif %}
  <br />
  <a href="/">Return to the homepage...</a>
{% endblock %}
{% block content %}
  <ul>
    {% for message in messages %}
      <li>{{ message }}</li>
    {% endfor %}
  </ul>
{% endblock %}