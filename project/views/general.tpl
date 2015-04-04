{% extends "base.tpl" %}
{% block title %}{{ title }}{% endblock %}
{% block css %}
    #main {
        text-align: center !important
    }
{% endblock %}
{% block extra %}
    {{ extra }}<br />
    <a href="/">Return to homepage...</a>
{% endblock %}
{% block content %}
    {{ message }}
{% endblock %}