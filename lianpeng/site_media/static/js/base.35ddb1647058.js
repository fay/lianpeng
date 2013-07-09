var router;
$('.search').submit(function(){
    var query = $(this).find('.query').val();
    var search_url = $(this).attr('action') + query;
    if (router) {
        router.navigate(search_url, {trigger: true});
    } else {
        window.location.href = search_url;
    }
    return false;
});
$('#feedback .confirm').click(function(){
    if ($(this).hasClass('disabled')) {
        return false;
    }
    $(this).addClass('disabled')
    var text = $('#feedback textarea').val();
    var data = {text:text}
    data = JSON.stringify(data)
    $.ajax({url:'/api/v1/feedback/', data:data, type:'POST',
        contentType: "application/json",
        dataType: "application/json"
    }).complete(function(){
        $('#feedback textarea').hide();
        $('#feedback .success').show();
    });
    return false;
});

$('#feedback').on('hidden', function () {
    $('#feedback textarea').val("");
    $('#feedback .confirm').removeClass("disabled");
    $('#feedback textarea').show();
    $('#feedback .success').hide();
});
