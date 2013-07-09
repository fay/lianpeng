var loading_lists = false;
var lists = {};
$('.bookmark-entry-box').hover(function(){
    $(this).find('.actions').toggle();
    if (!loading_lists) {
        loading_lists = true;
        $.ajax({type:'GET', url:"/api/v1/list/", processData: false,
        }).success(function(data){
            lists = data;
        });
    }
});
$('.bookmark-entry-box .actions .save-action').click(function(){



    var template = $('#bookmark-form-tmpl').html();
    var bookmark_dom = $(this).parents('.bookmark-entry-box');
    var id = bookmark_dom.data('id');
    var title = bookmark_dom.data('title');
    var url = bookmark_dom.data('url');
    var tags = bookmark_dom.data('tags');
    var note = bookmark_dom.data('note');
    var domain = bookmark_dom.data('domain');
    var bookmark = {id:id, title:title, note:note, tags:tags, url: url, domain:domain};


    
    var html = _.template(template, {bookmark: bookmark, list:{}});
    bookmark_dom.find('.edit-bookmark-box').html(html).show();
    for(var i = 0;i < lists.objects.length;i++) {
        bookmark_dom.find('form #list').append('<option value="' + lists.objects[i].resource_uri + '">' +  lists.objects[i].name + '</option>');
    }
    $.ajax({type:'GET', url:"/api/v1/bookmark/?url=" + url, processData: false}).success(function(data){
        if(data.objects.length > 0) {
            bookmark_dom.find('.existed-bookmark').show();
            bookmark_dom.find('.existed-bookmark').addClass('alert');
            bookmark_dom.find('.existed-bookmark .text').show();
        } else {
            bookmark_dom.find('.existed-bookmark').hide();
        }
    });
    bookmark_dom.find('.edit-bookmark-box form').submit(function(e){
        if ($(this).find('.save').hasClass("disabled")) {
            return false;
        }
        $(this).find('.save').addClass("disabled");
        var data = F.form2json(this);
        var self = this;
        var data_str = JSON.stringify(data); //TODO JSON needs to import in IE7
        $.ajax({type:'POST', url:'/api/v1/bookmark/', data:data_str, processData: false,
            contentType: "application/json",
            dataType: "application/json"}).complete(function(xhr){
                $(self).hide();
            });
        return false;
    });
    bookmark_dom.find('.edit-bookmark-box form .cancel').click(function(){
        bookmark_dom.find('.edit-bookmark-box').hide(); 
        bookmark_dom.find('.bookmark-title-box').show();
    });
});
