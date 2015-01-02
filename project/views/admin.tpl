<!doctype html>
<html>
    <head>
        <title>super secret admin panel do not leek</title>
    </head>
    <body>
        <form method="post" action="/admin/deletehits">
            Delete uploads for <input type="text" value="" placeholder="key" name="key" /> where hits below or are equal to:
            <input type="text" name="hit_threshold" />
            <br />
            <input type="checkbox" name="all_keys" /> Delete from all keys
            <input type="submit" />
        </form>
    </body>
</html>