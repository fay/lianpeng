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
    $('#feedback .feedback-input-area').show();
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

/*  new link */
function fetch_url (e) {
    var url = $(e.currentTarget).find('.url').val();
    url = $.trim(url);
    if (url.indexOf('http://') >= 0 || url.indexOf('https://') >= 0 ) {
    } else {
        noty({text: '请输入正确的链接', type:'warning', timeout:1000});
        return false;
    }
    $(e.currentTarget).spin();
    $(e.currentTarget).find('input').attr('disabled', 'on');
    var self = this;

    // fetch web page info
    F.fetch_title(url, function(data) {
        $(e.currentTarget).spin(false);
        data = $.parseJSON(data);
        if (data) {
            var domain = F.url_domain(url); 
            data.url = url;
            data['domain'] = domain;
            data['tags'] = '';
            $('#new-link-modal').modal('hide').on('hidden', function () {
                show_add_bookmark_modal(data);
            });
        };
    });
    return false;
}
$('#new-link-modal form').submit(function (e) {
    fetch_url(e);
    return false;
});
$('#new-link-modal').on('hide', function () {
    $(this).find('input').removeAttr('disabled');
    $(this).find('input.url').val("");
});
var get_list_options = function(current_list) {
    try {
        var lists = lists_view.collection.toJSON();
    } catch(e) {
        var lists = window.lists;
    }
    var option_html = "";
    for(var i = 0;i < lists.length;i++) {
        var is_current = false;
        var name = lists[i].name;
        if (lists[i].kind == 3) {
            name += " - " + lists[i].user_name;
        }
        if (current_list && current_list == lists[i].resource_uri) {
            is_current = true;
        }
        option_html += '<option value="' +  lists[i].resource_uri;
        if (is_current) {
            option_html += '" selected="on'
        }
        option_html += '" >' +  name  + '</option>';
    }
    return option_html; 
};
function show_add_bookmark_modal(data, callback) {
    $('#new-link-modal').off('hidden');
    var bookmark_dict = {url: data.url,
        user: USER_URL,
        title: data.title,
        domain: data.domain,
        note: data.note,
        tags: data.tags
    };
    var url = data.url;
    var template = $('#bookmark-form-tmpl').html();
    $('#bookmark-modal').remove();
    var html = $(_.template(template, {bookmark: bookmark_dict}));
    html.modal();
    html.on('shown', function () {
        render_bookmark_form(data, callback);
    });
};
function render_bookmark_form(data, callback) {
    var url = data.url;
    var self = this;
    var option_html = get_list_options();
    $('#bookmark-modal form #list').html(option_html);

    ////////////////////////
    var method = "POST";
    var action = "/api/v1/bookmark/";
    // check if existed
    function update_form (bookmark) {
        $('.modal-header .existed').show();
        $('.modal-header .new-title-text').hide();
        $('.modal-header .edit-title-text').show();
        
        var fields = ['title', 'domain', 'note', 'url', 'tags', 'list'];
        for(var i=0;i < fields.length;i ++) {
            $('#bookmark-modal form [name="' + fields[i] + '"]').val(bookmark[fields[i]]);
        }
        
        action = action + bookmark['id'];
        method = "PUT";
    }
    if (data.id && data.user == USER_URL) {
        $('.modal-header .spinner').hide();
        update_form(data);
    } else {
        $.getJSON('/api/v1/bookmark/', {url: url}, function(data){
            if(!data.meta) {
                data = $.parseJSON(data);
            }
            if(data.meta.total_count > 0) {
                var bookmark = data.objects[0];
                update_form(bookmark);
            }
        }).complete(function (argument) {
            $('.modal-header .spinner').hide();
        });
    }

    // create new bookmark
    $('#bookmark-modal' + ' form').submit(function(){
        if ($('#bookmark-modal .save').hasClass("disabled")) {
            return false;
        }
        $('#bookmark-modal .save').addClass("disabled");
        var data = F.form2json(this);
        var self = this;
        var data_str = JSON.stringify(data); //TODO JSON needs to import in IE7
        $.ajax({type: method, url: action, data: data_str, processData: false,
            contentType: "application/json",
            success: function (resp) {
            },
            dataType: "application/json"}).complete(function(xhr){
                $('#bookmark-modal').modal('hide');
                if (xhr.status == 202) {
                    callback($.parseJSON(xhr.responseText));
                }
            });
        return false;
    });
};
