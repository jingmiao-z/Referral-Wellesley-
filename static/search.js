var searchRequest = null;
var search_by = 'position';

$('#radio_button_group input:radio').on('change', function () {
    search_by = $(this).val();
});

$(function () {
    var minlength = 3;
    // when user type in the input box
    $("#search_input").keyup(function () {
        value = $(this).val();
        console.log(search_by);
        // if user types 3 or more characters
        if (value.length >= minlength) {
            // show the div and get json object from python
            $('#result').show();
            $.get('/keywords/' + value + '/' + search_by,
                function (data) {
                    keywords = data['keywords'];
                    search_by = data['search_by'];
                    let myData;
                    myData = $('<table>', { 'class': 'result_matches' });
                    myData.css({
                        'text-align': 'left',
                        'border-collapse': 'separate',
                        'border-spacing': '10px 8px',
                        'width': '610px',
                        'border-radius': '0.5rem',
                        'background': 'rgb(217, 158, 249)'
                    });
                    // If the user is searching by position
                    // iterate through keywords and get the matched positionNames
                    if (search_by == 'position') {
                        $.each(keywords, function (i, value) {
                            myData.append($('<tr>',
                                {
                                    'class': 'result_contents',
                                    'onclick': 'setValue(\"' + value.positionName + '\")'
                                }).text(value.positionName + " "));
                        });
                    // If the user is searching by referrer
                    // iterate through keywords and get the matched referrer names
                    } else if (search_by == 'referrer') {
                        $.each(keywords, function (i, value) {
                            myData.append($('<tr>',
                                {
                                    'class': 'result_contents',
                                    'onclick': 'setValue(\"' + value.referrerName + '\")'
                                }).text(value.referrerName + " "));
                        });
                    // If the user is searching by company
                    // iterate through keywords and get the matched company names
                    } else {
                        $.each(keywords, function (i, value) {
                            myData.append($('<tr>',
                                {
                                    'class': 'result_contents',
                                    'onclick': 'setValue(\"' + value.company + '\")'
                                }).text(value.company + " "));
                        });
                    }
                    $("#result").html(myData);
                });
        } else {
            $('#result').hide();
        }
    });
});

// when user click on the keyword
// update the value in the search box (the value will be autofilled in the search bar)
function setValue(value) {
    $("#search_input").val(value);
}