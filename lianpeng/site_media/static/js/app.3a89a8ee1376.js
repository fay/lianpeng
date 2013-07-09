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
    },
});
