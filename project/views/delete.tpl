<!DOCTYPE html>
<html>

<head>
    <title>SGFC >> Delete Files</title>
    <link rel="icon" type="image/ico" href="/favicon.ico" />
    <link href='/static/css/style.css' rel='stylesheet' type='text/css'>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body class="general">
    <table id="maintb" cellpadding="0" cellspacing="0">
        <tr>
            <td id="maintd">
                <header>
                    Delete Files
                </header>
                <div id="main">
                    <ul>
                    {% for message in messages %}
                        <li>{{ message }}</li>
                    {% endfor %}
                    </ul>
                    {% if key %}
                        <a href="/gallery/{{ key }}">Return to your gallery</a>
                    {% else %}
                        <a href="/">Return to homepage</a>
                    {% endif %}
                </div>
            </td>
        </tr>
    </table>
</body>

</html>