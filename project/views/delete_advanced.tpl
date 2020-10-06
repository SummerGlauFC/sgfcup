{% extends "base.tpl" %}
{% from "utils.tpl" import login_form %}
{% block title %}Advanced Delete{% endblock %}
{% block content %}
  <form method="post" action="/gallery/delete/advanced">
    {{ login_form(key=key) }}
    <br />
    Delete uploads where:
    <br /><br />
    <select name="type">
      <option value="hits">Hit Count</option>
      <option value="size">Size (bytes)</option>
    </select>
    is
    <select name="operator">
      <option value="gte">greater than or equal</option>
      <option value="lte">less than or equal</option>
      <option value="e">equal</option>
    </select>
    to
    <input type="text" name="threshold" size="10" />
    <br /><br />
    <input type="submit" />
  </form>
{% endblock %}