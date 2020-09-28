{% extends "base.tpl" %}
{% block title %}Homepage{% endblock %}
{% block head %}
  <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/dropzone/5.7.2/min/dropzone.min.css" />
  <link href='/static/css/dropzone.css' rel='stylesheet' type='text/css'>
{% endblock %}
{% block css %}
{% endblock %}
{% block other %}
  <div id="overlay">
    <table id="overlaytb">
      <tr>
        <td style='vertical-align:middle'>
          <div class='rules-hidden'>
                        <pre>
* filesize limit: 100MB
* all file types are allowed, except for viruses and illegal shit
* Logging policy: No IPs are stored. Ever.
* How upload logging works:
    - You upload file.
    - App receives file and inserts this info into database:
        * filename
        * file path
        * user id (either supplied or generated)
    - App spews upload info back at you
    - go on with your life doing whatever you do
* How viewing logging works:
    - Person opens link for file
    - If the file exists, serve it and increment hits column by 1.
    - thats it
* if you want a file removed for reasons (a valid reason please), shoot me an email at <a href='mailto:admin@sgfc.co'>admin@sgfc.co</a>, with the offending link and a reason why it should be gone.
* if you feel like poking around the source, visit <a href="http://github.com/SummerGlauFC/sgfcup">http://github.com/SummerGlauFC/sgfcup</a>
                            </pre>
            <button type='button' class="toggle-rules">Hide Rules</button>
          </div>
        </td>
      </tr>
    </table>
  </div>
{% endblock %}
{% block left %}
  <span>
        <h6>Pasting?</h6>
        <a href="/paste" data-icon="&#xf016;"></a>
    </span>
  <span>
        <h6>Looking at pics?</h6>
        <a href="/gallery/{{ key }}" data-icon="&#xf03e;">
            <strong class='locks' data-icon="&#xf023;"></strong>
            <span class='types'>private</span>
        </a>
    </span>
  <span>
        <h6>Need your keys for reasons?</h6>
        <a href="/keys" data-icon="&#xf084;"></a>
        or <a href="/settings" data-icon="&#xf013;"></a>
    </span>
  <button type='button' class="toggle-rules">Show Rules</button>
{% endblock %}
{% block content %}
  <div id="message"></div>
  <form class="dropzone" id="my-awesome-dropzone" action="/api/upload/file" method="post" enctype="multipart/form-data">
    <div id="fields">
      <div id="filess">
        Drop files <strong>here</strong>, or click to browse
      </div>
      <div id="identification">
        <p class='unimportant'>You do not have to change these values.
          <br />Clear the fields to upload anonymously.
          <br />
          <br />
          <button type='button' id="clear-fields">Clear Fields</button>
        </p>
        <label for="key">Key</label>&nbsp;
        <input type="text" size="20" value="{{ key }}" name="key" id="key" />
        <br />
        <label for="password">Password</label>&nbsp;
        <input type="password" size="20" value="{{ password }}" name="password" id="password" />
      </div>
    </div>
    <br />
    <input type="submit" name="submit" value="Upload" />
  </form>
{% endblock %}
{% block script %}
  <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/dropzone/5.7.2/min/dropzone.min.js"></script>
  <script type="text/javascript" src="/static/js/index.js"></script>
{% endblock %}
