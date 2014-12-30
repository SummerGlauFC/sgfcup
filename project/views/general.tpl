<!DOCTYPE html>
<html>

<head>
    <title>SGFC >> {{ title }}</title>
    <link rel="icon" type="image/ico" href="/favicon.ico" />
    <link href='/static/css/style.css' rel='stylesheet' type='text/css'>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style type="text/css">
        #main {
            text-align: center !important
        }
    </style>
</head>

<body class="general">
    <table id="maintb" cellpadding="0" cellspacing="0">
        <tr>
            <td id="maintd">
                <header>
                    {{ title }}
                </header>
                <div id="main">
                    {{ message }}
                </div>
            </td>
        </tr>
    </table>
</body>

</html>