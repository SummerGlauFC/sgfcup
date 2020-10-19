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
    <p class="m-none">
      <label for="key">User</label>
      <input type="text" size="20" name="key" id="key" value="{{ key }}" />
    </p>
    <p class="m-none">
      <label for="password">Password</label>
      <input type="password" size="20" name="password" id="password" value="{{ password }}" />
    </p>
  </div>
{% endmacro %}