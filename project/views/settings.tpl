<!-- settings.tpl -->
<form action="" method="POST">
{% for key, value in settings.iteritems() %}
<ul>
    {{ value.name }}:
    {% if value.type == "radio" %}
        {%- for option in value.options %}
            <li>
                <input type="radio" name="{{ key }}" value="{{ loop.index0 }}"
                {%- if value.value == loop.index0 %} checked {% endif -%}
                /> {{ option }}
            </li>
        {% endfor -%}
    {% else %}
        <li>
            <input type="{{ value.type }}" name="{{ key }}" value="{{ value.value }}" />
        </li>
    {% endif %}
</ul>
{% endfor %}
<input type="submit" value="Update Settings" />
</form>