{% extends 'base.tpl' %}
{% block title %}Error{% if in_title %}: {{ error }}{% endif %}{% endblock %}
{% block left %}
  <h1>Error</h1>
  {% if status %}
    <h2>{{ status }}</h2>
  {% endif %}
{% endblock %}
{% block extra %}
  {{ extra|safe }}
  <p><a href="/">Return to the homepage...</a></p>
{% endblock %}
{% block content %}
  <div class="middle">
    <h2>{{ error }}</h2>
    <p>Make sure all provided information is correct, and try again.</p>
  </div>
{% endblock %}