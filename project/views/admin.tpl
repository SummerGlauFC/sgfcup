{% extends "base.tpl" %}
{% block title %}super secret admin panel<br>do not leek{% endblock %}
{% block content %}
  <form class="flex-full" method="post" action="/admin/deletehits">
    <div class="middle mb-none">
      Delete uploads for <input type="text" value="" placeholder="key" name="key" />
      <br />
      where hits &lt;=:
      <input type="text" name="hit_threshold" size="5" />
      <br /><br />
      <input type="checkbox" name="all_keys" /> Delete from all keys
    </div>
    <div class="bottom">
      <p><input type="submit" /></p>
    </div>
  </form>

{% endblock %}