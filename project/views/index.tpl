{% extends "base.tpl" %}
{% block title %}Homepage{% endblock %}
{% block head %}
    <link href="/static/css/dropzone.css" rel="stylesheet">
{% endblock %}
{% block other %}
    <div id="overlay">
        <table id="overlaytb">
            <tr>
                <td style='vertical-align:middle'>
                    <div class='rules-hidden'>
                        <pre>
* filesize limit: 100MB
* pls no cp guise i.e. dont upload shit which is illegal, or will get me sued.
* all filestypes are allowed, except for viruses and illegal shit
* Logging policy: No IPs are stored. Ever.
* How upload logging works:
    - You upload file.
    - App receives file and inserts this info into database:
        * filename
        * file path
        * user id (either supplied or generated)
    - App spews upload info back at you
    - go on with your life doing whatever you do
* How viewing logging works:
    - Person opens link for file
    - If the file exists, serve it and increment hits column by 1.
    - thats it
* if you want a file removed for reasons (a valid reason please), shoot me an email at <a href='mailto:admin@sgfc.co'>admin@sgfc.co</a>, with the offending link and a reason why it should be gone.
* if you feel like poking around the source, visit <a href="http://github.com/SummerGlauFC/sgfcup">http://github.com/SummerGlauFC/sgfcup</a>
                            </pre>
                        <button type='button' class="toggle-rules">Hide Rules</button>
                    </div>
                </td>
            </tr>
        </table>
    </div>
    <div id="previews" class="dropzone-previews"></div>
{% endblock %}
{% block left %}
    <span>
        <h6>Pasting?</h6>
        <a href="/paste" data-icon="&#xf016;"></a>
    </span>
    <span>
        <h6>Looking at pics?</h6>
        <a href="/gallery/{{ key }}" data-icon="&#xf03e;">
            <strong class='locks' data-icon="&#xf023;"></strong>
            <span class='types'>private</span>
        </a>
    </span>
    <span>
        <h6>Need your keys for reasons?</h6>
        <a href="/keys" data-icon="&#xf084;"></a>
        or <a href="/settings" data-icon="&#xf013;"></a>
    </span>
    <button type='button' class="toggle-rules">Show Rules</button>
{% endblock %}
{% block content %}
    <div id="message"></div>
    <form id="my-awesome-dropzone" class="dropzone" action="/api/upload/file" method="post" enctype="multipart/form-data">
        <div id="dropped">
            <div>Drop your files here!</div>
        </div>
        <div id="fields">
            <div id="filess">
                <!-- <input type="file" name="files" id="file" /> -->
                Drop files <strong>here</strong>, or click to browse
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
                <label for="password">Password</label>&nbsp;
                <input type="password" size="20" value="{{ password }}" name="password" id="password" />
            </div>
        </div>
        <br />
        <input type="submit" name="submit" value="Upload" />
    </form>
{% endblock %}
{% block script %}
    <script type="text/javascript" src="/static/css/dropzone.js"></script>
    <script>
        $('.toggle-rules').on('click', function () {
            if ($("#overlay").is(':visible')) {
                $('.rules-hidden').fadeToggle(500);
                $('#overlay').delay(500).fadeToggle(500);
            } else {
                $('#overlay').fadeToggle(500);
                $('.rules-hidden').delay(600).fadeToggle(500);
            }
        });
        $('#clear-fields').on('click', function () {
            $('#key').get(0).setAttribute('value', ''); //this works
            $('#password').get(0).setAttribute('value', ''); //this works
        });
        $(document).ready(function () {
            $('#wrapper').equalHeight();
        });
        $(function () {
            $('#dropped').css('height', $("#main").height());
            $('#dropped div').css('height', $("#main").height());
            Dropzone.options.myAwesomeDropzone = { // The camelized version of the ID of the form element
                // The configuration we've talked about above
                url: "/api/upload/file",
                autoProcessQueue: false,
                uploadMultiple: false,
                previewsContainer: "#previews",
                parallelUploads: 2,
                maxFiles: 20,
                paramName: "files",
                clickable: "#filess",
                addRemoveLinks: true,
                // The setting up of the dropzone
                init: function () {
                    var myDropzone = this;
                    // First change the button to actually tell Dropzone to process the queue.
                    this.element.querySelector('input[name="submit"]').addEventListener("click", function (e) {
                        // Make sure that the form isn't actually being sent.
                        e.preventDefault();
                        e.stopPropagation();
                        myDropzone.processQueue();
                    });
                    // Listen to the sendingmultiple event. In this case, it's the sendingmultiple event instead
                    // of the sending event because uploadMultiple is set to true.
                    this.on("sending", function (file, xhr, formData) {
                        // Gets triggered when the form is actually being sent.
                        // Hide the success button or the complete form.
                    });
                    this.on("success", function (file, response) {
                        // Gets triggered when the files have successfully been sent.
                        // Redirect user or notify of success.
                        console.log(response);
                        console.log(file);
                        console.log(file.previewTemplate);
                        $('.dz-error-message span', file.previewTemplate).html('<a href="' + response.url + '">' + response.base + response.url + '</a>');
                        $('.dz-error-message', file.previewTemplate).css("opacity", 1);
                        myDropzone.processQueue();
                    });
                    this.on("error", function (file, response) {
                        // Gets triggered when there was an error sending the files.
                        // Maybe show form again, and notify user of error
                        console.log("error:");
                        console.log(file);
                        console.log(response);
                        $('.dz-error-message', file.previewTemplate).css("opacity", 1);
                        myDropzone.processQueue();
                    });
                }
            }
        });
    </script>
{% endblock %}
