/** @odoo-module */
// Bilal
import { registry } from "@web/core/registry"
import { formView } from "@web/views/form/form_view"
import { FormController } from "@web/views/form/form_controller"
const { useEffect } = owl


class ReadonlyFormController extends FormController {

    setup(){
        // console.log("form inherited!")
        super.setup()

        useEffect(()=>{  
            // this.props.preventEdit = true
            this.disableForm()
        }, ()=>[this.model.root.data.readonly_check])

        this.onNotebookPageChange = (notebookId, page) => {
            this.disableForm()
            // this.props.preventEdit = true
        };
    }

    disableForm(){
        const inputElements = document.querySelectorAll(".o_form_sheet input")
        const fieldWidgets = document.querySelectorAll(".o_form_sheet .o_field_widget")

        const check = this.model.root.data.readonly_check == true
        console.log("------> check", check)
        if (check){
            // console.log("IF Condistion " ,this.props.preventEdit)
            this.props.preventEdit = true
            if (inputElements) inputElements.forEach(e => e.setAttribute("disabled", 1))
            if (fieldWidgets) fieldWidgets.forEach(e => e.classList.add("pe-none"))
            this.canEdit = false
        } else {
            this.props.preventEdit = false
            // console.log("else Condistion " ,this.props.preventEdit)
            if (inputElements) inputElements.forEach(e => e.removeAttribute("disabled"))
            if (fieldWidgets) fieldWidgets.forEach(e => e.classList.remove("pe-none"))
            this.canEdit = true
        }
    }
    async beforeLeave() {
        if (this.model.root.data.readonly_check == true) return
        super.beforeLeave()
    }

    async beforeUnload(ev) {
        if (this.model.root.data.readonly_check == true) return
        super.beforeUnload(ev)
    }
}

const readonlyFormView = {
    ...formView,
    Controller: ReadonlyFormController,
}

registry.category("views").add("view_form_disable_readonly", readonlyFormView)