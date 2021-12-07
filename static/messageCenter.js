
// function called when user clicked on Message Center Button
$(document).ready(function() {
    $("#message_center").click(function(){
        $.getJSON("/messageCenter",
        function (data) {
            // Create a DOM
            let appendlist;
            appendlist = $('<ul>', {'class': 'message_contents'});
            // if there is no notifications in the database
            if (data.empty) {
                console.log(data.emptymsg);
                appendlist.append($('<li>', {'class': 'error'}).text(data.emptymsg + " "));
            // if there exits notifications in the database
            } else {
                var list = data['message'];
                console.log(list)
                $.each(list, function (i, value) {
                    appendlist.append($('<li>', {'class': 'message_content'}).text(value.announcement));
                })
            }
            // show the message_center_div and display the DOM in html
            $('#message_center_div').show();
            $('#message_contents').html(appendlist);
        }
    );
    }); 
});

// hide message_center_div when user click outside of the div
$(document).mouseup(function(e) {
    var container = $('#message_center_div');
    if (!container.is(e.target) && container.has(e.target).length === 0) 
    {
        container.hide();
    }
});