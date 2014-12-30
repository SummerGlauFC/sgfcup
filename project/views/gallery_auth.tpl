<!DOCTYPE html>
<html>

<head>
    <title>SGFC >> Authenticate</title>
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
                    Authenticate
                </header>
                <div id="main">
                    You need to authenticate to view this gallery.
                    <br/>
                    <br />
                    <form action="" method="post">
                        <input type="password" name="authcode" placeholder="gallery password" />
                        <br />
                        <br />Remember this key?
                        <br />
                        <input type="radio" name="remember" value="1" id="pub" checked>
                        <label>Yes</label>
                        <input type="radio" name="remember" value="0" id="priv">
                        <label>No</label>
                        <br />
                        <br />
                        <input value="Submit" type="submit" />
                    </form>
                </div>
            </td>
        </tr>
    </table>
</body>

</html>