/**
 * Created by Kaiyuan_Wang on 10/11/15.
 */
$(function () {
    var cache = {};
    $("#auto_complete").autocomplete({
        minLength: 1,
        source: function (request, response) {
            var term = request.term;
            if (term.trim() == '')
                return;
            if (term in cache) {
                response(cache[term]);
                return;
            }
            $.getJSON("auto_complete", request, function (data, status, xhr) {
                if (data.length !== 0) {
                    cache[term] = data.data;
                    response(data);
                }
            });
        }
    });
});