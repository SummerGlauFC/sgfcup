<!-- settings.tpl -->

{% for key, value in settings.iteritems() %}
<ul>
    {{ key }}:
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
            <input type="text" name="{{ key }}" value="{{ value.value }}" />
        </li>
    {% endif %}
</ul>
{% endfor %}
