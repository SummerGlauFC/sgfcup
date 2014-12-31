<!DOCTYPE html>
<html>

<head>
    <title>SGFC >> Pastebin</title>
    <link rel="icon" type="image/ico" href="/favicon.ico" />
    <link href='/static/css/style.css' rel='stylesheet' type='text/css'>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body class="pastebin">
    <table id="maintb" cellpadding="0" cellspacing="0">
        <tr>
            <td id="maintd">
                <header>
                    Pastebin
                </header>
                <div id="main">
                    <form action="/api/upload/paste" method="post">
                        <label>Name:</label>
                        <input type="text" name="paste_name" id="paste_name" placeholder="(optional)" />
                        <label for="lang">Language:</label>
                        <select name="lang" id="lang">
                            <option value="bbcode">BBCode</option>
                            <option value="bash">Bash</option>
                            <option value="bat">Batchfile</option>
                            <option value="brainfuck">Brainfuck</option>
                            <option value="c">C</option>
                            <option value="csharp">C#</option>
                            <option value="cpp">C++</option>
                            <option value="css">CSS</option>
                            <option value="diff">Diff</option>
                            <option value="html">HTML</option>
                            <option value="html+php">HTML+PHP</option>
                            <option value="ini">INI</option>
                            <option value="irc">IRC logs</option>
                            <option value="java">Java</option>
                            <option value="js">JavaScript</option>
                            <option value="lua">Lua</option>
                            <option value="mysql">MySQL</option>
                            <option value="nginx">Nginx configuration file</option>
                            <option value="php">PHP</option>
                            <option value="python">Python</option>
                            <option value="text" selected>Plain text</option>
                        </select>
                        <br />
                        <br />

                        <div id="filess">
                            <textarea tabindex="20" rows="22" name="paste_body" id="paste_body" cols="40" class="pastebox"></textarea>
                        </div>
                        <br />
                        <input type="submit" name="submit" value="Paste" />
                        <br />
                        <br />
                        <div id="identification">
                            <p class='unimportant'>You do not have to change these values.
                                <br />Clear the fields to upload anonymously.
                                <br />
                                <br />
                                <button type='button' id="clear-fields">Clear Fields</button>
                            </p>
                            <label for="key">Key</label>&nbsp;
                            <input type="text" size="20" value="{{ key }}" name="key" id="key" />
                            <br />
                            <label for="password">Password</label>&nbsp;
                            <input type="password" size="20" value="{{ password }}" name="password" id="password" />
                        </div>
                    </form>
                    <div id="message" style="display: none">Uploading...</div>
                </div>
            </td>
        </tr>
    </table>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js" type="text/javascript"></script>
    <script>
        $('#clear-fields').on('click', function () {
            $('#key').get(0).setAttribute('value', ''); //this works
            $('#password').get(0).setAttribute('value', ''); //this works
        });
        $("form").submit(function () {
            var url = "/api/upload/paste"; // the script where you handle the form input.
            $("form").hide();
            $.ajax({
                type: "POST",
                url: url,
                data: $("form").serialize(), // serializes the form's elements.
                success: function (data) {
                    if (data.success) {
                        $("#message").html('<a href="' + data.url + '">' + data.base + data.url + '</a>');
                    } else {
                        $("#message").html(data.error);
                    }
                    $("#message").fadeIn(250);
                }
            });
            return false; // avoid to execute the actual submit of the form.
        });
    </script>
</body>

</html>