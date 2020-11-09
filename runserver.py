#!/usr/bin/env python
import sys

from project import create_app
from project.functions import get_setting

app = create_app()

debug_enabled = bool(get_setting("debug.enabled"))
sentry_enabled = bool(get_setting("debug.sentry.enabled"))
if sentry_enabled:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(
        dsn=get_setting("debug.sentry.url"), integrations=[FlaskIntegration()]
    )

if __name__ == "__main__":
    try:
        print("Running in this fashion is deprecated, use flask run instead.")
        port = int(sys.argv[1])
        app.run(host="localhost", port=port, debug=debug_enabled)
    except Exception as e:
        print(e)
        print("Port to run on not specified.")
