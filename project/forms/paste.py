from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import InputRequired
from wtforms.validators import Length
from wtforms.validators import Optional
from wtforms.widgets import HiddenInput

from project.functions import list_languages


class BasePasteForm(FlaskForm):
    body = TextAreaField(
        validators=[InputRequired(), Length(max=65000)], render_kw={"class": "pastebox"}
    )


class PasteForm(BasePasteForm):
    name = StringField(
        "Name:", validators=[Optional()], render_kw={"placeholder": "(optional)"}
    )
    lang = SelectField(
        "Language:",
        validators=[InputRequired()],
        # (lang_code, label) e.g. ("csharp", "C#")
        choices=[(lang[1][0], lang[0]) for lang in list_languages()],
    )


class PasteEditForm(BasePasteForm):
    id = IntegerField(widget=HiddenInput(), validators=[InputRequired()])
    commit = IntegerField(widget=HiddenInput(), default=None)
    commit_message = TextAreaField(
        validators=[Optional(), Length(max=1024)],
        render_kw={"placeholder": "commit message"},
    )
