var window_height;
var lists_view;
var List = Backbone.Model.extend({
    urlRoot: '/api/v1/list/',
    can_edit: function() {
        var result = false;
        if(this.get('user') == USER_URL) {
            result = true;
        }
        var perms = this.get('perms');
        if(perms) {
            for (var i = 0; i < perms.length; i++) {
                if ('can_edit' == perms[i]){
                    result = true;
                    break;
                };
            };
        }
        return result;
    },
    can_comment: function() {
        return true;
    }
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
var SharedLists = Lists.extend({
    baseUrl: '/api/v1/list/share/'
});
var ListInvitation = Backbone.Model.extend({
    urlRoot: '/api/v1/listinvitation/'
});
var ListInvitations = BaseCollection.extend({
    model: ListInvitation,
    url: '/api/v1/listinvitation/'
});
var ListView = Backbone.View.extend({
    events : {
        'click .list-name': 'redirect'
    },
    initialize: function() {
        var self = this;
        this.model.bind("destroy", this.delete_model, this);
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
    delete_model: function() {
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
        var html = _.template(template, {list: list.toJSON(), 'can_edit': list.can_edit()});
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
var ListInvitationView = Backbone.View.extend({
    events: {
        'change select.permission' : 'change_invitee_permission',
        'click .delete' : 'remove_invitee_permission',
    },
    initialize: function() {
    },
    remove_invitee_permission: function(e) {
        this.model.destroy();
        this.remove();
    },
    change_invitee_permission: function(e) {
        var select = $(e.currentTarget);
        var new_permission = select.val();
        this.model.save({permission: new_permission});
    }
});
var ListSettingView = Backbone.View.extend({
    events: {
        'click .delete-list': "delete_list",
        'click .invite-list': "show_invite",
        'click .list-edit-modal .save' : 'update',
        'click .invite-list-modal .invite' : 'invite',
        'submit .invite-list-modal form' : 'invite',
        'submit .list-edit-modal form' : 'update',
        'click .edit-list': "edit"
    },
    initialize: function() {
        this.model.bind('change', this.render, this);
        this.render();
        this.list_invitations = new ListInvitations();
        this.list_invitations.bind("reset", this.render_invitees, this);
        this.list_invitations.bind("add", this.append_invitee, this);
    },
    render: function() {
        var template = $('#list-header-tmpl').html();
        var html = _.template(template, {list:this.model.toJSON(), can_edit: this.model.can_edit()});
        this.$el.html(html);
    },
    delete_list: function() {
        var result = confirm("确认删除？"); 
        if (result) {
            this.model.destroy();
        }
    },
    render_invitees: function(data) {
        this.$('.invite-list-modal #invitee-list').html('');
        for (var i = 0; i < data.models.length; i++) {
            this.append_invitee(data.models[i]);
        };
    },
    append_invitee: function(invitee) {
        var template = $('#invitee-list-tmpl').html();
        var html = $(_.template(template, {invitees: [invitee.toJSON()]}));
        this.$('.invite-list-modal #invitee-list').append(html);
        var list_invitation_view = new ListInvitationView({model: invitee, el: html});
    },
    show_invite: function() {
        this.list_invitations.fetch({url: this.list_invitations.url + "?list=" + this.model.id});
        this.$('.invite-list-modal').modal(); 
    },
    invite: function() {
        var form = this.$('.invite-list-modal form');
        var data = F.form2json(form);
        var invitee_string = data.invitee;
        var invitees = invitee_string.split(',');
        for (var i = 0; i < invitees.length; i++) {
            var invitee = $.trim(invitees[i]);
            if (invitee) {
                data.invitee = invitee;
                this.list_invitations.create(data, {wait:true, success: function(){
                    form.find('.invited').hide();
                    form.find('input[name="invitee"]').val(""); 
                }, error: function(){
                    form.find('.invited').show();
                }});
            }
        };
        return false;
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
        this.collection.bind('destroy', function(){this.resize_height(-26);}, this);// resize sidebar list height after a list is deleted
        this.collection.bind("reset", this.render, this);
        this.collection.bind("reset", this.user_lists_loaded, this);
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
    render: function(data, resp, target) {
        var self = this;
        if(!target) {
            target = 'ul.lists-ul';
        }
        //this.$(target).html('');
        $.each(data.models, function(index, list){
            self.append_new_list(list, data, null, target);
        });
        if (!this.$('.jquery-bootstrap-pagination').html()) {
            F.show_paginator(self, 4, function(){
            });
        }
        this.$('.jquery-bootstrap-pagination').addClass("pagination-mini");
        this.resize_height();
    },
    resize_height: function(height) {
        var user_lists_height = $('.user-lists').height();
        var user_lists_max_height = window_height - 320;
        if (user_lists_max_height < user_lists_height) {
            user_lists_height = user_lists_max_height;
        }
        if (height) {
            user_lists_height += height;
        }
        $('.user-lists').css('height', user_lists_height);

    },
    append_new_list: function(list, collection, resp, target) {
        var template = $('#list-tmpl').html();
        var html = _.template(template, {lists: [list.toJSON()]});
        if (!target) {
            target = 'ul.lists-ul';
        }
        var kind = list.get('kind');
        if (kind == 0) {
            target = '.sys-lists .nav';// if it's sys list, append it to sys ul
        } else if(kind == 3){
            target = '.shared-lists-ul';
        } else {
            this.$('.user-lists-sep').show();
        }
        this.$(target + '-sep').show();
        target = this.$(target);
        target.append(html);
        target.show();
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
        var height = 28;
        if(this.collection.size() <= 2) {
            height = 48;
        }
        this.resize_height(height);
        return false;
    }
});


$(document).ready(function(){ 
    lists_view = new ListsView();
    var all_list = new List({id:"all"});
    var all_list_view = new FilterView({model: all_list, el: "#all-list", fake_list: true});
    var feed_list = new List({id:"feed"});
    var feed_list_view = new FilterView({model: feed_list, el: "#feed", fake_list: true});
    var try_times = 0;

    var AppRouter = Backbone.Router.extend({
        routes: {
            '': "index",
            ':username/list/all': "index",
            ':username/list/feed': "feed",
            ':username/list/:id': "list",
            ':username/tag/:tag': "tag",
            ':username/search/:query': "search"
        },

        index: function(username) {
            $('body').animate({scrollTop: 0});
            lists_view.render_current_list_view(all_list_view);
        },
        feed: function(username) {
            $('body').animate({scrollTop: 0});
            lists_view.render_current_list_view(feed_list_view);
        },
        list: function(username, id) {
            $('body').animate({scrollTop: 0});
            var list_view = lists_view.views[id];
            var list_id = id;
            if (list_view) {
                list_view.render();
            } else {
                if (try_times <= 8) {
                    setTimeout(function(){router.list(username, id)}, 400);
                    try_times ++;
                }
            }
        },
        search: function(username, query) {
            $('body').animate({scrollTop: 0});
            var list = new List({id:"search", query:query, name:TEXTS['search_title'] + decodeURI(query)});
            var list_view = new SearchView({model: list, el: "#no-such-dom", fake_list: true});
            lists_view.render_current_list_view(list_view);
        },
        tag: function(username, tag) {
            $('body').animate({scrollTop: 0});
            var list = new List({id:"tag", tag:tag, name:TEXTS['tag_title'] + tag});
            var list_view = new TagView({model: list, el: "#no-such-dom", fake_list: true});
            lists_view.render_current_list_view(list_view);
        }
    });
    router = new AppRouter();
    window_height = $(window).height();
    $('#bookmarks').css('min-height', window_height);
    $('#lists').css('min-height', window_height);

    sidebarwidth = $(".sidebar-width").css('width');
    bodypaddingtop = $(".navbar-fixed-top").css('height');
    $('.sidebar-nav-fixed').css('width', sidebarwidth);
    contentmargin = parseInt(sidebarwidth)
    $('.span-fixed-sidebar').css('marginLeft', contentmargin);
    $('.span-fixed-sidebar').css('paddingLeft', 60);

    Backbone.history.start({pushState: true});

});
