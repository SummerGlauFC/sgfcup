{% extends "base.tpl" %}
{% block title %}super secret admin panel do not leek{% endblock %}
{% block content %}
  <form method="post" action="/admin/deletehits">
    Delete uploads for <input type="text" value="" placeholder="key" name="key" />
    <br />
    where hits &lt;=:
    <input type="text" name="hit_threshold" size="5" />
    <br /><br />
    <input type="checkbox" name="all_keys" /> Delete from all keys
    <br /><br />
    <input type="submit" />
  </form>
{% endblock %}