var loading_lists = false;
$('.bookmark-entry-box').hover(function(){
    $(this).find('.actions').toggle();
    if (!loading_lists) {
        loading_lists = true;
        $.ajax({type:'GET', url:"/api/v1/list/", processData: false,
        }).success(function(data){
            window.lists = data.objects;
        });
    }
});
$('.bookmark-entry-box .actions .save-action').click(function(){



    var bookmark_dom = $(this).parents('.bookmark-entry-box');
    var id = bookmark_dom.data('id');
    var title = bookmark_dom.data('title');
    var url = bookmark_dom.data('url');
    var tags = bookmark_dom.data('tags');
    var note = bookmark_dom.data('note');
    var domain = bookmark_dom.data('domain');
    var bookmark = {id:id, title:title, note:note, tags:tags, url: url, domain:domain};

    show_add_bookmark_modal(bookmark);
});
