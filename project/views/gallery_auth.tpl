{% extends "base.tpl" %}
{% block title %}Authenticate{% endblock %}
{% block content %}
  <form class="flex-full" action="" method="post">
    {{ form.hidden_tag() }}
    <div class="middle mb-none">
      <p>You need to authenticate to view this gallery.</p>
      <p>{{ form.authcode() }}</p>
      <p>
        {{ form.remember() }} {{ form.remember.label }}
      </p>
    </div>
    <div class="bottom">
      <p>
        <input value="Submit" type="submit" />
      </p>
    </div>
  </form>
{% endblock %}
