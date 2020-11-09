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

{% macro login_form(form, show_clear=False, show_logged_in=True) %}
  <div id="identification">
    {% if current_user.is_authenticated and show_logged_in %}
      <p>Logged in as <a href="/gallery/{{ current_user.key }}">{{ current_user.key }}</a>.</p>
      <p><a id="logout" class="button" href="/logout">Sign out</a></p>
    {% else %}
      {% if show_clear %}
        <p>
          <small>
            You do not have to change these values.
            <br />
            Clear the fields to upload anonymously.
          </small>
          <br />
          <br />
          <button type='button' id="clear-fields">Clear Fields</button>
        </p>
      {% endif %}
      {{ errors(form.key) }}
      <p class="m-none">
        {{ form.key.label }}
        {{ form.key(size=20, autocomplete="username") }}
      </p>
      {{ errors(form.password) }}
      <p class="m-none">
        {{ form.password.label }}
        {{ form.password(size=20, autocomplete="current-password") }}
      </p>
      <p>
        <button type='button' id="login">Sign in</button>
      </p>
    {% endif %}
  </div>
{% endmacro %}

{% macro window_csrf(show_clear=False) %}
  <script type="text/javascript">
    window.CSRF_TOKEN = "{{ csrf_token() }}"
    window.SHOW_CLEAR = {{ "false" if not show_clear else "true" }}
  </script>
{% endmacro %}