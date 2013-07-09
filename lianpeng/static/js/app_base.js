var BaseCollection = Backbone.Collection.extend({
    parse: function(data) {
        this.total_count = data.meta.total_count;
        return data.objects;
    }
});
