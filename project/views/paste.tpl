{% from "utils.tpl" import login_status, window_csrf with context %}
{% macro render_revisions() %}
  {% if pagination.pages > 1 %}
    [ Revisions:
    {% for rev in pagination.iter_pages()|reverse %}
      {% if rev %}
        {% if rev == pagination.current_page %}
          {{ rev.commit }}
        {% else %}
          <a href="/paste/{{ paste.url }}
              {%- if rev.commit != "base" %}:{{ rev.commit }}{% endif -%}
              {%- if flag.value %}/{{ flag.value }}{% endif -%}"
             {% if rev.message %}title="{{ rev.message }}"{% endif %}
          >{{ rev.commit }}</a>
        {% endif %}
      {% else %}
        ...
      {% endif %}
      {%- if not loop.last %}
        /
      {%- endif -%}
    {% endfor %}
    ]
    <br />
  {% endif %}
  {%- if revision.parent_url %}
    [ Parent: <a href="/paste/{{ revision.parent_url }}">{{ revision.parent_url }}</a> ]
  {%- endif %}
{% endmacro %}
<!DOCTYPE html>
<html>
<head>
  <title>SGFC | {{ title }}</title>
  <link href="/static/misc/favicon.ico" rel="icon" type="image/x-icon" />
  <link href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css" rel="stylesheet">
  <link href="/static/css/main.css" rel="stylesheet" type="text/css">
  <style type="text/css">{{ css }}</style>
  <link href="/static/css/paste.css" rel="stylesheet" type="text/css">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body class="paste">
<div id="container">
  <header>
    {{ title }}
  </header>
  <div id="main" class="wrapper">
    <div class="paste-header">
      <div class="paste-info">
        [
        Characters: {{ paste.length }} |
        Lines: {{ paste.lines }} |
        Hits: {{ paste.hits }} |
        Language: {{ paste.lang }}
        ]
        <br />
        {{ render_revisions() }}
      </div>
      {% set paste_url = paste.url + (":" + revision.commit if revision.commit else "") %}
      <div class="paste-info right">
        [
        <a href="/paste/{{ paste_url }}/raw">View raw paste</a> |
        {% if flag != paste_actions.EDIT -%}
          <a href="/paste/{{ paste_url }}/edit">{% if paste.own %}Edit{% else %}Fork{% endif %} paste</a>
        {%- else -%}
          <a href="/paste/{{ paste_url }}">View paste</a>
        {%- endif %}
        ]
        {% if revision.commit -%}
          <br />
          [ View:
          {% if flag != paste_actions.DIFF -%}
            <a href="/paste/{{ paste_url }}/diff">Diff</a> / Paste
          {%- else -%}
            Diff / <a href="/paste/{{ paste_url }}">Paste</a>
          {%- endif %}
          ]
        {% endif %}
      </div>
    </div>
    {% if flag != paste_actions.EDIT -%}
      {% if revision.message -%}
        <div class="commit-message">
          <h6>Commit Message</h6>
          <div class="code-text">
            <div class="syntax">
              <table class="syntaxtable">
                <tbody>
                <tr>
                  <td class="code">
                    <div class="syntax">
                      <pre>{{ revision.message|trim|e }}</pre>
                    </div>
                  </td>
                </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      {% endif %}
      <div class="code-view">
        {{ paste.content|safe }}
      </div>
    {%- else -%}
      <form action="/api/edit/paste" method="POST" id="paste">
        {{ form.csrf_token }}
        {{ form.id() }}
        {% if revision.id -%}
          {{ form.commit() }}
        {%- endif %}
        {{ form.commit_message(rows=2) }}
        {{ form.body(rows=22) }}
        <div style="text-align:center; margin-top:15px">
          <div id="message" style="display: none">Uploading...</div>
          {{ login_status(show_button=True) }}
          <br />
          <input type="submit" name="submit" value="{% if paste.own %}Edit{% else %}Fork{% endif %}" />
        </div>
      </form>
      {{ window_csrf() }}
      <script src="/static/js/base.js" type="text/javascript"></script>
      <script src="/static/js/pastebin.js" type="text/javascript"></script>
    {%- endif %}
  </div>
</div>
</body>
</html>
