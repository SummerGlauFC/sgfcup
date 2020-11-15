from pprint import pprint

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_login import current_user
from flask_login import logout_user

from project.extensions import oauth
from project.forms import LoginForm
from project.functions import get_next_url
from project.functions import redirect_next
from project.services.account import AccountService
from project.services.oauth import OAuthService

blueprint = Blueprint("oauth", __name__)


@blueprint.route("/oauth/link", methods=["GET", "POST"])
def link():
    form = LoginForm()

    if not session.get("oauth"):
        return redirect(url_for("static.login", next=get_next_url(request.path)))

    if not form.is_submitted():
        form.key.data, form.key.errors = OAuthService.get_potential_name(
            session["oauth"]
        )
        form.password.data = ""

    if form.validate_on_submit() or current_user.is_authenticated:
        if current_user.is_authenticated:
            user, is_authed = current_user, current_user.is_authenticated
        else:
            user, is_authed = form.get_or_create_account()
        if user and is_authed:
            if user["hash"] is not None:
                form.key.errors.append(
                    "Given account is already linked to an OpenID, please use a different account"
                )
                return render_template("oauth_link.tpl", form=form)
            OAuthService.link(user.get_id(), session["oauth"]["sub"])
            del session["oauth"]
            flash("Successfully linked accounts!")
            form.login(user)

    return render_template("oauth_link.tpl", form=form)


@blueprint.route("/oauth/unlink", methods=["GET", "POST"])
def unlink():
    session["next"] = get_next_url(url_for("static.index"))
    if current_user.is_authenticated:
        OAuthService.link(current_user.get_id(), None)
        flash("Successfully unlinked accounts.")
    redirect_next()


@blueprint.route("/oauth/login", methods=["GET"])
def login():
    session["next"] = get_next_url()
    redirect_uri = url_for("oauth.callback", _external=True)
    return oauth.auth.authorize_redirect(redirect_uri)


@blueprint.route("/oauth/callback", methods=["GET"])
def callback():
    if "error" in request.args:
        flash("There was a problem logging you in.", "error")
        logout_user()
    else:
        token = oauth.auth.authorize_access_token()
        id_token = oauth.auth.parse_id_token(token)
        pprint(dict(token=token, user=id_token))
        subject = id_token.get("sub")
        if subject:
            user = AccountService.get_by_subject(subject)
            if user:
                LoginForm.login(user)
            else:
                # subject is not assigned to an account already
                # go through the account linking flow
                session["oauth"] = id_token
                return redirect(url_for("oauth.link"))
    return redirect(url_for("static.login"))
