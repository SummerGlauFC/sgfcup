{% extends "base.tpl" %}
{% from "utils.tpl" import login_form %}
{% block title %}Pastebin{% endblock %}
{% block head %}
  <style type="text/css">
      #paste_body {
          height: 392px;
          width: 392px;
          max-width: 95vw;
          margin: 0 !important;
      }

      #reset {
          margin: 1rem;
      }

      #box-right {
          min-height: 430px;
          padding: 1rem;
          box-sizing: border-box;
      }

      #details {
          margin: 2rem;
      }

      textarea {
          font-family: "InconsolataMedium", Consolas, Monaco, "Liberation Mono", Courier,
          monospace;
          font-size: 12px;
          margin: 0.5rem 0;
      }
  </style>
{% endblock %}
{% block other %}
  <form id="paste" action="/api/upload/paste" method="post">
{% endblock %}
{% block left %}
  <h2>{{ self.title() }}</h2>
  <div id="details">
    <p>
      <label>Name:</label>
      <input type="text" name="paste_name" id="paste_name" placeholder="(optional)" />
    </p>
    <p>
      <label for="lang">Language:</label>
      <select name="lang" id="lang">
        <option value="text" selected>Plain Text</option>
        <optgroup label="------ POPULAR LANGUAGES -------">
          <option value="bash">Bash</option>
          <option value="c">C</option>
          <option value="csharp">C#</option>
          <option value="cpp">C++</option>
          <option value="css">CSS</option>
          <option value="html">HTML</option>
          <option value="json">JSON</option>
          <option value="java">Java</option>
          <option value="js">JavaScript</option>
          <option value="ts">TypeScript</option>
          <option value="lua">Lua</option>
          <option value="md">Markdown</option>
          <option value="objective-c">Objective C</option>
          <option value="php">PHP</option>
          <option value="perl">Perl</option>
          <option value="python">Python</option>
          <option value="rb">Ruby</option>
          <option value="swift">Swift</option>
        </optgroup>
        <optgroup label="------ ALL LANGUAGES -------">
          {% for lang in langs %}
            <option value="{{ lang[1][0] }}">{{ lang[0] }}</option>
          {%- endfor %}
        </optgroup>
      </select>
    </p>
  </div>
  {{ login_form(key=key, password=password, show_clear=True) }}
  <br />
{% endblock %}
{% block extra %}
  <p>
    <input type="submit" name="submit" value="Paste" />
  </p>
{% endblock %}
{% block content %}
  <div class="middle">
    <div id="message" style="display: none">Uploading...</div>
    <textarea tabindex="20" name="paste_body" id="paste_body" class="pastebox"></textarea>
    <div style="text-align:center; display: none" id="reset">
      <button type="button">Go back</button>
    </div>
  </div>
{% endblock %}
{% block end %}
  </form>
{% endblock %}
{% block script %}
  <script src="/static/js/base.js" type="text/javascript"></script>
  <script src="/static/js/pastebin.js" type="text/javascript"></script>
{% endblock %}
