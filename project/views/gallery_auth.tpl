{% extends "base.tpl" %}
{% block title %}Authenticate{% endblock %}
{% block content %}
    <p>You need to authenticate to view this gallery.</p>
    <form action="" method="post">
        <p><input type="password" name="authcode" placeholder="gallery password"/></p>
        <p>
            <label>
                <input type="checkbox" name="remember" value="1"> Remember this key
            </label>
        </p>
        <input value="Submit" type="submit"/>
    </form>
{% endblock %}
