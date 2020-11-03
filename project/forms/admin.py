from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import IntegerField
from wtforms import StringField


class AdminDeleteForm(FlaskForm):
    key = StringField("Key")
    hit_threshold = IntegerField("Hits")
    all_keys = BooleanField("Delete from all keys")
