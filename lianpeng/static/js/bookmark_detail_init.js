var comments_view = new CommentsView({el:'#bookmark-' + bookmark_id + " .comments-box", bookmark: {id:bookmark_id}});
comments_view.fetch();

