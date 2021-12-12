
// function called when user clicked on Message Center Button
$(document).ready(function () {
    $("#message_center").click(function () {
        $.getJSON("/messageCenter/",
            function (data) {
                if (data.logout) {
                    alert("You are not logged in. Please login.");
                    window.location.replace('..');
                    e.preventDefault();
                } else {
                    // Create a DOM
                    let appendlist;
                    appendlist = $('<li>', { 'class': 'message_contents' });
                    // if there is no notifications in the database
                    if (data.empty) {
                        appendlist.append($('<li>', { 'class': 'error' }).text(data.emptymsg + " "));
                        appendlist.css({
                            'margin': '20px 0px',
                            'font-size': '25px',
                            'list-style-type': 'none'
                        });
                        // if there exits notifications in the database
                    } else {
                        var list = data['message'];
                        $.each(list, function (i, value) {
                            appendlist.append($('<li>').text(value.announcement + " "))
                        });
                        appendlist.css({
                            'margin': '10px 0px',
                            'font-size': '20px',
                            'list-style-type': 'square'
                        });
                    }
                    // show the message_center_div and display the DOM in html
                    $('#message_center_div').show();
                    $('#message_center_div').html(appendlist);
                }
            }
        );
    });
});

// hide message_center_div when user click outside of the div
$(document).mouseup(function (e) {
    var container = $('#message_center_div');
    if (!container.is(e.target) && container.has(e.target).length === 0) {
        container.hide();
    }
});