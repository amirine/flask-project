/* Displays user popup */

$(function () {
    var timer = null;
    var xhr = null;

    $('.user_popup').hover(

        // Handles mouse on username
        function (event) {
            var elem = $(event.currentTarget);
            timer = setTimeout(function () {
                timer = null;
                xhr = $.ajax(
                    elem.first().text().trim() + '/popup').done(
                    function (data) {
                        xhr = null;
                        elem.popover({
                            trigger: 'manual',
                            html: true,
                            animation: false,
                            container: elem,
                            content: data
                        }).popover('show');
                        flask_moment_render_all();
                    }
                );
            }, 1000);
        },

        // Handles mouse out username
        function (event) {
            var elem = $(event.currentTarget);
            if (timer) {
                clearTimeout(timer);
                timer = null;
            } else if (xhr) {
                xhr.abort();
                xhr = null;
            } else {
                elem.popover('destroy');
            }
        }
    )
});
