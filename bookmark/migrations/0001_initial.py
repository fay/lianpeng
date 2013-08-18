# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'List'
        db.create_table('bookmark_list', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True, blank=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('kind', self.gf('django.db.models.fields.IntegerField')(default=2, db_index=True)),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('modified_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
        ))
        db.send_create_signal('bookmark', ['List'])

        # Adding model 'ListUserObjectPermission'
        db.create_table('bookmark_listuserobjectpermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Permission'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('content_object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bookmark.List'])),
        ))
        db.send_create_signal('bookmark', ['ListUserObjectPermission'])

        # Adding unique constraint on 'ListUserObjectPermission', fields ['user', 'permission', 'content_object']
        db.create_unique('bookmark_listuserobjectpermission', ['user_id', 'permission_id', 'content_object_id'])

        # Adding model 'ListGroupObjectPermission'
        db.create_table('bookmark_listgroupobjectpermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Permission'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('content_object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bookmark.List'])),
        ))
        db.send_create_signal('bookmark', ['ListGroupObjectPermission'])

        # Adding unique constraint on 'ListGroupObjectPermission', fields ['group', 'permission', 'content_object']
        db.create_unique('bookmark_listgroupobjectpermission', ['group_id', 'permission_id', 'content_object_id'])

        # Adding model 'Bookmark'
        db.create_table('bookmark_bookmark', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('domain', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('modified_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('unique_key', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bookmark.List'], null=True, blank=True)),
        ))
        db.send_create_signal('bookmark', ['Bookmark'])

        # Adding model 'Follow'
        db.create_table('bookmark_follow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('followee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='followers', to=orm['auth.User'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='following', to=orm['auth.User'])),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('bookmark', ['Follow'])

        # Adding unique constraint on 'Follow', fields ['followee', 'user']
        db.create_unique('bookmark_follow', ['followee_id', 'user_id'])

        # Adding model 'FollowList'
        db.create_table('bookmark_followlist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bookmark.List'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('bookmark', ['FollowList'])

        # Adding unique constraint on 'FollowList', fields ['list', 'user']
        db.create_unique('bookmark_followlist', ['list_id', 'user_id'])

        # Adding model 'PickedList'
        db.create_table('bookmark_pickedlist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('list', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['bookmark.List'], unique=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('bookmark', ['PickedList'])

        # Adding model 'Feedback'
        db.create_table('bookmark_feedback', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('bookmark', ['Feedback'])

        # Adding model 'ListInvitation'
        db.create_table('bookmark_listinvitation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invitee', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bookmark.List'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('permission', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('bookmark', ['ListInvitation'])

        # Adding unique constraint on 'ListInvitation', fields ['list', 'user', 'invitee']
        db.create_unique('bookmark_listinvitation', ['list_id', 'user_id', 'invitee'])

        # Adding model 'SyncState'
        db.create_table('bookmark_syncstate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('website', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('bookmark', ['SyncState'])

        # Adding unique constraint on 'SyncState', fields ['user', 'website']
        db.create_unique('bookmark_syncstate', ['user_id', 'website'])


    def backwards(self, orm):
        # Removing unique constraint on 'SyncState', fields ['user', 'website']
        db.delete_unique('bookmark_syncstate', ['user_id', 'website'])

        # Removing unique constraint on 'ListInvitation', fields ['list', 'user', 'invitee']
        db.delete_unique('bookmark_listinvitation', ['list_id', 'user_id', 'invitee'])

        # Removing unique constraint on 'FollowList', fields ['list', 'user']
        db.delete_unique('bookmark_followlist', ['list_id', 'user_id'])

        # Removing unique constraint on 'Follow', fields ['followee', 'user']
        db.delete_unique('bookmark_follow', ['followee_id', 'user_id'])

        # Removing unique constraint on 'ListGroupObjectPermission', fields ['group', 'permission', 'content_object']
        db.delete_unique('bookmark_listgroupobjectpermission', ['group_id', 'permission_id', 'content_object_id'])

        # Removing unique constraint on 'ListUserObjectPermission', fields ['user', 'permission', 'content_object']
        db.delete_unique('bookmark_listuserobjectpermission', ['user_id', 'permission_id', 'content_object_id'])

        # Deleting model 'List'
        db.delete_table('bookmark_list')

        # Deleting model 'ListUserObjectPermission'
        db.delete_table('bookmark_listuserobjectpermission')

        # Deleting model 'ListGroupObjectPermission'
        db.delete_table('bookmark_listgroupobjectpermission')

        # Deleting model 'Bookmark'
        db.delete_table('bookmark_bookmark')

        # Deleting model 'Follow'
        db.delete_table('bookmark_follow')

        # Deleting model 'FollowList'
        db.delete_table('bookmark_followlist')

        # Deleting model 'PickedList'
        db.delete_table('bookmark_pickedlist')

        # Deleting model 'Feedback'
        db.delete_table('bookmark_feedback')

        # Deleting model 'ListInvitation'
        db.delete_table('bookmark_listinvitation')

        # Deleting model 'SyncState'
        db.delete_table('bookmark_syncstate')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'bookmark.bookmark': {
            'Meta': {'object_name': 'Bookmark'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bookmark.List']", 'null': 'True', 'blank': 'True'}),
            'modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'unique_key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'bookmark.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'bookmark.follow': {
            'Meta': {'unique_together': "(('followee', 'user'),)", 'object_name': 'Follow'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'followee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'followers'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'following'", 'to': "orm['auth.User']"})
        },
        'bookmark.followlist': {
            'Meta': {'unique_together': "(('list', 'user'),)", 'object_name': 'FollowList'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bookmark.List']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'bookmark.list': {
            'Meta': {'object_name': 'List'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'kind': ('django.db.models.fields.IntegerField', [], {'default': '2', 'db_index': 'True'}),
            'modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'bookmark.listgroupobjectpermission': {
            'Meta': {'unique_together': "([u'group', u'permission', u'content_object'],)", 'object_name': 'ListGroupObjectPermission'},
            'content_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bookmark.List']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Permission']"})
        },
        'bookmark.listinvitation': {
            'Meta': {'unique_together': "(('list', 'user', 'invitee'),)", 'object_name': 'ListInvitation'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invitee': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bookmark.List']"}),
            'permission': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'bookmark.listuserobjectpermission': {
            'Meta': {'unique_together': "([u'user', u'permission', u'content_object'],)", 'object_name': 'ListUserObjectPermission'},
            'content_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bookmark.List']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Permission']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'bookmark.pickedlist': {
            'Meta': {'object_name': 'PickedList'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['bookmark.List']", 'unique': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'bookmark.syncstate': {
            'Meta': {'unique_together': "(('user', 'website'),)", 'object_name': 'SyncState'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bookmark']