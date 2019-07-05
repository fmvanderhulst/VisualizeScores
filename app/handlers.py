import webapp2
import math
import datetime
import jinja2
import os
import logging


from app.models import *
from app.elo_rating import *
from google.appengine.api import users
from google.appengine.api import app_identity
import sys
sys.path.insert(0, 'lib')
import cloudstorage as gcs


# initialise templating engine
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainHandler(webapp2.RequestHandler):
  def get(self):
    template_values = {
        "rankings": Competitor.ordered(), 
        }
    template = jinja_environment.get_template('templates/rankings.html')
    self.response.out.write(template.render(template_values)) 

class StartHandler(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('templates/index.html')
    self.response.out.write(template.render()) 


class AddResultHandler(webapp2.RequestHandler):
  def get(self):
    if self.request.get("userid"):
      competitor = Competitor.by_id(self.request.get("userid"))
      logging.info("get results for %s " % (competitor.nickname))
    else:
      competitor = Competitor.by_newestdate()
      logging.info("get results for %s based on date" % (competitor.nickname))
    if competitor.nickname:
      try:
        data = self.getData((competitor.nickname+str(competitor.userid)))
      except:
        data = None
    else:
      data = {"X1":{"0":-1.0,"1":-2.0},"X2":{"0":0.0,"1":1.0},"Y1":{"0":2.0,"1":2.0},"Y2":{"0":1.0,"1":1.0}}

    template_values = {
      'user': competitor,
      'competitors': Competitor.ordered(),
      'data': data,
    }
    template = jinja_environment.get_template('templates/result.html')
    self.response.out.write(template.render(template_values))

  def getData(self,name):
      # self.response.out.write('Reading the full file contents:\n')
      gcs_file = gcs.open('/franky-test-bucket/'+name)
      contents = gcs_file.read()
      gcs_file.close()
      return(contents)

class ActiveUser():
  def __init__(self):
    # initialize with a appengine user object
    self.loaded = False
    if self.load():
      self.loaded = True
    
  def load(self):
    user = users.get_current_user()
    if user:
      u = self.find_or_add_user(user)
      self.userid = u.userid
      self.nickname = u.nickname
      self.totalscore = u.totalscore
      self.include_in_rankings = u.include_in_rankings
      self.coverage = u.coverage
      self.quality = u.quality
      self.speed = u.speed
      self.signout_url = users.create_logout_url("/")
      return True

  def find_or_add_user(self,user):
    if user:
      u = Competitor.by_id(user.user_id())
      if u is None:
        u = Competitor(
            userid = user.user_id(),
            nickname = user.nickname()
            )
        u.put()
        logging.info("added competitor " + u.userid)
      else:
        logging.info("recognised competitor " + u.userid)
      return u
      
  class StorageHandler(webapp2.RequestHandler):
    def get(self):
      bucket_name = os.environ.get('BUCKET_NAME',
                                  app_identity.get_default_gcs_bucket_name())

      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('Demo GCS Application running from Version: '
                          + os.environ['CURRENT_VERSION_ID'] + '\n')
      self.response.write('Using bucket name: ' + bucket_name + '\n\n')

