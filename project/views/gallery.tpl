{% macro render_pagination(pagination) %}
  {% if pagination.has_prev %}
    <a class="prev" href="{{ url_for_page(pagination.page - 1) }}" data-page="{{ page }}">&laquo;</a>
  {% endif %}
  {% for page in pagination.iter_pages() %}
    {% if page %}
      <a href="{{ url_for_page(page) }}"
         data-page="{{ page }}"
          {% if page == pagination.page %} class="active" {% endif %}
      >
        {{ page }}
      </a>
    {% else %}
      <a><span style="color: #090910"> .. </span></a>
    {% endif %}
  {% endfor %}
  {% if pagination.has_next %}
    <a class="next" href="{{ url_for_page(pagination.page + 1) }}" data-page="{{ page }}">&raquo;</a>
  {% endif %}
{% endmacro %}
{% macro write_ext(file) -%}
  {%- if info.show_ext == 1 -%}
    {{ file.url }}{{ file.ext }}
  {%- elif info.show_ext == 2 -%}
    {{ file.url }}/{{ file.original }}
  {%- else -%}
    {{ file.url }}
  {%- endif -%}
{%- endmacro %}
{% if not error %}
  {% if not info.pjax %}
    <!DOCTYPE html>
    <html>
    <head>
      <link rel="icon" type="image/x-icon"
            href="data:image/x-icon;base64,AAABAAEAEBAQAAAAAAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAA//36AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAREREREQAAABERERERAAAAAAAAAAAAAAAAABEAAAAAAAABERAAAAAAABEREQAAAAABEREREAAAABERERERAAAAAAEREAAAAAAAAREQAAAAAAABERAAAAAAAAEREAAAAAAAAREQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" />
      <link href='/static/css/main.css' rel='stylesheet' type='text/css'>
      <link href='/static/css/gallery.css' rel='stylesheet' type='text/css'>
      <link href="/static/css/loader.css" rel="stylesheet" type='text/css' />
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>SGFC | {{ info.key }}'{% if info.key[-1] != "s" %}s{% endif %} Gallery</title>
    </head>

    <body class="gallery">
    <div id="container">
    <header>
      <a href="/">Gallery</a>
    </header>
    <div id="main" class="wrapper">
  {% endif %}
<h2>{{ info.usage }} used ({{ info.entries }} items)</h2>
<div class="row pages" style="position:relative;">
  {{ render_pagination(info.pages) }}
</div>
<script>
  window.current_page = {{ info.pages.page }};
</script>
<div class="row top">
  <form class="sort-form small" action="" method="get">
    <div>
      <select name="sort" id="sort">
        {% for mode in info.sort.list %}
          <option value="{{ loop.index0 }}" {% if loop.index0 == info.sort.current %}selected{% endif %}>
            {{ mode[0] }}
          </option>
        {% endfor %}
      </select>
      <input type="submit" value="Sort" />
    </div>
    <div>
      <select class="search-mode" name="in">
        {% for mode in info.search.modes %}
          <option value="{{ loop.index0 }}" {% if loop.index0 == info.search.in -%} selected {%- endif %}>
            {{ mode[0] }}
          </option>
        {% endfor %}
      </select>
      matches
      <input class="search-query" type="text" name="query" placeholder="search query" value="{{ info.search.query }}" />
      <input type="submit" value="Search" />
      <div>
        <label>
          <input type="checkbox"
                 name="case" value="1" {% if info.search.case %}checked{% endif %} />
          Case-sensitive search
        </label>
      </div>
    </div>
  </form>
</div>
<div id='loader' style="display:none;">
  <div class="lds-spinner">
    <div></div>
    <div></div>
    <div></div>
    <div></div>
    <div></div>
    <div></div>
    <div></div>
    <div></div>
    <div></div>
    <div></div>
    <div></div>
    <div></div>
  </div>
</div>
<form action="/gallery/delete" method="post" id="main_form"
      onsubmit="return confirm('Do you really want to delete your files?');">
  <input type="hidden" name="key" value="{{ info.key }}" />
  {% for file in info.files %}
    <div class="file-container">
      <div class="file-thumbnail"
           {% if file.type == types.IMAGE %}style="background-image: url('/api/thumb/{{ write_ext(file) }}')"{% endif %}
      >
        {% if file.type == types.FILE %}
          <a class="file-thumbnail-link file-thumbnail-type"
             title="{{ file.original|e }}"
             href="/{{ write_ext(file) }}">
          FILE
        {% elif file.type == types.IMAGE %}
          <a class="file-thumbnail-link" target="_blank"
             title="{{ file.original|e }}"
             href="/{{ write_ext(file) }}">
        {% elif file.type == types.PASTE %}
          <a title="{{ file.name }}" href="/paste/{{ file.url }}"
             class="file-thumbnail-link">
          {% set split_paste = file.content.split("\n") %}
          <pre class="file-thumbnail-paste">{{ "\n".join(split_paste[0:16])|e }}{% if split_paste|length >= 16 -%}
            ... Only 16 lines shown here{% endif %}</pre>
        {% endif %}
        </a>
      </div>
      <div class="file-info">
        <label for="delete_this">
          <input type="checkbox" class="file-delete-checkbox" name="delete_this" value="{{ file.url }}" />
          {% if file.type == types.PASTE %}
            Paste: <a title="{{ file.url }}" href="/paste/{{ file.url }}">
            {{ hl(file.name|e) }}
            {% if file.name != file.url %}({{ file.url }}){% endif %}
          </a>
          {% else %}
            <a title="{{ file.url }}" href="/{{ write_ext(file) }}">{{ hl(file.original|e) }}</a>
          {% endif %}
        </label>
      </div>
      <div class="file-info details">
        <span style="color:rgba(0, 0, 0, 0.5);">Size:</span>
        {% if file.type == types.IMAGE %}
          {{ file.size }} ({{ file.resolution[0] }}x{{ file.resolution[1] }})
        {% elif file.type == types.PASTE %}
          {{ file.size }} lines
        {% else %}
          {{ file.size }}
        {% endif %}
        <br />
        <span
            style="color:rgba(0, 0, 0, 0.5);">Uploaded:</span> {{ file.time.timestamp }}
        <br />
        <span style="color:rgba(0, 0, 0, 0.5);">Hits:</span> {{ file.hits }}
      </div>
    </div>
  {% endfor %}
  <div class="pages row bottom">
    {{ render_pagination(info.pages) }}
  </div>
  <div class="row small">
    <p>password:
      <input type="password" value="" name="password" placeholder="key password" />
      &nbsp;&nbsp;&nbsp;
      <input type="submit" name="type" value="Delete Selected" />
      &nbsp;&nbsp;&nbsp;
      <input type="submit" name="type" value="Delete All" />
    </p>
  </div>
</form>
<div class="row padded">
  <form action="/gallery/delete/advanced" method="get" class="main_form">
    <input type="submit" value="Advanced Delete..." />
  </form>
</div>
{% if not info.pjax %}
  </div>
  </div>
  <script src="/static/js/base.js"></script>
  <script src="/static/js/gallery.js"></script>
  </body>
  </html>
{% endif %}
{% else %}
  <!DOCTYPE HTML>
  <html>
  <head>
    <title>Error: {{ error }}</title>
    <style type="text/css">
        html {
            background-color: #eee;
            font-family: -apple-system, BlinkMacSystemFont, avenir next, avenir, helvetica neue, helvetica, Ubuntu, roboto, noto, segoe ui, arial, sans-serif;
        }

        body {
            background-color: #fff;
            border: 1px solid #ddd;
            padding: 15px;
            margin: 15px;
        }

        pre {
            background-color: #eee;
            border: 1px solid #ddd;
            padding: 5px;
        }
    </style>
  </head>
  <body>
  <h1>Error: {{ error }}</h1>
  <p>Try again later.</p>
  </body>
  </html>
{% endif %}