{% macro login_form(key="", password="", show_clear=False) %}
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
    <label for="key">User</label>&nbsp;
    <input type="text" size="20" name="key" id="key" value="{{ key }}" />
    <br />
    <label for="password">Password</label>&nbsp;
    <input type="password" size="20" name="password" id="password" value="{{ password }}" />
  </div>
{% endmacro %}