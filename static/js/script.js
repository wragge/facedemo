$(function() {
    $.wait = function(ms) {
        var defer = $.Deferred();
        setTimeout(function() { defer.resolve(); }, ms);
        return defer;
    };

    var checkJob = function () {
        return $.get("/facedemo/check/" + job_id);
    };

    var checkJobDone = function () {
        return checkJob()
        .done(function(data) {
            if (data == 'Waiting') {
                return $.wait(200).then(checkJobDone)
            } else {
                $('.img-cell').append('<img id="test-image" class="img-responsive" src="/static/' + data + '">');
            }
        })
    };

    if (job_id !== "") {
        checkJobDone();
    }
});