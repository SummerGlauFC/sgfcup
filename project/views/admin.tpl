{% extends "base.tpl" %}
{% block title %}super secret admin panel<br>do not leek{% endblock %}
{% block extra %}
  <form action="/admin/logout" method="post">
    <p>
      <input type='submit' value="Sign out" />
    </p>
  </form>
{% endblock %}
{% block content %}
  <form class="flex-full" method="post" action="/admin/deletehits">
    {{ form.hidden_tag() }}
    <div class="middle mb-none">
      Delete uploads for {{ form.key(placeholder="key") }}
      <br />
      where hits &lt;= {{ form.hit_threshold(size=5) }}
      <br /><br />
      {{ form.all_keys() }} {{ form.all_keys.label }}
    </div>
    <div class="bottom">
      <p><input type="submit" /></p>
    </div>
  </form>

{% endblock %}