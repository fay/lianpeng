/* search */
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

/* feedback */
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

/* follow */
$('.follow-button').click(function(){
    if (!$(this).hasClass('disabled')) {
        $(this).addClass('disabled');
        var followee_id = $(this).data('id');
        var self = $(this);
        var data = JSON.stringify({followee:"/api/v1/user/" + followee_id});
        $.ajax({url: '/api/v1/follow', data:data, type:'POST', 
            contentType: "application/json",
            dataType: "application/json"
        }).complete(function(xhr){
            var data = JSON.parse(xhr.responseText);
            self.prev().attr('data-id', data.id);
            self.hide();
            self.prev().css("display", "block");
            self.removeClass('disabled');
        });
    }
    return false;
});
$('.unfollow-button').click(function(){
    if (!$(this).hasClass('disabled')) {
        $(this).addClass('disabled');
        var follow_id = $(this).attr('data-id');
        
        var self = $(this);
        $.ajax({url: '/api/v1/follow/' + follow_id, type:'DELETE', 
            contentType: "application/json",
            dataType: "application/json"
        }).complete(function(){
            self.hide();
            self.next().css("display", "block");
            self.removeClass('disabled');
        });
    }
    return false;
});


