<!DOCTYPE html>
<html>

<head>
  <title>SGFC | {% block title %}{% endblock %}</title>
  <link href="/static/misc/favicon.ico" rel="icon" type="image/x-icon" />
  <link href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css" rel="stylesheet">
  <link href='/static/css/main.css' rel='stylesheet' type='text/css'>
  <link href='/static/css/index.css' rel='stylesheet' type='text/css'>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>{% block css %}{% endblock %}</style>
  {% block head %}{% endblock %}
</head>

<body class="index">
<table id="maintb" cellpadding="0" cellspacing="0">
  <tr>
    <td id="maintd">
      {% block other %}{% endblock %}
      <div id="wrapper" class='cf'>
        <header id="box-left">
          <a href="/"><h2>SGFC File Upload</h2></a>
          <div class='cf'>
            {% block left %}
              <h3>{{ self.title() }}</h3>
            {% endblock %}
          </div>
          <div class="bottom">
            {% block extra %}{% endblock %}
          </div>
        </header>
        <div id="box-right">
          <table id="overlaytb">
            <tr>
              <td style='vertical-align:middle'>
                {% block content %}{% endblock %}
              </td>
            </tr>
          </table>
        </div>
      </div>
      <div id="previews" class="dropzone-previews"></div>
      {% block end %}{% endblock %}
    </td>
  </tr>
</table>
<script src="/static/js/base.js"></script>
{% block script %}{% endblock %}
</body>

</html>