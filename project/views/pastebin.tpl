<!DOCTYPE html>
<html>

<head>
    <title>SGFC | Pastebin</title>
    <link href="/favicon.ico" rel="icon" type="image/x-icon" />
    <link href="//cdnjs.cloudflare.com/ajax/libs/normalize/3.0.2/normalize.min.css" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href='/static/css/main.css' rel='stylesheet' type='text/css'>
    <style type="text/css">
        h2, #identification {
            margin-bottom: 1em;
        }
        #paste_body {
            height: 392px;
            width: 392px;
        }
        #details {
            display: inline-block;
            margin: 0 auto;
            text-align: left;
        }
        h3 {
            margin: 0 0 15px;
        }
        #details > input {
            margin-bottom: 5px;
        }
        #identification label {
            margin: 5px 5px 5px 0;
            width: 40px;
        }
        #maintb {
            width: 750px;
        }
        #main {
            height: 428px;
        }
    </style>
</head>

<body class="index">
        <table id="maintb" cellpadding="0" cellspacing="0">
            <tr>
                <td id="maintd">
                    <form action="/api/upload/paste" method="post">
                        <div id="wrapper" class='cf'>
                            <header>
                                <h2>SGFC File Upload</h2>
                                <div class='cf'>
                                    <h3>Pastebin</h3>
                                    <div id="details">
                                        <label>Name:</label>
                                        <input type="text" name="paste_name" id="paste_name" placeholder="(optional)" />
                                        <br />
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
                                            <option value="nginx">Nginx Conf</option>
                                            <option value="php">PHP</option>
                                            <option value="python">Python</option>
                                            <option value="text" selected>Plain text</option>
                                        </select>
                                    </div>
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
                                        <label for="password">Pass</label>&nbsp;
                                        <input type="password" size="20" value="{{ password }}" name="password" id="password" />
                                        <br /><br />
                                        <input type="submit" name="submit" value="Paste" />
                                    </div>
                                </div>
                            </header>
                            <div id="main">
                                <table id="overlaytb">
                                    <tr>
                                        <td style='vertical-align:middle'>
                                            <textarea tabindex="20" name="paste_body" id="paste_body" class="pastebox"></textarea>
                                            <div id="message" style="display: none">Uploading...</div>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </form>
                </td>
            </tr>
        </table>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js" type="text/javascript"></script>
    <script src="/static/js/pastebin.js" type="text/javascript"></script>
</body>

</html>