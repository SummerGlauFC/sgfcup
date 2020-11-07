from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import HiddenField
from wtforms import IntegerField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import InputRequired
from wtforms.validators import NumberRange

from project.constants import FileType
from project.constants import search_modes
from project.constants import sort_modes
from project.forms import FlashErrorsForm
from project.forms import LoginForm


class GalleryAuthForm(FlashErrorsForm):
    authcode = PasswordField(
        validators=[InputRequired()],
        render_kw={"placeholder": "gallery password"},
    )
    remember = BooleanField("Remember this key")


class GallerySortForm(FlaskForm):
    class Meta:
        csrf = False

    page = IntegerField("Page", default=1, validators=[NumberRange(min=1)])
    case = BooleanField("Case-sensitive search", default=False)
    in_ = SelectField(
        "In",
        name="in",
        choices=[(idx, name[0]) for idx, name in enumerate(search_modes)],
        coerce=int,
        default=0,
    )
    query = StringField("Search", render_kw={"placeholder": "search query"})
    sort = SelectField(
        "Sort",
        choices=[(idx, name[0]) for idx, name in enumerate(sort_modes)],
        coerce=int,
        default=0,
    )

    filter = SelectField(
        "Filter by type",
        choices=[
            (FileType.ALL.value, "All file types"),
            (FileType.FILE.value, "Files only"),
            (FileType.IMAGE.value, "Images only"),
            (FileType.PASTE.value, "Pastes only"),
        ],
        default=FileType.ALL.value,
        coerce=int,
    )


class GalleryDeleteForm(FlaskForm):
    key = HiddenField()
    password = PasswordField(
        "password:",
        validators=[InputRequired()],
        render_kw={"placeholder": "key password"},
    )
    delete_selected = SubmitField("Delete Selected")
    delete_all = SubmitField("Delete All")


class GalleryAdvancedDeleteForm(LoginForm):
    type = SelectField(
        "Type",
        choices=[("hits", "Hit Count"), ("size", "Size (bytes)")],
        validators=[InputRequired()],
    )
    operator = SelectField(
        "Operator",
        choices=[
            ("gte", "greater than or equal"),
            ("lte", "less than or equal"),
            ("e", "equal"),
        ],
        validators=[InputRequired()],
    )
    threshold = IntegerField("Threshold", validators=[InputRequired()])
