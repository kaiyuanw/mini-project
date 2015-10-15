function failure_content(err) {
     return '<div class="alert alert-danger alert-dismissible" role="alert">' +
     '<button type="button" class="close" data-dismiss="alert"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>' +
     '<strong>Sorry! </strong>' + err + '</div>'
}

var $alert = $("#alert");
var $name = $('#stream_name');
var $tags = $('#stream_tags');
var $subscribers = $('#stream_subscribers');
var $msg = $('#stream_msg');
var $url = $('#stream_cover_url');
var success_content = '<div class="alert alert-success alert-dismissible" role="alert">' +
                      '<button type="button" class="close" data-dismiss="alert"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>' +
                      '<strong>Great! </strong> You have just created a new stream!</div>';

$('#create_btn').on('click', function(e) {
    e.preventDefault();
    var stream = {
        stream_name: $name.val(),
        stream_tags: $tags.val(),
        subscribers: $subscribers.val(),
        optional_msg: $msg.val(),
        cover_url: $url.val()
    };
    $.ajax({
        type: 'POST',
        url: 'create',
        data: stream,
        success: function(msg) {
            if (msg.successful) {
                if ($alert.children().length == 1)
                    $alert.find('>:first-child').replaceWith(success_content);
                else
                    $alert.append(success_content);
                $name.val('');
                $tags.val('');
                $subscribers.val('');
                $msg.val('');
                $url.val('');
            }
            else {
                if ($alert.children().length == 1)
                    $alert.find('>:first-child').replaceWith(failure_content(msg.error));
                else
                    $alert.append(failure_content(msg.error));
            }
        },
        error: function(msg) {
            alert("We apologize, but it seems there is problem in communication with the server!");
        }
    });
});