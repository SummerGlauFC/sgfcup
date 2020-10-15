{% extends "base.tpl" %}
{% block title %}Authenticate{% endblock %}
{% block content %}
  <form class="flex-full" action="" method="post">
    <div class="middle">
      <p>You need to authenticate to view this gallery.</p>
      <p><input type="password" name="authcode" placeholder="gallery password" /></p>
      <p>
        <label>
          <input type="checkbox" name="remember" value="1"> Remember this key
        </label>
      </p>
    </div>
    <div class="bottom">
      <p>
        <input value="Submit" type="submit" />
      </p>
    </div>
  </form>
{% endblock %}
