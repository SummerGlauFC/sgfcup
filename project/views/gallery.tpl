{% from "utils.tpl" import login_status with context %}
{% macro render_pagination(pagination) %}
  {% if pagination.has_prev %}
    <a class="prev" href="{{ url_for_page(pagination.page - 1) }}" data-page="{{ page }}">&laquo;</a>
  {% endif %}
  {% for page in pagination.iter_pages() %}
    {% if page %}
      <a href="{{ url_for_page(page) }}"
         data-page="{{ page }}" {% if page == pagination.page %}class="active"{% endif %}>
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
{% macro file_url(file) -%}
  {%- if show_ext == 1 -%}
    {{ file.url }}{{ file.ext }}
  {%- elif show_ext == 2 -%}
    {{ file.url }}/{{ file.original }}
  {%- else -%}
    {{ file.url }}
  {%- endif -%}
{%- endmacro %}
{% if not xhr %}
<!DOCTYPE html>
<html>
<head>
  <link rel="icon" type="image/x-icon"
        href="data:image/x-icon;base64,AAABAAEAEBAQAAAAAAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAA//36AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAREREREQAAABERERERAAAAAAAAAAAAAAAAABEAAAAAAAABERAAAAAAABEREQAAAAABEREREAAAABERERERAAAAAAEREAAAAAAAAREQAAAAAAABERAAAAAAAAEREAAAAAAAAREQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" />
  <link href='/static/css/main.css' rel='stylesheet' type='text/css'>
  <link href='/static/css/gallery.css' rel='stylesheet' type='text/css'>
  <link href="/static/css/loader.css" rel="stylesheet" type='text/css' />
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SGFC | {{ key }}'{% if key[-1] != "s" %}s{% endif %} Gallery</title>
</head>

<body class="gallery">
  <div id="container">
    <header>
      <a href="/">Gallery</a>
    </header>
    <div id="main" class="wrapper">
      <h2>{{ usage }} used ({{ entries }} items)</h2>
      <div class="row top">
        <form class="sort-form" action="" method="get">
          <div>
            {{ form_filter.sort() }}
            <input type="submit" value="Sort">
          </div>
          <div>
            {{ form_filter.filter() }}
            <input type="submit" value="Filter">
          </div>
          <div>
            {{ form_filter.in_() }}
            <small>matches</small>
            {{ form_filter.query(class="search-query") }}
            <input type="submit" value="Search">
            <div>
              {{ form_filter.case(value="1") }} <small>{{ form_filter.case.label }}</small>
            </div>
          </div>
        </form>
      </div>
      <form action="/gallery/delete" method="post" id="main_form"
            onsubmit="return confirm('Do you really want to delete your files?');">
        <div id="replace-content">
          {% endif %}
          <div class="row pages top m-b" style="position:relative;">
            {{ render_pagination(pages) }}
          </div>
          <div id='loader' style="display:none;" data-saved-display="flex">
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
          <div id="fader"
           {%- if xhr %}style="transition:opacity 100ms ease 0s;opacity:0;pointer-events:inherit;"
           data-saved-display="block"{% endif %}
          >
            {% for file in files %}
              <div class="file-container">
                <div class="file-thumbnail"
                 {% if file.type == file_type.IMAGE %}style="background-image: url('/api/thumb/{{ file_url(file) }}')"{% endif %}
                >
                  {% if file.type == file_type.FILE %}
                    <a class="file-thumbnail-link file-thumbnail-type"
                       title="{{ file.original }}"
                       href="/{{ file_url(file) }}">
                    FILE
                  {% elif file.type == file_type.IMAGE %}
                    <a class="file-thumbnail-link" target="_blank"
                       title="{{ file.original }}"
                       href="/{{ file_url(file) }}">
                  {% elif file.type == file_type.PASTE %}
                    <a title="{{ file.name }}" href="/paste/{{ file.url }}"
                       class="file-thumbnail-link">
                    {% set split_paste = file.content.split("\n") %}
                    <pre class="file-thumbnail-paste">{{ "\n".join(split_paste[0:16]) }}{% if split_paste|length >= 16 -%}
                      ... Only 16 lines shown here{% endif %}</pre>
                  {% endif %}
                  </a>
                </div>
                <div class="file-info">
                  <label for="delete_this">
                    <input type="checkbox" class="file-delete-checkbox" name="delete_this" value="{{ file.url }}" />
                    {% set name = file.name if file.type == file_type.PASTE else file.original %}
                    {% set hl_name = hl(name|e) if not search["in"] else name|e %}
                    {% if file.type == file_type.PASTE %}
                      Paste: <a title="{{ file.url }}" href="/paste/{{ file.url }}">
                      {{ hl_name|safe }}
                    </a>
                    {% else %}
                      <a title="{{ file.url }}" href="/{{ file_url(file) }}">{{ hl_name|safe }}</a>
                    {% endif %}
                  </label>
                </div>
                <div class="file-info details">
                  <span style="color:rgba(0, 0, 0, 0.5);">Size:</span>
                  {% if file.type == file_type.IMAGE %}
                    {{ file.size }} ({{ file.resolution[0] }}x{{ file.resolution[1] }})
                  {% elif file.type == file_type.PASTE %}
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
          </div>
          <div class="row pages bottom">
            {{ render_pagination(pages) }}
          </div>
          {% if not xhr %}
        </div>
        {% if current_user.is_authenticated and current_user.key == key %}
          <div class="row delete-options">
            {{ form_delete.csrf_token }}
            <small>{{ login_status(show_button=False) }}</small>
            {{ form_delete.delete_selected() }}
            {{ form_delete.delete_all() }}
          </div>
        {% endif %}
      </form>
      {% if current_user.is_authenticated and current_user.key == key %}
        <div class="row padded">
          <form action="/gallery/delete/advanced" method="get" class="main_form">
            <input type="submit" value="Advanced Delete..." />
          </form>
        </div>
      {% endif %}
    </div>
  </div>
  <script type="text/javascript">
    window.current_page = "{{ pages.page }}"
  </script>
  <script src="/static/js/base.js"></script>
  <script src="/static/js/gallery.js"></script>
</body>
</html>
{% endif %}