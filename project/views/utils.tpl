{% macro errors(field, show_required=False) %}
  {% if field.errors %}
    <p class="{{ kwargs.pop("class", "m-none") }}">
      {% for error in field.errors %}
        <span style="color: red;">{{ error|e }}</span>
      {% endfor %}
    </p>
  {% endif %}
{% endmacro %}

{% macro flashed_messages(break=False) %}
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      <ul class="messages" style="padding-inline-start:0;">
        {% for category, message in messages %}
          <li class="{{ category }}">{{ message }}</li>
        {% endfor %}
      </ul>
      {% if break %}
        <hr />
      {% endif %}
    {% endif %}
  {% endwith %}
{% endmacro %}

{% macro login_status(show_button=False, next=request.path) %}
  <div id="identification">
    {% if current_user.is_authenticated %}
      <p>Logged in as <a href="/gallery/{{ current_user.key }}">{{ current_user.key }}</a>.</p>
      {% if show_button %}
        <p><a class="button" href="{{ url_for("static.logout", next=next) }}">Sign out</a></p>
      {% endif %}
    {% else %}
      {% if current_user.is_anonymous %}
        <p>Logged in anonymously.</p>
      {% else %}
        <p>Not logged in.</p>
      {% endif %}
      {% if show_button %}
        <p><a class="button" href="{{ url_for("static.login", next=next) }}">Sign in</a></p>
      {% endif %}
    {% endif %}
  </div>
{% endmacro %}

{% macro login_form(form, show_logged_in=True) %}
  <div id="identification">
    {% if current_user.is_authenticated and show_logged_in %}
      <p>Logged in as <a href="/gallery/{{ current_user.key }}">{{ current_user.key }}</a>.</p>
    {% else %}
      {{ errors(form.key, class="") }}
      <p class="m-none">
        {{ form.key.label }}
        {{ form.key(size=20, autocomplete="username") }}
      </p>
      {{ errors(form.password) }}
      <p class="m-none">
        {{ form.password.label }}
        {{ form.password(size=20, autocomplete="current-password") }}
      </p>
    {% endif %}
  </div>
{% endmacro %}

{% macro window_csrf() %}
  <script type="text/javascript">
    window.CSRF_TOKEN = "{{ csrf_token() }}"
  </script>
{% endmacro %}