/* Function to display a number of unread messages */

function set_message_count(n) {
    $('#message_count').text(n);
    $('#message_count').css('visibility', n ? 'visible' : 'hidden');
}

/* Function updating unread messages count */

$(function () {
    var since = 0;
    var url = "/notifications"
    setInterval(function () {
        $.ajax(url + '?since=' + since).done(
            function (notifications) {
                for (var i = 0; i < notifications.length; i++) {
                    switch (notifications[i].name) {
                        case 'unread_message_count':
                            set_message_count(notifications[i].data);
                            break;
                        case 'task_progress':
                            set_task_progress(
                                notifications[i].data.task_id,
                                notifications[i].data.progress);
                            break;
                    }
                    since = notifications[i].timestamp;
                }
            }
        );
    }, 10000);
});
