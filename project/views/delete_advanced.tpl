{% extends "base.tpl" %}
{% block title %}Advanced Delete{% endblock %}
{% block content %}
  <form method="post" action="/gallery/delete/advanced">
    <div id="fields">
      <div id="identification">
        <label for="key">Key</label>&nbsp;
        <input type="text" size="20" name="key" id="key" value="{{ key }}" />
        <br />
        <label for="password">Password</label>&nbsp;
        <input type="password" size="20" name="password" id="password" value="" />
      </div>
    </div>
    <br />
    Delete uploads where:
    <br /><br />
    <select name="type">
      <option value="hits">Hit Count</option>
      <option value="size">Size (bytes)</option>
    </select>
    is
    <select name="operator">
      <option value="less"> {{ 'equal or less' }} </option>
      <option value="greater"> {{ 'equal or greater' }} </option>
    </select>
    than
    <input type="text" name="threshold" size="10" />
    <br /><br />
    <input type="submit" />
  </form>
{% endblock %}