{% extends "base.tpl" %}
{% block title %}Homepage{% endblock %}
{% block head %}
{% endblock %}
{% block css %}
    .dropzone,.dropzone *,.dropzone-previews,.dropzone-previews *{box-sizing:border-box}.dropzone{position:relative;padding:1em;border:0;background:0}.dropzone.dz-clickable{cursor:pointer}.dropzone.dz-clickable .dz-message,.dropzone.dz-clickable .dz-message span{cursor:pointer}.dropzone.dz-clickable *{cursor:default}.dropzone .dz-message{display:none;opacity:1}.dropzone.dz-drag-hover{border-color:rgba(0,0,0,0.15);background:rgba(0,0,0,0.04)}.dropzone.dz-started .dz-message{display:none}.dropzone-previews{text-align:center}.dropzone .dz-preview,.dropzone-previews .dz-preview{display:inline-block;position:relative;margin:6px;padding:6px;border:1px solid #acacac;vertical-align:top;background:rgba(255,255,255,0.8)}.dropzone .dz-preview.dz-file-preview [data-dz-thumbnail],.dropzone-previews .dz-preview.dz-file-preview [data-dz-thumbnail]{display:none}.dropzone .dz-preview .dz-details,.dropzone-previews .dz-preview .dz-details{position:relative;width:100px;height:100px;margin:0 auto 22px;padding:5px;background:none repeat scroll 0 0 #ebebeb}.dropzone .dz-preview .dz-details .dz-filename,.dropzone-previews .dz-preview .dz-details .dz-filename{height:100%;overflow:hidden}.dropzone .dz-preview .dz-details img,.dropzone-previews .dz-preview .dz-details img{position:absolute;top:0;left:0;width:100px;height:100px}.dropzone .dz-preview .dz-details .dz-size,.dropzone-previews .dz-preview .dz-details .dz-size{height:28px;line-height:28px;absolute:bottom -28px left 3px}.dropzone .dz-preview.dz-error .dz-error-mark,.dropzone-previews .dz-preview.dz-error .dz-error-mark{display:block}.dropzone .dz-preview.dz-success .dz-success-mark,.dropzone-previews .dz-preview.dz-success .dz-success-mark{display:block}.dropzone .dz-preview:hover .dz-details img,.dropzone-previews .dz-preview:hover .dz-details img{display:none}.dropzone .dz-preview .dz-success-mark,.dropzone-previews .dz-preview .dz-success-mark,.dropzone .dz-preview .dz-error-mark,.dropzone-previews .dz-preview .dz-error-mark{display:none;position:absolute;top:-10px;right:-10px;width:40px;height:40px;text-align:center;font-size:30px}.dropzone .dz-preview .dz-success-mark,.dropzone-previews .dz-preview .dz-success-mark{color:#8cc657}.dropzone .dz-preview .dz-error-mark,.dropzone-previews .dz-preview .dz-error-mark{color:#ee162d}.dropzone .dz-preview .dz-progress,.dropzone-previews .dz-preview .dz-progress{display:none;position:absolute;top:100px;right:6px;left:6px;height:6px;background:#d7d7d7}.dropzone .dz-preview .dz-progress .dz-upload,.dropzone-previews .dz-preview .dz-progress .dz-upload{display:block;position:absolute;top:0;bottom:0;left:0;width:0;background-color:#8cc657}.dropzone .dz-preview.dz-processing .dz-progress,.dropzone-previews .dz-preview.dz-processing .dz-progress{display:block}.dropzone .dz-preview .dz-error-message,.dropzone-previews .dz-preview .dz-error-message{display:none;z-index:500;padding:8px 10px;max-width:500px;min-width:140px;color:#800;background:rgba(245,245,245,0.8);absolute:top -5px left -20px}.dropzone .dz-preview:hover.dz-error .dz-error-message,.dropzone-previews .dz-preview:hover.dz-error .dz-error-message{display:block}.dropzone{padding:23px;min-height:270px;border:0;-webkit-border-radius:3px;border-radius:3px;background:0}.dropzone .dz-default.dz-message{position:absolute;top:50%;left:50%;width:428px;height:123px;margin-top:-61.5px;margin-left:-214px;opacity:1;background-image:url(../images/spritemap.png);background-position:0 0;background-repeat:no-repeat;-webkit-transition:opacity 0.3s ease-in-out;-moz-transition:opacity 0.3s ease-in-out;-ms-transition:opacity 0.3s ease-in-out;-o-transition:opacity 0.3s ease-in-out;transition:opacity 0.3s ease-in-out;-ms-filter:none;filter:none}@media all and(-webkit-min-device-pixel-ratio:1.5),(min--moz-device-pixel-ratio:1.5),(-o-min-device-pixel-ratio:1.5/1),(min-device-pixel-ratio:1.5),(min-resolution:138dpi),(min-resolution:1.5dppx){.dropzone .dz-default.dz-message{background-image:url(../images/spritemap@2x.png);-webkit-background-size:428px 406px;-moz-background-size:428px 406px;background-size:428px 406px}}.dropzone .dz-default.dz-message span{display:none}.dropzone.dz-square .dz-default.dz-message{width:268px;height:174px;margin-top:-87px;margin-left:-134px;background-position:0 -123px}.dropzone.dz-drag-hover .dz-message{opacity:0.15;-ms-filter:"progid:DXImageTransform.Microsoft.Alpha(Opacity=15)";filter:alpha(opacity=15)}.dropzone.dz-started .dz-message{display:block;opacity:0;-ms-filter:"progid:DXImageTransform.Microsoft.Alpha(Opacity=0)";filter:alpha(opacity=0)}.dropzone .dz-preview,.dropzone-previews .dz-preview{font-size:14px;-webkit-box-shadow:1px 1px 4px rgba(0,0,0,0.16);box-shadow:1px 1px 4px rgba(0,0,0,0.16)}.dropzone .dz-preview.dz-image-preview:hover .dz-details img,.dropzone-previews .dz-preview.dz-image-preview:hover .dz-details img{display:block;opacity:0.1;-ms-filter:"progid:DXImageTransform.Microsoft.Alpha(Opacity=10)";filter:alpha(opacity=10)}.dropzone .dz-preview.dz-success .dz-success-mark,.dropzone-previews .dz-preview.dz-success .dz-success-mark{opacity:1;-ms-filter:none;filter:none}.dropzone .dz-preview.dz-error .dz-error-mark,.dropzone-previews .dz-preview.dz-error .dz-error-mark{opacity:1;-ms-filter:none;filter:none}.dropzone .dz-preview.dz-error .dz-progress .dz-upload,.dropzone-previews .dz-preview.dz-error .dz-progress .dz-upload{background:#ee1e2d}.dropzone .dz-preview .dz-error-mark,.dropzone-previews .dz-preview .dz-error-mark,.dropzone .dz-preview .dz-success-mark,.dropzone-previews .dz-preview .dz-success-mark{display:block;opacity:0;background-image:url(//raw.githubusercontent.com/enyo/dropzone/master/downloads/images/spritemap.png);background-repeat:no-repeat;-webkit-transition:opacity 0.4s ease-in-out;-moz-transition:opacity 0.4s ease-in-out;-ms-transition:opacity 0.4s ease-in-out;-o-transition:opacity 0.4s ease-in-out;transition:opacity 0.4s ease-in-out;-ms-filter:"progid:DXImageTransform.Microsoft.Alpha(Opacity=0)";filter:alpha(opacity=0)}.dz-preview.dz-image-preview{width:auto}@media all and(-webkit-min-device-pixel-ratio:1.5),(min--moz-device-pixel-ratio:1.5),(-o-min-device-pixel-ratio:1.5/1),(min-device-pixel-ratio:1.5),(min-resolution:138dpi),(min-resolution:1.5dppx){.dropzone .dz-preview .dz-error-mark,.dropzone-previews .dz-preview .dz-error-mark,.dropzone .dz-preview .dz-success-mark,.dropzone-previews .dz-preview .dz-success-mark{background-image:url(../images/spritemap@2x.png);-webkit-background-size:428px 406px;-moz-background-size:428px 406px;background-size:428px 406px}}.dropzone .dz-preview .dz-error-mark span,.dropzone-previews .dz-preview .dz-error-mark span,.dropzone .dz-preview .dz-success-mark span,.dropzone-previews .dz-preview .dz-success-mark span{display:none}.dropzone .dz-preview .dz-error-mark,.dropzone-previews .dz-preview .dz-error-mark{background-position:-268px -123px}.dropzone .dz-preview .dz-success-mark,.dropzone-previews .dz-preview .dz-success-mark{background-position:-268px -163px}.dropzone .dz-preview .dz-progress .dz-upload,.dropzone-previews .dz-preview .dz-progress .dz-upload{position:absolute;top:0;left:0;width:0;height:100%;-webkit-border-radius:2px;border-radius:2px;background-image:url(../images/spritemap.png);background-position:0 -400px;background-repeat:repeat-x;-webkit-animation:loading 0.4s linear infinite;-moz-animation:loading 0.4s linear infinite;-o-animation:loading 0.4s linear infinite;animation:loading 0.4s linear infinite;-webkit-transition:width 0.3s ease-in-out;-moz-transition:width 0.3s ease-in-out;-ms-transition:width 0.3s ease-in-out;-o-transition:width 0.3s ease-in-out;transition:width 0.3s ease-in-out;-ms-animation:loading 0.4s linear infinite}@media all and(-webkit-min-device-pixel-ratio:1.5),(min--moz-device-pixel-ratio:1.5),(-o-min-device-pixel-ratio:1.5/1),(min-device-pixel-ratio:1.5),(min-resolution:138dpi),(min-resolution:1.5dppx){.dropzone .dz-preview .dz-progress .dz-upload,.dropzone-previews .dz-preview .dz-progress .dz-upload{background-image:url(../images/spritemap@2x.png);-webkit-background-size:428px 406px;-moz-background-size:428px 406px;background-size:428px 406px}}.dropzone .dz-preview.dz-success .dz-progress,.dropzone-previews .dz-preview.dz-success .dz-progress{display:block;opacity:0;-webkit-transition:opacity 0.4s ease-in-out;-moz-transition:opacity 0.4s ease-in-out;-ms-transition:opacity 0.4s ease-in-out;-o-transition:opacity 0.4s ease-in-out;transition:opacity 0.4s ease-in-out;-ms-filter:"progid:DXImageTransform.Microsoft.Alpha(Opacity=0)";filter:alpha(opacity=0)}.dropzone .dz-preview .dz-error-message,.dropzone-previews .dz-preview .dz-error-message{display:block;opacity:0;-webkit-transition:opacity 0.3s ease-in-out;-moz-transition:opacity 0.3s ease-in-out;-ms-transition:opacity 0.3s ease-in-out;-o-transition:opacity 0.3s ease-in-out;transition:opacity 0.3s ease-in-out;-ms-filter:"progid:DXImageTransform.Microsoft.Alpha(Opacity=0)";filter:alpha(opacity=0)}.dropzone .dz-preview:hover.dz-error .dz-error-message,.dropzone-previews .dz-preview:hover.dz-error .dz-error-message{opacity:1;-ms-filter:none;filter:none}.dropzone a.dz-remove,.dropzone-previews a.dz-remove{display:block;margin-top:0;padding:4px 5px;border:1px solid #eee;-webkit-border-radius:2px;border-radius:2px;text-align:center;text-decoration:none;color:#aaa;background-image:-webkit-linear-gradient(top,#fafafa,#eee);background-image:-moz-linear-gradient(top,#fafafa,#eee);background-image:-o-linear-gradient(top,#fafafa,#eee);background-image:-ms-linear-gradient(top,#fafafa,#eee);background-image:linear-gradient(to bottom,#fafafa,#eee)}.dropzone a.dz-remove:hover,.dropzone-previews a.dz-remove:hover{color:#666}@-moz-keyframes loading{from{background-position:0 -400px}to{background-position:-7px -400px}}@-webkit-keyframes loading{from{background-position:0 -400px}to{background-position:-7px -400px}}@-o-keyframes loading{from{background-position:0 -400px}to{background-position:-7px -400px}}@keyframes loading{from{background-position:0 -400px}to{background-position:-7px -400px}}
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
    <form id="my-awesome-dropzone" action="/api/upload/file" method="post" enctype="multipart/form-data">
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
    <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/dropzone/3.11.1/dropzone.min.js"></script>
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
            $('#key').get(0).setAttribute('value', '');
            $('#password').get(0).setAttribute('value', '');
        });
        $(document).ready(function () {
            $('#wrapper').equalHeight();
        });
        $(function () {
            $('#dropped').css('height', $("#main").height());
            $('#dropped div').css('height', $("#main").height());
            $('#my-awesome-dropzone').dropzone({
                url: "/api/upload/file",
                autoProcessQueue: false,
                uploadMultiple: false,
                previewsContainer: "#previews",
                parallelUploads: 2,
                maxFiles: 1000,
                paramName: "files",
                clickable: "#filess",
                addRemoveLinks: true,
                init: function () {
                    var myDropzone = this;
                    this.element.querySelector('input[name="submit"]').addEventListener("click", function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                        myDropzone.processQueue();
                    });
                    this.on("sending", function (file, xhr, formData) {
                    });
                    this.on("success", function (file, response) {
                        console.log(response);
                        console.log(file);
                        console.log(file.previewTemplate);
                        $('.dz-error-message span', file.previewTemplate).html('<a href="' + response.url + '">' + response.base + response.url + '</a>');
                        $('.dz-error-message', file.previewTemplate).css("opacity", 1);
                        myDropzone.processQueue();
                    });
                    this.on("error", function (file, response) {
                        console.log("error:");
                        console.log(file);
                        console.log(response);
                        $('.dz-error-message', file.previewTemplate).css("opacity", 1);
                        myDropzone.processQueue();
                    });
                }
            });
        });
    </script>
{% endblock %}
