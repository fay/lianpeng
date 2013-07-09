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
        'click .delete-list': "delete_list",
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
    delete_list: function() {
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
