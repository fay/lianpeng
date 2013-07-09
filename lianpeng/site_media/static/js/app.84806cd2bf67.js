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
var USER_URL = "/api/v1/user/" + USER_ID;
var Bookmark = Backbone.Model.extend({
    urlRoot: '/api/v1/bookmark/'
});

var BaseCollection = Backbone.Collection.extend({
    parse: function(data) {
        this.total_count = data.meta.total_count;
        return data.objects;
    }
});

var List = Backbone.Model.extend({
    urlRoot: '/api/v1/list/'
});

var FilterList = List.extend({
    
});
var Lists = BaseCollection.extend({
    model: List,
    initialize: function() {
        Backbone.Pagination.enable(this, {
            page_attr: "offset",
            ipp: 100,
            ipp_attr: "limit"
        });
    },
    baseUrl: '/api/v1/list/'
});
var ListView = Backbone.View.extend({
    events : {
        'click .list-name': 'redirect'
    },
    initialize: function() {
        var self = this;
        this.model.bind("destroy", this.delete, this);
        this.model.bind("change", this.change_name, this);
        this.$el.droppable({
            accept: '.bookmark-entry-box',
            tolerance: 'pointer',
            drop: _.bind(function(event, ui) {
                var object = $(event.target);
                var bookmark_id = $(ui.draggable).data('id');
                var list_id = $(ui.draggable).data('list-id')
                self.trigger('dropped', list_id, bookmark_id, self.model);
                $(ui.draggable).remove();
            }, this),
            over: _.bind(function(event,ui){
                var object = $(event.target);
                if (object.hasClass('active')) {
                    object.addClass('source');
                } else {
                    object.addClass('active');
                }
            }, this),
            out: _.bind(function(event,ui){
                var object = $(event.target);
                if (!object.hasClass('source')) {
                    object.removeClass('active');
                }
            }, this)
        });

    },
    delete: function() {
        this.remove();
        $('#all-list .list-name').click();
    },
    redirect: function() {
        var newFragment =  USER_NAME + '/list/' + this.model.id;
        if (Backbone.history.fragment == newFragment) {
            // need to null out Backbone.history.fragement because 
            // navigate method will ignore when it is the same as newFragment
            Backbone.history.fragment = null;
        }
        Backbone.history.navigate(newFragment, true);
    },
    render: function() {
        var list = this.model;
        var template = $('#list-bookmarks-tmpl').html();
        var html = _.template(template, {list: list.toJSON()});
        $('#bookmarks').html(html);
        $('#bookmarks').spin();

        this.bookmarks = new Bookmarks({list:this.model});
        this.bookmarks.bind("reset", this.stop_spin, this);
        this.model.bookmarks = this.bookmarks;
        
        this.bookmarks_view = new BookmarksView({
            collection:this.bookmarks, 
            el: "#bookmarks #list-bookmarks-" + this.model.id + " .bookmarks", 
            list:this.model
        });
        this.bookmarks.fetch();

        this.list_setting_view = new ListSettingView({
            el:"#bookmarks #list-bookmarks-" + this.model.id + " .list-header", 
            model: this.model
        });

        $('#lists li').removeClass('active');
        this.$el.addClass('active');

    },
    stop_spin: function() {
        $('#bookmarks').spin(false);
    },
    change_name: function() {
        this.$('.list-name .name-text').text(this.model.get('name'));
    }
});
var FilterView = ListView.extend({
    initialize: function() {
    }
});
var SearchView = ListView.extend({
    render: function(){
        ListView.prototype.render.call(this);
        $('.add-bookmark-form-box').hide();
        $('.list-setting-box').hide();
    }
});
var TagView = SearchView.extend({});
var ListSettingView = Backbone.View.extend({
    events: {
        'click .delete-list': "delete",
        'click .list-edit-modal .save' : 'update',
        'submit .list-edit-modal form' : 'update',
        'click .edit-list': "edit"
    },
    change_name: function() {
        this.$('.list-name').text(this.model.get('name'));
    },
    initialize: function() {
        this.model.bind('change', this.change_name, this);
    },
    delete: function() {
        this.model.destroy();
    },
    edit: function() {
        this.$('.list-edit-modal').modal();
    },
    update: function() {
        this.$('.list-edit-modal').modal("hide");
        var form = this.$('.list-edit-modal form');
        var data = F.form2json(form);
        if (!('public' in data)) {
            data['public'] = false;
        }
        this.model.save(data);
        return false;
    }
});
var ListsView = Backbone.View.extend({
    el: '#lists',
    events: {
        'click .new-list-button': 'show_add_form',
        'submit .new-list-form': 'add'
    },
    views: {},
    current_list: null,
    initialize: function() {
        var self = this;
        this.collection = new Lists();
        this.collection.bind('add', this.append_new_list, this);
        this.collection.bind("reset", this.render, this);
        this.collection.fetch();

        this.bookmarks = this.options['bookmarks'];
        this.$(".lists-ul").sortable({
            revert: true,
            start: function(event, ui) {
            },
            stop: function(event, ui) {
                var id = $(ui.item).data('id');
                var list = self.collection.get(id);
                list.save({position:ui.item.index()});
            }
        });
    },
    render_current_list_view: function(list_view) {
        this.current_list_view = list_view;
        this.current_list_view.render();
    },
    render: function() {
        var self = this;
        this.$('ul.lists-ul').html('');
        $.each(this.collection.models, function(index, list){
            self.append_new_list(list);
        });
        if (!this.$('.jquery-bootstrap-pagination').html()) {
            F.show_paginator(self, 4, function(){
            });
        }
        this.$('.jquery-bootstrap-pagination').addClass("pagination-mini");
        this.resize_height();
    },
    resize_height: function() {
        var user_lists_height = $('.user-lists').height();
        var user_lists_max_height = window_height - 290;
        if (user_lists_max_height < user_lists_height) {
            user_lists_height = user_lists_max_height;
        }
        $('.user-lists').css('height', user_lists_height);

    },
    append_new_list: function(list) {
        var template = $('#list-tmpl').html();
        var html = _.template(template, {lists: [list.toJSON()]});
        var target = this.$('ul.lists-ul');
        var kind = list.get('kind');
        if (kind != 2) {
            target = this.$('.sys-lists .nav');// if it's sys list, append it to sys ul
        }
        target.append(html);
        var self = this;
        var list_view = new ListView({model: list, el:'#list-' + list.id});
        this.views[list.id] = list_view;
        list_view.bind('seleted', this.list_selected, this);
        list_view.bind('dropped', this.list_dropped, this);
        list.bind("destroy", this.render_all_list, this);
    },
    show_add_form: function() {
        $('.new-list-button').hide();
        $('.new-list-form').show();
        $('.new-list-form').find('input.list-name').focus();
    },
    list_dropped: function(list_id, bookmark_id, target_list) {
        if (typeof(list_id) != 'number') {
            var source_list = this.current_list_view.model;
        } else {
            var source_list = this.collection.get(list_id);
        }
        var bookmark = source_list.bookmarks.get(bookmark_id);
        bookmark.save({list:target_list.url()});
    },
    list_selected: function(list) {

    },
    add: function(e) {
        var form = $(e.currentTarget);
        var data = F.form2json(form);
        data['user'] = USER_URL; 
        this.collection.create(data, {wait:true});
        $('.new-list-button').show();
        $('.new-list-form').hide();
        form.find('input.list-name').val("");
        return false;
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
            "click .share-action": "share",
            "click .shares .douban": "share_douban",
            "hover": "show_actions",
            "hover .move": "enable_drag",
            "mouseleave .move": "disable_drag",
            "click .remove-action": "remove"
        }
        this.list = this.options['list'];
        this.listenTo(this.model, 'destroy', this.remove_bookmark_html);
        this.listenTo(this.model, 'change', this.append_bookmark_html);
    },
    share: function(e) {
        $(e.currentTarget).dropdown('toggle')
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
    enable_drag:function() {
        this.$el.draggable({
            helper: "clone",
        });
        this.$el.draggable("enable");
    },
    disable_drag: function() {
        this.$el.draggable( "disable" )
    },
    show_actions: function() {
        this.$('.move').toggle();
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
        var html = _.template(template, {bookmarks: [bookmark.toJSON()], list: this.list})
        this.$el.html($(html).html());
    },
    edit: function(){
        var self = this;
        var template = $('#bookmark-form-tmpl').html();
        var html = _.template(template, {bookmark: self.model.toJSON()});
        this.$('.bookmark-title-box').hide();
        this.$('.edit-bookmark-box').html(html);

        self.$('.edit-bookmark-box form').submit(function(e){
            
            self.model.save(F.form2json(this));
            self.$('.bookmark-title-box').show();
            return false;
        });
        self.$('.edit-bookmark-box form .cancel').click(function(){
            self.$('.edit-bookmark-box').hide(); 
            self.$('.bookmark-title-box').show();
        });
    }
});
var BookmarksView = Backbone.View.extend({
    events: {
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
    },
    add_bookmark: function(e) {
        var url = $(e.currentTarget).find('.url').val();
        $(e.currentTarget).spin();
        $(e.currentTarget).find('input').attr('disabled', 'on');
        var self = this;

        // fetch web page info
        F.fetch_title(url, function(data) {
            $(e.currentTarget).spin(false);
            data = $.parseJSON(data);
            if (data) {
                var domain = F.url_domain(url); 
                var bookmark_dict = {url: url,
                    user: USER_URL,
                    title: data.title,
                    domain: domain,
                    note: data.description
                };
                var template = $('#bookmark-form-tmpl').html();
                var html = _.template(template, {bookmark: bookmark_dict});
                self.$('.confirm-add-bookmark').html(html).show();

                // check if existed
                self.$('.confirm-add-bookmark .existed-bookmark .spinner').spin({length:0, radius:6, width:2});
                var existed_bookmarks = new Bookmarks();
                existed_bookmarks.bind("reset", function(data){
                    self.$('.confirm-add-bookmark .existed-bookmark .spinner').spin(false);
                    
                    if (data.total_count > 0) {
                        var existed_bookmark = data.models[0]
                        self.$('.confirm-add-bookmark .existed-bookmark').addClass('alert');
                        self.$('.confirm-add-bookmark .existed-bookmark .text').show();
                        self.$('.confirm-add-bookmark .existed-bookmark .edit').click(function(){
                            if (!self.collection.get(existed_bookmark.id)) {
                                self.collection.push(existed_bookmark );
                            }
                            self.$('.confirm-add-bookmark .existed-bookmark .edit').attr('href', '#bookmark-' + existed_bookmark.id);
                            self.$('.list #bookmark-' + existed_bookmark.id + ' .bookmark-title-box .actions .edit-action').trigger('click');
                            self.recover_submit_form(e.currentTarget);
                        });
                    } else {
                        self.$('.confirm-add-bookmark .existed-bookmark').hide();
                    }
                });
                existed_bookmarks.fetch({url:existed_bookmarks.url() + "&url=" + url});

                // create new bookmark
                self.$('.confirm-add-bookmark form').submit(function(){
                    var new_bookmark = F.form2json(this);
                    if (self.list.id != 'all') {
                        new_bookmark.list = self.list.url();
                    }
                    self.collection.create(new_bookmark, {wait:true, success:function(data){
                    }});
                    self.recover_submit_form(e.currentTarget);
                    return false;
                });
                // hide confirm form and enable add-bookmark form
                self.$('.confirm-add-bookmark form .cancel').click(function(){
                    self.recover_submit_form(e.currentTarget);
                });
            };
        });
        return false;
    },
    recover_submit_form: function(form) {
        $('.confirm-add-bookmark').hide(); 
        $(form).find('input').removeAttr('disabled');
        $(form).find('input.url').val("");
    },
    append_bookmark_html: function(bookmark) {
        var template = $('#bookmarks-tmpl').html();
        var html = _.template(template, {bookmarks: [bookmark.toJSON()], list: this.list.toJSON()});
        
        this.$('.no-bookmarks').hide();
        this.$('.list').prepend(html);
    },
    render_pagination: function() {
        if (!this.$('.jquery-bootstrap-pagination').html()) {
            var self = this;
            F.show_paginator(self, 8, function(){
                $(self.$('.list').children()[0]).spin();
            }); 
        }
        //this.$('.jquery-bootstrap-pagination').addClass("pagination-right");
    },
    render: function() {
        var self = this;
        if (this.collection.size() > 0) {
            var template = $('#bookmarks-tmpl').html();
            var html = _.template(template, {bookmarks: this.collection.toJSON(), list: self.list.toJSON()});
            this.$('.list').html(html);
        } else {
            this.$('.list .no-bookmarks').show();
        }
    }
});


var lists_view = new ListsView();
var all_list = new List({id:"all"});
var all_list_view = new FilterView({model: all_list, el: "#all-list", fake_list: true});

var AppRouter = Backbone.Router.extend({
    routes: {
        '': "index",
        ':username/list/all': "index",
        ':username/list/:id': "list",
        ':username/tag/:tag': "tag",
        ':username/search/:query': "search"
    },

    index: function(username) {
        lists_view.render_current_list_view(all_list_view);
    },
    list: function(username, id) {
        var list_view = lists_view.views[id];
        var list_id = id;
        if (list_view) {
            list_view.render();
        } else {
            var list = new List({id: list_id});
            var list_view = new ListView({model:list});
            list.bind("change", function(list){ 
                list_view.render();
            });
            list.fetch();
        }
    },
    search: function(username, query) {
        var list = new List({id:"search", query:query, name:TEXTS['search_title'] + query});
        var list_view = new SearchView({model: list, el: "#no-such-dom", fake_list: true});
        lists_view.render_current_list_view(list_view);
    },
    tag: function(username, tag) {
        var list = new List({id:"tag", tag:tag, name:TEXTS['tag_title'] + tag});
        var list_view = new TagView({model: list, el: "#no-such-dom", fake_list: true});
        lists_view.render_current_list_view(list_view);
    }
});
var router = new AppRouter();
var window_height = $(window).height();
$('#bookmarks').css('min-height', window_height);
$('#lists').css('min-height', window_height);

sidebarwidth = $(".sidebar-width").css('width');
bodypaddingtop = $(".navbar-fixed-top").css('height');
$('.sidebar-nav-fixed').css('width', sidebarwidth);
contentmargin = parseInt(sidebarwidth)
$('.span-fixed-sidebar').css('marginLeft', contentmargin);
$('.span-fixed-sidebar').css('paddingLeft', 60);
Backbone.history.start({pushState: true});
