{% from "utils.tpl" import flashed_messages %}
<!DOCTYPE html>
<html lang="en">

<head>
  <title>SGFC | {% block title %}{% endblock %}</title>
  <link href="/static/misc/favicon.ico" rel="icon" type="image/x-icon" />
  <link href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css" rel="stylesheet">
  <link href="/static/css/main.css" rel="stylesheet" type="text/css">
  <link href="/static/css/index.css" rel="stylesheet" type="text/css">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>{% block css %}{% endblock %}</style>
  {% block head %}{% endblock %}
</head>

<body class="index">
<div id="container">
  <div id="content">
    {% block other %}{% endblock %}
    <div id="wrapper">
      {% block wrapper %}
        <div id="box-left">
          <a href="/"><h2>SGFC File Upload</h2></a>
          <div class="middle">
            {% block left %}
              <h2>{{ self.title() }}</h2>
            {% endblock %}
            {{ flashed_messages() }}
          </div>
          <div class="bottom">
            {% block extra %}{% endblock %}
          </div>
        </div>
        <div id="box-right">
          {% block content %}{% endblock %}
        </div>
      {% endblock %}
    </div>
    <div id="previews" class="dropzone-previews"></div>
    {% block end %}{% endblock %}
  </div>
</div>
<script src="/static/js/base.js"></script>
{% block script %}{% endblock %}
</body>

</html>