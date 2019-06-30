
import logging
import operator
import datetime
from google.appengine.ext import db

# from app.elo_rating import *

BASE_RANK = 1200.0

class Competitor(db.Model):
  userid = db.StringProperty()
  nickname = db.StringProperty()
  date = db.DateTimeProperty(default=datetime.datetime.now())
  totalscore = db.FloatProperty(default=0.)
  include_in_rankings = db.BooleanProperty(default=True)
  coverage = db.FloatProperty(default=0.)
  quality = db.FloatProperty(default=0.)
  speed = db.FloatProperty(default=0.)

  @staticmethod
  def ordered():
    r = Competitor.all()
    r.order("-totalscore")
    return [c for c in r] 

  @staticmethod
  def by_id(id):
    r = Competitor.all()
    r.filter("userid =", id)
    return r.get()

  @staticmethod
  def by_newestdate():
    r = Competitor.all()
    r.order("-date")
    return(r.get())


