/** @odoo-module */

import { useService } from "@web/core/utils/hooks";
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';

export class ButtonListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");  // ✅ Fix added here
        console.log("ButtonListController initialized for res.partner");
    }

    async _test() {
        const action = await this.orm.call("payment.wht.line", "action_open_tax_payment_wizard", [[]]);
        this.action.doAction(action);  // ✅ Now this.action is defined
    }

    async _test_2() {
        const action = await this.orm.call("payment.wht.line", "action_open_certificate_wizard", [[]]);
        this.action.doAction(action);  // ✅ Now this.action is defined
    }
}

registry.category("views").add("button_name", {
    ...listView,
    Controller: ButtonListController,
    buttonTemplate: "button_payment_wht.ListView.Buttons",
});
