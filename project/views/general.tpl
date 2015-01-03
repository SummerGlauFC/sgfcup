{% extends "base.tpl" %}
{% block title %}{{ title }}{% endblock %}
{% block css %}
    #main {
        text-align: center !important
    }
{% endblock %}
{% block content %}
    {{ message }}
{% endblock %}