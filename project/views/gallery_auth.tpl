{% extends "base.tpl" %}
{% block title %}Authenticate{% endblock %}
{% block content %}
  You need to authenticate to view this gallery.
  <br />
  <br />
  <form action="" method="post">
    <input type="password" name="authcode" placeholder="gallery password" />
    <br />
    <br />Remember this key?
    <br />
    <input type="radio" name="remember" value="1" id="pub" checked>
    <label>Yes</label>
    <input type="radio" name="remember" value="0" id="priv">
    <label>No</label>
    <br />
    <br />
    <input value="Submit" type="submit" />
  </form>
{% endblock %}
