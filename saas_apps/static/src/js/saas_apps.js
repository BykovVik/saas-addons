odoo.define("saas_apps.saas_apps", function (require) {
    "use strict";

    require('web.dom_ready');

    if (!$(".js_saas_apps").length) {
        return Promise.reject("DOM doesn't contain '.js_saas_apps'");
    }

    var MONTHLY = "month";
    var ANNUALLY = "year";
    var basket_apps = new Set();
    var basket_packages = new Set();
    var period = MONTHLY;

    // задаем свойства вида depends-<MODULE_NAME>=1
    $(".app[data-depends]").each(function(i, el) {
        var $el = $(el);
        $el.data("depends").split(",").filter(Boolean).forEach(function(depend) {
            $el.data("depends-" + depend, 1);
        });
    });

    function getAppNameByElementCallback(i, el) {
        return $(el).data("name");
    }

    function renderTotalPrice() {
        function priceCallback(i, el) {
            return $(el).data("price-" + period);
        }

        var chosen_apps = $(".app").filter(function(i, el) {
            return basket_apps.has(getAppNameByElementCallback(i, el));
        });

        var chosen_apps_prices = chosen_apps.map(priceCallback).get();

        var chosen_packages = $(".package").filter(function(i, el) {
            return basket_packages.has($(el).data("package-id"));
        });

        var chosen_packages_prices = chosen_packages.map(priceCallback).get();

        var sum_app_prices = _.reduce(chosen_apps_prices, function(a, c) {
            return a + c;
        }, 0);

        var sum_package_prices = _.reduce(chosen_packages_prices, function(a, c) {
            return a + c;
        }, 0);

        var sum_user_prices = $("#users").val() * parseFloat($("#users_block").data("price-" + period));

        $("#price").html((sum_app_prices + sum_package_prices + sum_user_prices).toString());
        $("#box-period").html(period);
    }

    function renderApps() {
        $(".app").each(function(i, el) {
            var $app = $(el);
            if (basket_apps.has($app.data("name"))) {
                $app.addClass("green-border");
            } else {
                $app.removeClass("green-border");
            }
        });
    }

    $(".app").on("click", function() {
        var $el = $(this);
        var name = $el.data("name");
        if (basket_apps.has(name) === false) {
            basket_apps.add(name);
            var app_names_to_select = $el
                .data("depends")
                .split(",")
                .filter(Boolean)  // take away falsy values
                .concat([name]);
            app_names_to_select.forEach(function(app_name) {
                basket_apps.add(app_name);
            });
        } else {
            var app_names_to_deselect = [name];
            while (app_names_to_deselect.length > 0) {
                var app_names_to_deselect_next = [];
                app_names_to_deselect.forEach(function(app_name) {
                    // Remove from basket
                    basket_apps.delete(app_name);

                    // Find other apps that depend on this
                    app_names_to_deselect_next = app_names_to_deselect_next.concat(
                        $(".app:data(depends-" + app_name + ")").map(getAppNameByElementCallback).get()
                    );
                });
                app_names_to_deselect = app_names_to_deselect_next;
            }
        }
        renderApps();
        renderTotalPrice();
    });

    renderTotalPrice();
});
