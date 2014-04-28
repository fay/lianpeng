var Bookmark = Backbone.Model.extend({
    urlRoot: '/api/v1/bookmark/',
    initialize: function () {
        this.bind("change", this.note2text, this);
        this.note2text();
    },
    note2text: function () {
        var note = this.get('note');
        if (note) {
            var note_text = $("<div>" + note + "</div>").text();
            this.set('note_text', note_text)
        }
    }
});

var Bookmarks = BaseCollection.extend({
    model: Bookmark,
    list: null,
    initialize: function(options){
        if (options && options.list) {
            this.list = options.list;
        }
        Backbone.Pagination.enable(this, {
            page_attr: "offset",
            ipp: 20,
            ipp_attr: "limit"
        });
    },
    baseUrl: function(){
        
        if (this.list) {
            if (typeof(this.list.id) == 'number') {
                return this.list.url() + "/bookmarks/"
            } else {
                var q = "";
                if (this.list.id == 'search') {
                    q = "?q=" + this.list.get('query');
                } else if (this.list.id == 'tag') {
                    q = "?tag=" + this.list.get('tag');
                } else if(this.list.id == 'feed') {
                    q = "?feed=t"
                } else if(this.list.id == 'recent') {
                    q = "?recent=t"
                }
                return '/api/v1/bookmark/' + q;
            }
        } else {
            return '/api/v1/bookmark/';
        }
    }
});
var BookmarkView = Backbone.View.extend({
    initialize: function(){
        this.$el = $('#bookmark-' + this.model.id);
        this.events = {
            "click .edit-action": "edit",
            "click .bookmark-title": "record_viewed",
            "click .share-action": "share",
            "click .like-action": "like",
            "click .preview-action": "preview",
            "click .save-action": "collect",
            "click .shares .douban": "share_douban",
            "click .shares .weibo": "share_weibo",
            "click .comment-action": "show_comment_box",
            "click .bookmark-list-link": "goto_list",
            "click #preview-box .close-preview": "close_preview",
            "click #preview-box .read-mode": "read_mode",
            "hover": "show_actions",
            "hover .move": "enable_drag",
            "mouseleave .move": "disable_drag",
            "click .remove-action": "remove"
        }
        this.list = this.options['list'];
        this.listenTo(this.model, 'destroy', this.remove_bookmark_html);
        this.listenTo(this.model, 'change', this.append_bookmark_html);
        this.comments_view = new CommentsView({el:'#bookmark-' + this.model.id + " .comments-box", bookmark:this.model});
        this.$('.actions li').tooltip({placement:'bottom', animation:false, delay: { show: 0, hide: 0 }});
        this.$('.move').tooltip({placement:'right', animation:false, delay: { show: 0, hide: 0 }});

    },
    like: function (e) {
        var target = $(e.currentTarget);
        $.post(target.attr('href'));
        if(target.find('i').hasClass('icon-heart-empty')) {
            target.find('i').removeClass('icon-heart-empty');
            target.find('i').addClass('icon-heart text-error');
            target.parent().attr('data-original-title', '取消');
        } else {
            target.find('i').addClass('icon-heart-empty');
            target.find('i').removeClass('text-error');
            target.find('i').removeClass('icon-heart');
            target.parent().attr('data-original-title', '赞');
        }
        return false;
    },
    goto_list: function () {
        if (USER_URL == this.model.get('user')) {
            router.navigate(USER_NAME + '/list/' + this.model.get('list_id'), {trigger:true});
        } else {
            window.open('/list/' + this.model.get('list_id') + '/');
        }
    },
    show_comment_box: function() {
        if (this.list.can_comment()) {
            this.$('.comments-box').toggle();
            if (!this.comments_view.loaded) {
                this.comments_view.fetch();
            }
        }
    },
    record_viewed: function() {
        $.get('/bookmark/viewed/' + this.model.id + '/');
    },
    collect: function() {
        show_add_bookmark_modal(this.model.toJSON());
    },
    share: function(e) {
        $(e.currentTarget).dropdown('toggle')
    },
    preview: function(e) {
        this.$el.append($('#preview-box'));
        $('#preview-box').show();
        $('#preview-box').spin();
        this.read_mode();
    },
    close_preview: function(){
        $('#preview-box').hide();
        $('#preview-box #read-box').hide();
    },
    read_mode: function() {
        var url = 'http://www.diffbot.com/api/article?token=b5d5504cbe0e360e30b70152b1a38ecc&html=true&url=' + encodeURIComponent(this.model.get('url'));
        $.ajax({url:url, dataType:'jsonp'}).done(function(data){
            $('#preview-box').spin(false);
            $('#preview-box #read-box').show();
            $('#preview-box #read-box .title').text(data.title);
            $('#preview-box #read-box .url').text(data.url);
            $('#preview-box #read-box .external-link').attr('href', data.url);
            var content = $(data.html);
            content.find('a').attr('target', '_blank');
            $('#preview-box #read-box .article').html(content);
        });
    },
    share_douban: function() {
        var s = this.model.get('note');
        var title = this.model.get('title');
        var url = this.model.get('url');
        var d=document,e=encodeURIComponent, 
        r='http://www.douban.com/recommend/?url='+e(url)+'&title='+e(title)+'&sel='+e(s)+'&v=1',
        x=function(){if(!window.open(r,'douban','toolbar=0,resizable=1,scrollbars=yes,status=1,width=450,height=330'))location.href=r+'&r=1'};
        if(/Firefox/.test(navigator.userAgent)){setTimeout(x,0)}else{x()}; 
    },
    share_weibo: function() {
        var s = this.model.get('note');
        var title = this.model.get('title');
        var url = this.model.get('url');
        var param = {
            url:url,
            type:'6',
            count:'', /**是否显示分享数，1显示(可选)*/
            appkey:'4018245563', /**您申请的应用appkey,显示分享来源(可选)*/
            title:title, /**分享的文字内容(可选，默认为所在页面的title)*/
            pic:'', /**分享图片的路径(可选)*/
            ralateUid:'3358911402', /**关联用户的UID，分享微博会@该用户(可选)*/
            language:'zh_cn', /**设置语言，zh_cn|zh_tw(可选)*/
            rnd:new Date().valueOf()
        }
        var temp = [];
        for( var p in param ){
           temp.push(p + '=' + encodeURIComponent( param[p] || '' ) )
        }
        var r = 'http://service.weibo.com/share/share.php?' + temp.join('&');
        var x=function(){if(!window.open(r,'douban','toolbar=0,resizable=1,scrollbars=yes,status=1,width=450,height=330'))location.href=r+'&r=1'};
        if(/Firefox/.test(navigator.userAgent)){setTimeout(x,0)}else{x()}; 
    },
    enable_drag:function(e) {
        var self = this;
        this.$el.draggable({
            helper: function () {
                drag_ui = "<div class='drag-ui label label-info' data-id='" + self.model.id +
                    "' data-list-id='" + self.list.id + 
                    "'>" + self.model.get('title').slice(0, 10) + "</div>";
                $('body').append(drag_ui);
                return $('.drag-ui');
            },
        });
        this.$el.draggable("enable");
    },
    disable_drag: function() {
        this.$el.draggable( "disable" )
    },
    show_actions: function() {
        //this.$('.move').toggle();
        this.$('.actions').toggle();
    },
    remove_bookmark_html: function() {
        this.$el.remove();
    },
    remove : function(){
        this.model.destroy();
    },
    append_bookmark_html: function(bookmark) {
        var template = $('#bookmarks-tmpl').html();
        var bookmark = this.model;
        var html = _.template(template, {bookmarks: [bookmark.toJSON()], list: this.list.toJSON(), can_edit: this.list.can_edit()});
        this.$el.html($(html).html());
    },
    edit: function(e){
        var self = this;
        show_add_bookmark_modal(self.model.toJSON(), function(data){
            var current_list = self.model.get('list');
            if (self.list.id != 'all' && current_list != data.list) {
                self.remove_bookmark_html();
            } else {
                self.model.fetch();
            }
        });
    }
});
var BookmarksView = Backbone.View.extend({
    events: {
        "resize window": "render",
        "click .tag": "list_by_tag",
        "submit .add-bookmark-form": "add_bookmark"
    },
    list_by_tag: function(e) {
        var tag = $(e.currentTarget).text();
        router.navigate(USER_NAME + '/tag/' + tag, {trigger:true});
    },
    initialize: function() {
        var self = this;
        self.listenTo(self.collection, "add", function(data){
            self.create_bookmark_view(data, true);
        });
        self.listenTo(self.collection, "reset", self.create_bookmarks_views);
        this.list = this.options['list'];
    },
    create_bookmarks_views: function(data) {
        var bookmarks = data.models;
        var self = this;
        self.render();
        self.render_pagination();
        $.each(bookmarks, function(index, bookmark){
            self.create_bookmark_view(bookmark); 
        });
    },
    create_bookmark_view: function(bookmark, new_bookmark) {
        if (new_bookmark) {
            this.append_bookmark_html(bookmark);
        };
        var bookmark_view = new BookmarkView({model:bookmark, list: this.list});
        this.listenTo(bookmark_view, "new_bookmark", this.show_add_bookmark_form);
    },
    add_bookmark: function(e) {
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
                self.show_add_bookmark_form(data, e.currentTarget);
            };
        });
        return false;
    },
    show_add_bookmark_form: function(data, add_form, target) {
                var bookmark_dict = {url: data.url,
                    user: USER_URL,
                    title: data.title,
                    domain: data.domain,
                    note: data.note,
                    tags: data.tags
                };
                var url = data.url;
                var self = this;
                if(!target) {
                    target = '.confirm-add-bookmark';
                }
                var template = $('#bookmark-form-tmpl').html();
                var html = _.template(template, {bookmark: bookmark_dict, list:this.list.toJSON()});
                self.$(target).html(html).show();
                var option_html = get_list_options(self.list.url());
                self.$(target).find('form #list').append(option_html);
                // check if existed
                self.$(target + ' .existed-bookmark .spinner').spin({length:0, radius:6, width:2});
                var existed_bookmarks = new Bookmarks();
                existed_bookmarks.bind("reset", function(data){
                    self.$(target + ' .existed-bookmark .spinner').spin(false);
                    
                    if (data.total_count > 0) {
                        var existed_bookmark = data.models[0]
                        self.$(target + ' .existed-bookmark').addClass('alert');
                        self.$(target + ' .existed-bookmark .text').show();
                        self.$(target + ' .existed-bookmark .edit').click(function(){
                            if (!self.collection.get(existed_bookmark.id)) {
                                self.collection.push(existed_bookmark );
                            }
                            self.$(target + ' .existed-bookmark .edit').attr('href', '#bookmark-' + existed_bookmark.id);
                            self.$('.list #bookmark-' + existed_bookmark.id + ' .bookmark-title-box .actions .edit-action').trigger('click');
                            self.recover_submit_form(target, add_form);
                        });
                    } else {
                        self.$(target + ' .existed-bookmark').hide();
                    }
                });
                existed_bookmarks.fetch({url:existed_bookmarks.url() + "&url=" + encodeURIComponent(url)});

                // create new bookmark
                self.$(target + ' form').submit(function(){
                    var new_bookmark = F.form2json(this);
                    
                    self.collection.create(new_bookmark, {wait:true, success:function(data){
                    }});
                    self.recover_submit_form(target, add_form);
                    return false;
                });
                // hide confirm form and enable add-bookmark form
                self.$(target + ' form .cancel').click(function(){
                    self.recover_submit_form(target, add_form);
                });
    },
    recover_submit_form: function(target, form) {
        $(target).hide(); 
        $(form).find('input').removeAttr('disabled');
        $(form).find('input.url').val("");
    },
    append_bookmark_html: function(bookmark) {
        if (this.list.id == 'feed') {
            return false; // do not add bookmark to feed list
        }
        var template = $('#bookmarks-tmpl').html();
        var html = _.template(template, {bookmarks: [bookmark.toJSON()], list: this.list.toJSON(), can_edit: this.list.can_edit()});
        
        this.$('.no-bookmarks').hide();
        this.$('.list').prepend(html);
    },
    render_pagination: function() {
        if (!this.$('.jquery-bootstrap-pagination').html()) {
            var self = this;
            F.show_paginator(self, 8, function(){
                this.$('.list').html("");
                $(self.$('.list-wrapper')).spin();
                $('.list-wrapper').animate({scrollTop: 0});
            }); 
        }
        //this.$('.jquery-bootstrap-pagination').addClass("pagination-right");
    },
    render: function() {
        var self = this;
        $(self.$('.list-wrapper')).spin(false);
        if (this.collection.size() > 0) {
            var template = $('#bookmarks-tmpl').html();
            var html = _.template(template, {bookmarks: this.collection.toJSON(), list: self.list.toJSON(), can_edit: this.list.can_edit()});
            this.$('.list').html(html);
        } else {
            this.$('.list .no-bookmarks').show();
        }
        resize_bookmarks();
    }
});
