/* Function to display a number of unread messages */

function set_message_count(n) {
            $('#message_count').text(n);
            $('#message_count').css('visibility', n ? 'visible' : 'hidden');
        }

/* Function updating unread messages count */

$(function() {
    var since = 0;
    var url = "/main/notifications"
    setInterval(function() {
        $.ajax(url + '?since=' + since).done(
            function(notifications) {
                for (var i = 0; i < notifications.length; i++) {
                    if (notifications[i].name == 'unread_message_count')
                        set_message_count(notifications[i].data);
                    since = notifications[i].timestamp;
                }
            }
        );
    }, 10000);
});
