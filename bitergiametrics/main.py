#-*- python -*-
import logging
from datetime import datetime, timedelta
import urllib2

# Non-stdlib imports
import pkg_resources
import pymongo
from tg import expose, validate, redirect, flash
from tg.decorators import with_trailing_slash, without_trailing_slash
from pylons import g, c, request, response
from formencode import validators
from webob import exc
import MySQLdb

# Pyforge-specific imports
from allura.app import Application, ConfigOption, SitemapEntry
from allura.app import DefaultAdminController
from allura.lib import helpers as h
from allura.lib.search import search
from allura.lib.decorators import require_post
from allura.lib.security import has_access, require_access
from allura.lib import widgets as w
from allura.lib.widgets.subscriptions import SubscribeForm
from allura.lib.widgets import form_fields as ffw
from allura import model as M
from allura.controllers import BaseController, AppDiscussionController

# Local imports
from bitergiametrics import model as BM
from bitergiametrics import version
from bitergiametrics import widgets

from forgetracker import model as TM

log = logging.getLogger(__name__)

class W:
    thread=w.Thread(
        page=None, limit=None, page_size=None, count=None,
        style='linear')
    # pager = widgets.BlogPager()
    # new_post_form = widgets.NewPostForm()
    # edit_post_form = widgets.EditPostForm()
    view_metrics_form = widgets.ViewMetricsForm()
    # label_edit = ffw.LabelEdit()
    # subscribe_form = SubscribeForm()

class BitergiaMetricsApp(Application):
    __version__ = version.__version__
    tool_label='Metrics'
    default_mount_label='Metrics'
    default_mount_point='metrics'
    permissions = ['configure', 'read', 'write', 'admin']
    ordinal=14
    installable=True
    config_options = Application.config_options
    icons={
        24:'images/blog_24.png',
        32:'images/blog_32.png',
        48:'images/blog_48.png'
    }

    def __init__(self, project, config):
        Application.__init__(self, project, config)
        self.root = RootController()
        self.admin = MetricsAdminController(self)

    @property
    @h.exceptionless([], log)
    def sitemap(self):
        menu_id = self.config.options.mount_label.title()
        with h.push_config(c, app=self):
            return [
                SitemapEntry(menu_id, '.')[self.sidebar_menu()] ]

    @h.exceptionless([], log)
    def sidebar_menu(self):
        base = c.app.url
        links = [
            SitemapEntry('Home', base),
            SitemapEntry('Search', base + 'search'),
            ]
        return links

    def admin_menu(self):
        return super(BitergiaMetricsApp, self).admin_menu(force_options=True)

    def install(self, project):
        'Set up any default permissions and roles here'
        super(BitergiaMetricsApp, self).install(project)

        # Setup permissions
        role_admin = M.ProjectRole.by_name('Admin')._id
        role_developer = M.ProjectRole.by_name('Developer')._id
        role_auth = M.ProjectRole.by_name('*authenticated')._id
        role_anon = M.ProjectRole.by_name('*anonymous')._id
        self.config.acl = [
            M.ACE.allow(role_anon, 'read'),
            M.ACE.allow(role_developer, 'write'),
            M.ACE.allow(role_admin, 'configure'),
            M.ACE.allow(role_admin, 'admin'),
            ]

    def uninstall(self, project):
        "Remove all the tool's artifacts from the database"
        # BM.Attachment.query.remove(dict(app_config_id=c.app.config._id))
        # BM.BlogPost.query.remove(dict(app_config_id=c.app.config._id))
        # BM.BlogPostSnapshot.query.remove(dict(app_config_id=c.app.config._id))
        super(BitergiaMetricsApp, self).uninstall(project)

class RootController(BaseController):

    def __init__(self):
        # setattr(self, 'feed.atom', self.feed)
        # setattr(self, 'feed.rss', self.feed)
        # self._discuss = AppDiscussionController()
        pass
    
    @expose('jinja:bitergiametrics:templates/metrics/index.html')
    @with_trailing_slash
    def index(self, page=0, limit=10, **kw):
        query_filter = dict(app_config_id=c.app.config._id)
        if not has_access(c.app, 'write')():
            query_filter['state'] = 'published'
        # q = BM.BlogPost.query.find(query_filter)
        # post_count = q.count()
        # limit, page = h.paging_sanitizer(limit, page, post_count)
        # posts = q.sort('timestamp', pymongo.DESCENDING) \
        #         .skip(page * limit).limit(limit)
        c.form = W.view_metrics_form
        # c.pager = W.pager
        # return dict(posts=posts, page=page, limit=limit, count=post_count)
        
        # TODO: error and config management. Share db connection
        bichodb = MySQLdb.connect(user="root", db="bicho")
        cursor = bichodb.cursor()
        cursor.execute("SELECT DATE_FORMAT(submitted_on, '%Y%V') AS yearweek, COUNT(*) AS nissues FROM issues GROUP BY yearweek")
        tickets_per_week = cursor.fetchall()
        bichodb.close() 
        
        total = TM.Ticket.query.find().count()
        tickets = TM.Ticket.query.find()
        
        now = datetime.utcnow()
        week = timedelta(weeks=1)
        week_ago = now - week

        week_tickets = self.tickets_since(week_ago)
        
           
        return dict(week_ago=str(week_ago),week_tickets=week_tickets, 
                    total=total, tickets = tickets, tickets_per_week = tickets_per_week) 
    
    def tickets_since(self, when=None):
        count = 0
        if when:
            count = TM.Ticket.query.find(dict(created_date={'$gte':when})).count()
        else:
            count = TM.Ticket.query.find(dict(app_config_id=c.app.config._id)).count()
        return count

class MetricsAdminController(DefaultAdminController):
    def __init__(self, app):
        self.app = app

    @without_trailing_slash
    @expose('jinja:bitergiametrics:templates/metrics/admin_options.html')
    def options(self):
        return dict(app=self.app,
                    allow_config=has_access(self.app, 'configure')())

    @without_trailing_slash
    @expose()
    @require_post()
    def set_options(self, show_discussion=False):
        self.app.config.options['show_discussion'] = show_discussion and True or False
        flash('Metrics options updated')
        redirect(h.really_unicode(c.project.url()+'admin/tools').encode('utf-8'))
