<!DOCTYPE html>
<html>

<head>
    <title>SGFC | {% block title %}{% endblock %}</title>
    <link href="/favicon.ico" rel="icon" type="image/x-icon" />
    <link href="//cdnjs.cloudflare.com/ajax/libs/normalize/3.0.2/normalize.min.css" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {% include "main.css" %}
    <style>{% block css %}{% endblock %}</style>
    {% block head %}{% endblock %}
</head>

<body class="index">
    {% block other %}{% endblock %}
    <table id="maintb" cellpadding="0" cellspacing="0">
        <tr>
            <td id="maintd">
                <div id="wrapper" class='cf'>
                    <header>
                        <h2>SGFC File Upload</h2>
                        <div class='cf'>
                        {% block left %}
                            <h3>{{ self.title() }}</h3>
                        {% endblock %}
                        </div>
                    </header>
                    <div id="main">
                        <table id="overlaytb">
                            <tr>
                                <td style='vertical-align:middle'>
                                {% block content %}{% endblock %}
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>
                <div id="previews" class="dropzone-previews"></div>
            </td>
        </tr>
    </table>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js" type="text/javascript"></script>
    <script>
        $.fn.equalHeight = function () {
            var max = 0;
            return this.children()
                .each(function () {
                    var height = $(this).height();
                    max = height > max ? height : max;
                })
                .height(max);
        };
        $(window).resize(function () {
            $('#wrapper').equalHeight();
        });
        $(document).ready(function () {
            $('#wrapper').equalHeight();
        });
    </script>
    {% block script %}{% endblock %}
</body>

</html>