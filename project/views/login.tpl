{% from "utils.tpl" import login_form with context %}
{{ login_form(form, show_clear=show_cleared) }}