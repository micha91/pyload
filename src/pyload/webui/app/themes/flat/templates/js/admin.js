{% autoescape true %}
var root;
root = this;
window.addEvent("domready", function() {
    var f, c, b, e, a, d;
    root.passwordDialog = new MooDialog({
        destroyOnHide: false
    });
    root.passwordDialog.setContent($("password_box"));
    $("login_password_reset").addEvent("click", function(g) {
        return root.passwordDialog.close()
    });
    $("login_password_button").addEvent("click", function(j) {
        var h, i, g;
        i = $("login_new_password").get("value");
        g = $("login_new_password2").get("value");
        if (i === g) {
            h = $("password_form");
            h.set("send", {
                onSuccess: function(k) {
                    return root.notify.alert("Success", {
                        className: "success"
                    })
                },
                onFailure: function(k) {
                    return root.notify.alert("Error", {
                        className: "error"
                    })
                }
            });
            h.send();
            root.passwordDialog.close()
        } else {
            alert('{{_("Passwords did not match.")}}')
        }
        return j.stop()
    });
    d = $$(".change_password");
    for (e = 0, a = d.length; e < a; e++) {
        c = d[e];
        f = c.get("id");
        b = f.split("|")[1];
        $("user_login").set("value", b);
        c.addEvent("click", function(g) {
            return root.passwordDialog.open()
        })
    }
    $("quit-pyload").addEvent("click", function(g) {
        new MooDialog.Confirm("{{_('You are really sure you want to quit pyLoad?')}}", function() {
            return new Request.JSON({
                url: "/api/kill",
                method: "get"
            }).send()
        }, function() {});
        return g.stop()
    });
    return $("restart-pyload").addEvent("click", function(g) {
        new MooDialog.Confirm("{{_('Are you sure you want to restart pyLoad?')}}", function() {
            return new Request.JSON({
                url: "/api/restart",
                method: "get",
                onSuccess: function(h) {
                    return alert("{{_('pyLoad restarted')}}")
                }
            }).send()
        }, function() {});
        return g.stop()
    })
});
{% endautoescape %}