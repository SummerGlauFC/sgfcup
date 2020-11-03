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

{% macro login_form(form, show_clear=False) %}
  <div id="identification">
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
      {{ form.key(size=20) }}
    </p>
    {{ errors(form.password) }}
    <p class="m-none">
      {{ form.password.label }}
      {{ form.password(size=20) }}
    </p>
  </div>
{% endmacro %}