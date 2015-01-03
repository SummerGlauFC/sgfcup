{% extends "base.tpl" %}
{% block title %}Delete Files{% endblock %}
{% block css %}
    ul { text-align: left; }
{% endblock %}
{% block content %}
    <ul>
    {% for message in messages %}
        <li>{{ message }}</li>
    {% endfor %}
    </ul>
    {% if key %}
        <a href="/gallery/{{ key }}">Return to your gallery</a>
    {% else %}
        <a href="/">Return to homepage</a>
    {% endif %}
{% endblock %}