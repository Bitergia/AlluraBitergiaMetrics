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
import json

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

    @expose('jinja:bitergiametrics:templates/metrics/bar.html')
    @with_trailing_slash
    def bar(self, page=0, limit=10, **kw):
        return dict()
    
    @expose('jinja:bitergiametrics:templates/metrics/tickets_swscopio.html')
    @with_trailing_slash
    def tickets_swscopio(self, page=0, limit=10, **kw):

        # FIXME: SQL query to get the results            
        tickets_per_month =  [
          # ['23989','1999','1','Jan 1999','10','2','2','3'],
          # ['23990','1999','2','Feb 1999','15','2','2','3'],
          # ['23991','1999','3','Mar 1999','20','4','9','3'],
          ['24135','2011','3','Mar 2011','0.56','9','23','12'],
          ['24136','2011','4','Apr 2011','0.89','2','30','15'],
          ['24137','2011','5','May 2011','0.210','5','12','50'],
          ['24138','2011','6','Jun 2011','0.300','6','3','33'],
          ['24139','2011','7','Jul 2011','0.215','2','50','45'],
          ['24140','2011','8','Aug 2011','0.120','3','88','15'],
          ['24141','2011','9','Sep 2011','0.100','8','93','84'],
          ['24142','2011','10','Oct 2011','0.20','4','87','29'],
          ['24143','2011','11','Nov 2011','0.18','4','90','88'],
          ['24144','2011','12','Dec 2011','0.45','2','15','90'],
          ['24145','2012','1','Jan 2012','0.40','3','23','56'],
          ['24146','2012','2','Feb 2012','0.37','4','80','15'],
          ['24147','2012','3','Mar 2012','0.89','7','14','9'],
          ['24148','2012','4','Apr 2012','0.121','5','78','33'],
        ]
            
        tickets_per_month_json = {}
        tickets_per_month_json['id'] = []
        tickets_per_month_json['year'] = []
        tickets_per_month_json['month'] = []
        tickets_per_month_json['date'] = []
        tickets_per_month_json['live'] = []
        tickets_per_month_json['people'] = []
        tickets_per_month_json['open'] = []
        tickets_per_month_json['close'] = []
        
        for ticket in tickets_per_month:                
            tickets_per_month_json['id'].append(ticket[0])
            tickets_per_month_json['year'].append(ticket[1])
            tickets_per_month_json['month'].append(ticket[2])
            tickets_per_month_json['date'].append(ticket[3])
            tickets_per_month_json['live'].append(ticket[4])
            tickets_per_month_json['people'].append(ticket[5])
            tickets_per_month_json['open'].append(ticket[6])
            tickets_per_month_json['close'].append(ticket[7])
        # FIXME: Find better way to find the path to the file
        f = open ("../BitergiaMetrics/bitergiametrics/nf/metrics/tickets_per_month_swscopio.json", 'w')
        # f.write(tickets_per_month)            
        f.write(json.dumps(tickets_per_month_json))            
        f.close()
                
        return dict()

    
    @expose('jinja:bitergiametrics:templates/metrics/pie.html')
    @with_trailing_slash
    def pie(self, page=0, limit=10, **kw):
        return dict()
    
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
        bichodb = None
        tickets_per_month = None
        try:
            bichodb = MySQLdb.connect(user="root", db="bicho_allura")
            cursor = bichodb.cursor()
            tickets_month_sql  = "SELECT id, DATE_FORMAT(submitted_on, '%Y') as year, "
            tickets_month_sql += "DATE_FORMAT(submitted_on, '%m') as month, "
            tickets_month_sql += "DATE_FORMAT(submitted_on, '%Y %m') AS yearmonth, "
            tickets_month_sql += "COUNT(*) AS nissues FROM issues "
            tickets_month_sql += "GROUP BY yearmonth order by yearmonth" 
            # cursor.execute("SELECT DATE_FORMAT(submitted_on, '%Y%V') AS yearweek, COUNT(*) AS nissues FROM issues GROUP BY yearweek")
            cursor.execute(tickets_month_sql) 
            tickets_per_month = cursor.fetchall()
            
            tickets_per_month_json = {}
            tickets_per_month_json['id'] = []
            tickets_per_month_json['year'] = []
            tickets_per_month_json['month'] = []
            tickets_per_month_json['date'] = []
            tickets_per_month_json['tickets'] = []
            
            for ticket in tickets_per_month:                
                tickets_per_month_json['id'].append(ticket[0])
                tickets_per_month_json['year'].append(ticket[1])
                tickets_per_month_json['month'].append(ticket[2])
                tickets_per_month_json['date'].append(ticket[3])
                tickets_per_month_json['tickets'].append(ticket[4])
            # FIXME: Find better way to find the path to the file
            f = open ("../BitergiaMetrics/bitergiametrics/nf/metrics/tickets_per_month.json", 'w')
            # f.write(tickets_per_month)            
            f.write(json.dumps(tickets_per_month_json))            
            f.close()
            
            
        except MySQLdb.Error, e:
            log.error("Error accessing Bicho %d: %s" % (e.args[0], e.args[1]))
        finally:
            if bichodb:
                bichodb.close()
                    
        
        total = TM.Ticket.query.find().count()
        tickets = TM.Ticket.query.find()
        
        now = datetime.utcnow()
        week = timedelta(weeks=1)
        week_ago = now - week

        week_tickets = self.tickets_since(week_ago)
        
           
        return dict(week_ago=str(week_ago),week_tickets=week_tickets, 
                    total=total, tickets = tickets, tickets_per_month = tickets_per_month) 
    
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
