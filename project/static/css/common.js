$(function() {

    var _is_ios = false;
    var _is_ie = false;
    var _is_ff = false

    var _is_iphone = false;
    var _is_ipad = false;

    //IE用
    if (!Array.indexOf) {
        Array.prototype.indexOf = function(o) {
            for (var i in this) {
                if (this[i] == o) {
                    return i;
                }
            }
            return -1;
        }
    }
    var ie = (function() {
        var undef, v = 3,
            div = document.createElement('div');

        while (
            div.innerHTML = '<!--[if gt IE ' + (++v) + ']><i></i><![endif]-->',
            div.getElementsByTagName('i')[0]
        );

        return v > 4 ? v : undef;
    }());

    ///*
    var _UA = navigator.userAgent.toLowerCase();
    if (_UA.indexOf("iphone") != -1 || _UA.indexOf("ipad") != -1 || _UA.indexOf("ipod") != -1) {
        _is_ios = true;
        if (_UA.indexOf("iphone") != -1 || _UA.indexOf("ipod") != -1) {
            _is_iphone = true;
        } else if (_UA.indexOf("ipad") != -1) {
            _is_ipad = true;
        }
    } else if (_UA.indexOf("android") != -1) {

        _is_ios = true;
    } else if (_UA.indexOf("msie") != -1) {
        _is_ie = true;
        /*
        if(ie >= 9){
          _is_ie = false;
        }
        */
    } else if (_UA.indexOf("firefox") != -1) {
        _is_ff = true;
    }

    var requestAnimationFrame = window.requestAnimationFrame || window.mozRequestAnimationFrame || window.webkitRequestAnimationFrame || window.msRequestAnimationFrame;
    window.requestAnimationFrame = requestAnimationFrame;

    var stats = new Stats();
    stats.setMode(0);
    stats.domElement.style.position = 'absolute';
    stats.domElement.style.left = '0px';
    stats.domElement.style.top = '0px';
    //document.body.appendChild( stats.domElement );

    var stageWidth = $(window).width();
    var stageHeight = $(window).height();

    //ジャケットモーションフラグ
    var _home_jacket_move = false;
    var _home_jacket_move_rad = 0;
    //shareモーションフラグ
    var _share_bg_move = false;

    var pNum = 200;
    var particles = [];

    for (var i = 0; i < pNum; i++) {
        particles.push({});
        setDefaultObj(particles[particles.length - 1]);
    }

    // プリローダー
    $("body").append('<div class="preloader" style="height: 0px;position: absolute;left: 50%;top: 50%;width: 0px;"></div>');
    $("body .preloader").activity({
        segments: 12,
        width: 2,
        space: 1,
        length: 4,
        color: '#000000',
        speed: 2
    });

    //!_is_ff &&
    if (!_is_ie) {
        //よし通れ！

        /*    ここから通常挙動     */

        //drawDots();
        resize();
        $(window).on("resize", function() {
            resize();
        });
        $(window).on("orientationchange", function() {
            resize();
        });

        /*
          遷移
        */
        var _nowMoving = true;
        var _nowContent = 4;
        moveContents(_nowContent);
        /*
          ロード完了
        */
        //window.addEventListener("load", function(){
        $(window).on("load", function() {
            resize();
            //イラスト
            //illustLoad();
            //
            $("body .preloader").activity(false);
            $("body .preloader").remove();
            $(".contents").animate({
                "opacity": 1
            }, {
                duration: 0
            });
            $("header").css({
                "display": "block"
            }).animate({
                "opacity": 1
            }, {
                duration: 1000
            });
            $(".share").css({
                "display": "table"
            }).animate({
                "opacity": 1
            }, 1000, function() {
                _nowMoving = false;
            });
        });

        /*
          loop
        */
        loop();

        /*    ここまで通常挙動     */

    } else {
        //何者だ！！
        $(window).on("load", function() {
            resize();
            //イラスト描画
            illustLoad();
            //
            $("body .preloader").activity(false);
            $("body .preloader").remove();
            $(".contents").css({
                "opacity": 1,
                "display": "block"
            });
            $("header").css({
                "opacity": 0,
                "display": "block"
            }).animate({
                "opacity": 1
            }, {
                duration: 1000
            });
            $("article").css({
                "opacity": 0,
                "display": "block"
            }).animate({
                "opacity": 1
            }, {
                duration: 1000
            });

            $(".main > .bg").css({
                "overflow-y": "auto"
            });
            $(".main > .container").css({
                "overflow-y": "auto"
            });
            $(".main > .container > .contents > article").css({
                "height": "640px",
                "display": "block",
                "opacity": 1,
                "position": "relative"
            });
            $(".main > .bg").css({
                "overflow-y": "auto",
                "display": "none"
            });
            $(".main > .bg > .bgs > .red").css({
                "margin-top": 640
            });
            $(".main > .bg > .bgs > div > canvas").css({
                "display": "none"
            });
            $(".main > .bg > .bgs > div").css({
                "height": "640px",
                "display": "block",
                "opacity": 1,
                "position": "relative",
                "left": "auto",
                "top": "auto"
            });

            $(".main > .container > .contents > .disc .jacket").css({
                "opacity": 1
            });

            $(".main > .container > .contents > .home").css({
                "background-color": "#FFFFFF"
            });
            $(".main > .container > .contents > .disc").css({
                "background-color": "#9d2226"
            });
            $(".main > .container > .contents > .track").css({
                "background-color": "#1d2087"
            });
            $(".main > .container > .contents > .staff").css({
                "background-color": "#be9e6d"
            });
            $(".main > .container > .contents > .share").css({
                "background-color": "#464d58"
            });
        });

    }

    function moveContents(num) {

        if (num < 0) {
            num = 0;
        } else if (num > 4) {
            num = 4;
        }
        _nowMoving = true;
        changeContent(num, _nowContent);
        _nowContent = num;
    }

    function changeContent(num, old_num) {

        _home_jacket_move = false;
        _home_jacket_move_rad = 0;

        var vec = "follow";
        if (old_num > num) {
            vec = "back";
        }

        old_num = 3;

        if (num == 0) {
            $(".menu").animate({
                "opacity": 0
            }, 1000).css({
                "display": "none"
            });
        } else {
            $(".menu").css({
                "display": "block"
            }).animate({
                "opacity": 1
            }, 1000);
        }
        /* soundclooud */
        $(".track .btn_play").css({
            "display": "block"
        });
        $(".track .soundcloud").css({
            "display": "none"
        });
        $(".track .soundcloud").html('');

        /* remove*/
        if (old_num == 0) {} else if (old_num == 1) {} else if (old_num == 2) {} else if (old_num == 3) {} else if (old_num == 4) {
            changeBg("red");
            $(".bg .done canvas").transit({
                "scale": "0",
                "opacity": 0
            }, 500, "easeOutCirc");
            $(".share .title").transit({
                "translate3d": "0,0,1000"
            }, 1000, "easeInCirc");
            $(".share .social").transit({
                "translate3d": "0,0,2000"
            }, 1000, "easeInCirc");
            $(".share .banner_468").transit({
                "translate3d": "0,0,3000"
            }, 1000, "easeInCirc");
            $(".share .banner_200").transit({
                "translate3d": "0,0,4000"
            }, 1000, "easeInCirc");
            $(".share .diverse").transit({
                "translate3d": "0,0,5000"
            }, 1000, "easeInCirc");
            $(".share .copyright").transit({
                "translate3d": "0,0,6000"
            }, 1000, "easeInCirc", function() {
                $(".contents > .share").css({
                    "display": "block",
                    opacity: 0
                });
            });

            // $(".bg .jacket .inner").css({"opacyty":1,"display":"block","transformOrigin":"50% 50%"}).transit({"translate3d":"0,0,-500",rotateX:-20+40*Math.random(),rotateY:-20+40*Math.random()}, 1000, "ease");

        }

        var o0 = 1;
        var o1 = 1;
        if (_is_ff) {
            /* Firefoxの深度管理がどうにもこうにも */
            o0 = 0;
        }

        if (num == 0) {} else if (num == 1) {} else if (num == 2) {} else if (num == 3) {} else if (num == 4) {
            $(".share").css({
                "display": "block",
                "opacity": 1
            });
            $(".share .title").css({
                "opacity": 0
            }).animate({
                "opacity": 0
            }, 2000).transit({
                "translate3d": "0,0,1000"
            }, 0, "easeInCirc").transit({
                "translate3d": "0,0,0",
                "opacity": 1
            }, 2000, "easeOutCirc");
            $(".share .social").css({
                "opacity": 0
            }).animate({
                "opacity": 0
            }, 2000).transit({
                "translate3d": "0,0,2000"
            }, 0, "easeInCirc").transit({
                "translate3d": "0,0,0",
                "opacity": 1
            }, 2000, "easeOutCirc");
            $(".share .banner_468").css({
                "opacity": 0
            }).animate({
                "opacity": 0
            }, 2000).transit({
                "translate3d": "0,0,3000"
            }, 0, "easeInCirc").transit({
                "translate3d": "0,0,0",
                "opacity": 1
            }, 2000, "easeOutCirc");
            $(".share .banner_200").css({
                "opacity": 0
            }).animate({
                "opacity": 0
            }, 2000).transit({
                "translate3d": "0,0,4000"
            }, 0, "easeInCirc").transit({
                "translate3d": "0,0,0",
                "opacity": 1
            }, 2000, "easeOutCirc");
            $(".share .diverse").css({
                "opacity": 0
            }).animate({
                "opacity": 0
            }, 2000).transit({
                "translate3d": "0,0,5000"
            }, 0, "easeInCirc").transit({
                "translate3d": "0,0,0",
                "opacity": 1
            }, 2000, "easeOutCirc");
            $(".share .copyright").css({
                "opacity": 0
            }).animate({
                "opacity": 0
            }, 2000).transit({
                "translate3d": "0,0,6000"
            }, 0, "easeInCirc").transit({
                "translate3d": "0,0,0",
                "opacity": 1
            }, 2000, "easeOutCirc", function() {
                _nowMoving = false;
            });

            changeBg("done");
            $(".bg .done canvas").css({
                "scale": "0",
                "opacity": 0
            }).transit({
                "scale": "1",
                "opacity": 1
            }, 2000, "ease");
        }
    }

    function changeBg(color) {
        for (var i = 0; i < particles.length; i++) {
            var particle = particles[i];
            setDefaultObj(particle);
        }
        $(".main > .bg > .bgs > div").each(function() {
            if ($(this).hasClass(color)) {
                $(this).css({
                    "display": "block",
                    "opacity": 1
                });
            } else {
                $(this).css({
                    "display": "none",
                    "opacity": 0
                });
            }
        });
    }

    function resize() {
        stageWidth = $(window).width();
        stageHeight = $(window).height();
        if (_is_ie) {
            stageHeight = 640;
        }
        // ホーム画面穴開け直し
        //done
        $(".main > .bg .done canvas").attr("width", stageWidth);
        $(".main > .bg .done canvas").attr("height", stageHeight);
        canvas = $(".main > .bg .done canvas")[0];
        canvas_context = canvas.getContext("2d");
        canvas_context.clearRect(0, 0, canvas.width, canvas.height);
        canvas_context.fillStyle = "rgba(255, 255, 255, 0)";
        canvas_context.strokeStyle = "rgb(255, 255, 255)";
        canvas_context.lineWidth = 30;
        canvas_context.beginPath();
        canvas_context.arc(Math.round(stageWidth * 0.5), Math.round(stageHeight * 0.5), 277, 0, Math.PI * 2, false);
        canvas_context.stroke();

        $("#test").attr("width", stageWidth);
        $("#test").attr("height", stageHeight);
    }

    function loop() {
        stats.begin();

        if (_home_jacket_move) {
            _home_jacket_move_rad += 2;
            if ((_home_jacket_move_rad * 0.1) % 360 > 90 && (_home_jacket_move_rad * 0.1) % 360 < 270) {
                _home_jacket_move_rad += 4;
            }
        }

        drawDots($(".bg .done canvas"));

        //

        stats.end();
        requestAnimationFrame(loop);
    }

    function setDefaultObj(particle) {
        particle.s = 5;
        particle.x = stageWidth * Math.random();
        particle.y = -2;
        particle.v = 5 * Math.random();
        particle.a = 0.01 * Math.random();
        particle.life = 0.001 + 0.002 * Math.random();
    }

    function drawDots(obj) {

        obj.clearCanvas()
        for (var i = 0; i < particles.length; i++) {
            var particle = particles[i];
            particle.v += particle.a;
            particle.v *= 0.990;
            particle.y += particle.v;
            particle.s = (3.0 - Math.pow(particle.y, 1.5) * particle.life);

            if (particle.s < 1 || Math.random() < 0.001) {
                particle.s = 1;
                setDefaultObj(particle);

            }
            var r = Math.random();
            var ox = 0;
            var oy = 0;
            if (_nowContent == 1) {
                ox = particle.x;
                oy = particle.y;
            } else if (_nowContent == 2) {
                ox = particle.x;
                oy = stageHeight - particle.y;
            } else if (_nowContent == 3) {

                ox = particle.y * 4;
                oy = stageHeight * particle.x / stageWidth;
            } else {
                ox = stageWidth * 0.5 + Math.cos(Math.PI * 2 * particle.x / stageWidth) * (particle.y * 0.3 + 287);
                oy = stageHeight * 0.5 + Math.sin(Math.PI * 2 * particle.x / stageWidth) * (particle.y * 0.3 + 287);
            }
            var color = "#F8D44E";
            if (r < 0.7) {
                color = "#F8D44E";

            } else if (r < 0.9) {
                color = "#ab8a11";
            } else {
                color = "#FFFFE0";
            }
            if (_nowContent == 4) {
                color = "#FFFFFF";
            }
            drawDot(obj, color, ox, oy, particle.s);

        }
        if (_nowContent == 4) {
            var canvas = $(".main > .bg .done canvas")[0];
            var canvas_context = canvas.getContext("2d");
            canvas_context.fillStyle = "rgba(255, 255, 255, 0)";
            canvas_context.strokeStyle = "rgb(255, 255, 255)";
            canvas_context.lineWidth = 30;
            canvas_context.beginPath();
            canvas_context.arc(Math.round(stageWidth * 0.5), Math.round(stageHeight * 0.5), 277, 0, Math.PI * 2, false);
            canvas_context.stroke();
        }
    }

    function drawDot(obj, color, x, y, s) {
        var canvas = obj[0];
        var canvas_context = canvas.getContext("2d");
        canvas_context.globalCompositeOperation = 'source-over';
        canvas_context.fillStyle = color;
        canvas_context.fillRect(x, y, s * (0.8 + Math.random() * 0.4), s * (0.8 + Math.random() * 0.4));

    }
});