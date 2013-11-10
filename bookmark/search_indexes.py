import datetime
from haystack import indexes
from bookmark.models import Bookmark

class BookmarkIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    user_id = indexes.IntegerField(model_attr='user__id')
    list = indexes.CharField(model_attr='list', null=True)
    created_time = indexes.DateTimeField(model_attr='created_time')

    def get_model(self):
        return Bookmark

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_time__lte=datetime.datetime.now())
