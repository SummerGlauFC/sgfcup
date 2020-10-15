{% extends "base.tpl" %}
{% from "utils.tpl" import login_form %}
{% block title %}Homepage{% endblock %}
{% block head %}
  <link href='/static/css/dropzone.css' rel='stylesheet' type='text/css'>
{% endblock %}
{% block other %}
  <div id="overlay">
    <table id="overlaytb">
      <tr>
        <td style='vertical-align:middle'>
          <div id='rules-hidden'>
<pre>* filesize limit: 100MB
* all file types are allowed, except for viruses and illegal shit
* Logging policy: No IPs are stored. Ever. As little user tracking as possible.
* Upload logging:
    - Original filename is stored
    - No IP tracking, user ID is stored alongside file
* View logging:
    - Serve and increment hits column by 1
    - No IP or user tracking
* if you want a file removed for reasons (a valid reason please), shoot me an email at <a href='mailto:admin@sgfc.co'>admin@sgfc.co</a>, with the offending link and a reason why it should be gone.
* if you feel like poking around the source, visit <a href="http://github.com/SummerGlauFC/sgfcup">http://github.com/SummerGlauFC/sgfcup</a></pre>
            <button type='button' class="toggle-rules">Close Rules</button>
          </div>
        </td>
      </tr>
    </table>
  </div>
{% endblock %}
{% block left %}
  <span class="button-icon">
        <a href="/paste" data-icon="&#xf016;">
            <span class='types'>pastebin</span>
        </a>
    </span>
  <span class="button-icon">
        <a href="/gallery/{{ key }}" data-icon="&#xf03e;">
            <strong class='locks' data-icon="&#xf023;"></strong>
            <span class='types'>gallery</span>
        </a>
    </span>
  <br />
  <span class="button-icon">
        <a href="/settings" data-icon="&#xf013;"><span class='types'>settings</span></a>
    </span>
{% endblock %}
{% block extra %}
  <p>
    <button type='button' class="toggle-rules">View Rules</button>
  </p>
{% endblock %}
{% block content %}
  <template id="dz-preview-template">
    <div class="dz-preview dz-file-preview">
      <div class="dz-details">
        <img data-dz-thumbnail />
        <div class="dz-filename"><span data-dz-name></span></div>
        <div class="dz-size" data-dz-size></div>
      </div>
      <div class="dz-progress"><span class="dz-upload" data-dz-uploadprogress></span></div>
      <div class="dz-success-mark"><span>✔</span></div>
      <div class="dz-error-mark"><span>✘</span></div>
      <div class="dz-error-message"></div>
      <button class="dz-remove" data-dz-remove>Remove file</button>
    </div>
  </template>
  <form class="dropzone" id="my-awesome-dropzone" action="/api/upload/file" method="post"
        enctype="multipart/form-data">
    <div class="middle mb-none">
      <div id="fields">
        <div id="files">
          Drop files <strong>here</strong>, or click to browse
        </div>
        {{ login_form(key=key, password=password, show_clear=True) }}
      </div>
    </div>
    <div class="bottom">
      <p>
        <input type="submit" name="submit" value="Upload" />
      </p>
    </div>
  </form>
{% endblock %}
{% block script %}
  <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/dropzone/5.7.2/min/dropzone.min.js"></script>
  <script type="text/javascript" src="/static/js/index.js"></script>
{% endblock %}
