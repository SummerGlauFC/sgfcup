{% extends "base.tpl" %}
{% block title %}Admin Login{% endblock %}
{% block content %}
  <form action="" method="post" enctype="multipart/form-data">
    <div id="fields">
      <div id="identification">
        <label for="key">User</label>&nbsp;
        <input type="text" size="20" name="key" id="key" />
        <br />
        <label for="password">Password</label>&nbsp;
        <input type="password" size="20" name="password" id="password" />
      </div>
    </div>
    <br />
    <input type="submit" name="submit" value="Login" />
  </form>
{% endblock %}