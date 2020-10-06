{% extends "base.tpl" %}
{% from "utils.tpl" import login_form %}
{% block title %}Admin Login{% endblock %}
{% block content %}
  <form action="" method="post" enctype="multipart/form-data">
    {{ login_form() }}
    <br />
    <input type="submit" name="submit" value="Login" />
  </form>
{% endblock %}