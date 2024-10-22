odoo.define('fastra_inventory_sheadul.asset_schedule_template', function (require) {
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var CustomDashBoard = AbstractAction.extend({
        template: 'fastra_inventory_sheadul.assetSchedule',
        events: { },
        init: function (parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['fastra_inventory_sheadul.assetSchedulereport'];
            this.today_sale = [];
        },
        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function () {
                return self.fetch_data();
            });
        },
        start: function () {
            var self = this;
            this.set("title", 'Asset schedule');
            return this._super().then(function () {
                self.render_dashboards();
            });
        },
        render_dashboards: function () {
            var self = this;
            console.log(self)
            _.each(this.dashboards_templates, function (template) {
                self.$('.o_pj_dashboard').append(QWeb.render(template, {
                    widget: self
                }));
            });
        },
        fetch_data: function () {
            var self = this;
            var def1 = this._rpc({
                model: 'request.inventory.line',
                method: 'get_repport_data'
            }).then(function (result) {

                self.data = result

                console.log(result)
            });
            return $.when(def1);
        }
       
       
     



        

    })
    core.action_registry.add('asset_schedule_template_tags', CustomDashBoard);
    return CustomDashBoard;
})