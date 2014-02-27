F = { 
    fetch_title : function(url, callback) {
        $.post('/harvest/pageinfo/', {url:url}, callback);
    },
    url_domain: function (url) {
        var a = document.getElementById('url-template');
        a.href = url;
        var domain = a.hostname;
        if (a.port && a.port != 80) {
            domain += ":" + a.port;
        };
        return domain;
    },
    form2json: function(form)
    {
        var o = {};
        var a = $(form).serializeArray();
        
        $.each(a, function() {
            if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    },
    show_paginator: function(view, display_max, callback) {
        var self = view;
        if (self.collection.total_count > self.collection.paginationConfig.ipp) {
            self.$(".paginator").pagination({
              total_pages: Math.ceil(self.collection.total_count / self.collection.paginationConfig.ipp),
              current_page: self.collection.currentPage,
              display_max:display_max,
              callback: function(event, page) {
                  callback();
                  self.collection.loadPage(page);
              }
            }).show();
        } else {
            self.$(".paginator").hide();
        }
    }
}
$.fn.spin = function(opts) {
  this.each(function() {
    var $this = $(this),
    data = $this.data();

    if (data.spinner) {
        data.spinner.stop();
        delete data.spinner;
    }
    if (opts !== false) {
        data.spinner = new Spinner($.extend({color: $this.css('color')}, opts)).spin(this);
    }
  });
  return this;
};

/* search */
var router;
$('.search').submit(function(){
    var query = $(this).find('.query').val();
    if (query.indexOf('#') == 0) {
        var search_url = $(this).attr('tag-action') + query.slice(1)
    } else {
        var search_url = $(this).attr('action') + query;
    }
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
        $('#feedback .feedback-input-area').hide();
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
            self.prev().css("display", "inline-block");
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
            self.next().css("display", "inline-block");
            self.removeClass('disabled');
        });
    }
    return false;
});

/*  */
