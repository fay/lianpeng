var Comment = Backbone.Model.extend({
    urlRoot: '/api/v1/comment/'
});
var Comments = BaseCollection.extend({
    model: Comment,
    url: '/api/v1/comment/'
});

var CommentView = Backbone.View.extend({
    events: {
        "hover": "show_actions",
        "click .remove": "delete_comment"
    },
    delete_comment: function(e) {
        this.model.destroy();
        this.remove();
    },
    show_actions: function(e) {
        this.$('.comment-actions').toggle();
    }
});
var CommentsView = Backbone.View.extend({
    events: {
        "submit form": "comment",
        "click .more": 'load_more'
    },
    loaded: false,
    current_page: 0,
    count: 0,
    initialize: function() {
        this.bookmark = this.options['bookmark'];
        this.collection = new Comments();
        this.collection.bind("reset", this.render, this);
        this.collection.bind("add", this.add_comment, this);
    },
    fetch: function() {
        this.collection.fetch({url:this.collection.url + "?limit=10&object_pk=" + this.bookmark.id});
    },
    load_more: function() {
        if (this.$('.more').hasClass('disabled')) {
            return;
        }
        var self = this;
        var limit = 10;
        var offset = this.current_page * 10;
        this.collection.fetch({
            url:this.collection.url + "?limit=" + limit + 
            "&offset=" + offset + "&object_pk=" + this.bookmark.id,
            complete: function() {
                if (self.count == self.collection.total_count) {
                    self.$('.more').addClass('disabled').text("已经没有更多的评论");
                }
            }
        });
    },
    comment: function(e) {
        var submit_btn = $(e.currentTarget).find("[type='submit']");
        if (submit_btn.hasClass("disabled")) {
            return false;
        }
        submit_btn.addClass("disabled");
        var data = F.form2json(e.currentTarget)
        if (!$.trim(data.comment)) {
            noty({text:"您必须填写评论内容", type:"warning", timeout:1000});
            return false;
        }
        this.collection.create(data, {wait:true, success: function(data){
                submit_btn.removeClass("disabled");
                $(e.currentTarget).find('textarea').val("");
            }, 
        });
        return false;
    },
    render: function() {
        var self = this;
        this.$el.show();
        $.each(this.collection.models, function(index, comment){
            self.add_comment(comment);
        });
        this.loaded = true;
        this.current_page += 1;
        this.count += this.collection.size();
        if (this.collection.total_count < 10) {
            this.$('.more-box').hide(); 
        }
        if (this.count == 0) {
            this.$('.comments').hide();
        }
    },
    add_comment: function(comment) {
        var template = $('#comment-tmpl').html();
        var html = _.template(template, {comments: [comment.toJSON()], current_user: USER_URL});
        var comment_dom = $(html);
        this.$('.comments').append(comment_dom).show();
        var comment_view = new CommentView({model:comment, el:comment_dom});
    }
});
