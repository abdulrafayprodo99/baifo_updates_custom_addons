/** @odoo-module */

import { useService } from "@web/core/utils/hooks";
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';

export class ButtonListControllerCustom extends ListController {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action"); 
    }

    async _test() {
        const action = await this.orm.call("quality.check", "action_create_qir", [[]]);
        this.action.doAction(action);  
    }
}

registry.category("views").add("qir_button", {
    ...listView,
    Controller: ButtonListControllerCustom,
    buttonTemplate: "button_quality_check.ListView.Buttons",
});
