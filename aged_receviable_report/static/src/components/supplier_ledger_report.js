/** @odoo-module **/

import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
// import { rpc } from "@web/core/network/rpc_service";
const { Component, onWillStart, useState } = owl;
export class SupplierLedgerReport extends Component {
    setup() {
        const data = this.props.action.params
        console.log(data)

        this.state = useState({ columns: [], values: [], header_values: []})
        this.rpc = useService("rpc");
        onWillStart(async () => {

            if (data.column || data.supplier_id1 || data.supplier_id2 || data.suppliers|| data.from_date || data.to_date) {
                console.log("this is true");

                localStorage.setItem('supplier_data', JSON.stringify(data.column))
                localStorage.setItem('suppliers', JSON.stringify(data.suppliers))
                localStorage.setItem('supplier_id2', JSON.stringify(data.supplier_id2))
                localStorage.setItem('supplier_id1', JSON.stringify(data.supplier_id1))
                localStorage.setItem('from_date', JSON.stringify(data.from_date))
                localStorage.setItem('to_date', JSON.stringify(data.to_date))
                this.state.columns = data.column
                console.log("colums", this.state.columns)
            } else {
                this.object = localStorage.getItem('supplier_data')
                this.supplier_id1 = localStorage.getItem('supplier_id1')
                this.supplier_id2 = localStorage.getItem('supplier_id2')
                this.from_date = localStorage.getItem('from_date')
                this.to_date = localStorage.getItem('to_date')
                // this.object_many2many = localStorage.getItem('suppliers')

                this.state.columns = JSON.parse(this.object)
                // this.state.many2many = JSON.parse(this.object_many2many)
                this.state.header_values = [this.supplier_id1, this.supplier_id2, this.from_date, this.to_date]
                // console.log("else colums", this.state.columns)
                // console.log("else colums", this.state.many2many)
            }
            this.state.values = await this.loadData()
            // const data = await this.loadData()
            console.log("values", this.state.values)

            if ((data.supplier_id1 && data.supplier_id2) || (data.from_date && data.to_date)) {
                console.log("header content", this.state.header_values);

            }
        });
    }

    heightOfPage() {
        let navbar = document.getElementsByClassName('o_navbar')
        navbar = navbar[0]
        const navbarHeight = navbar.scrollHeight
        const windowHeight = window.innerHeight
        return windowHeight - navbarHeight - 136
    }
    async loadData() {
        const data = this.props.action.params
        if ((data.supplier_id1 && data.supplier_id2) || (data.from_date && data.to_date || data.suppliers)) {
            const res = await this.rpc("/supplier/report/",
                {
                    method: 'call',
                    args: [{'sup1':data.supplier_id1, 'sup2':data.supplier_id2, 'date1':data.from_date, 'date2':data.to_date, 'many2many': data.suppliers}]
                }
            );
            return res
        }
        else {
            const res = await this.rpc("/supplier/report/",{
                method: 'call',
                args: [{'sup1':localStorage.getItem('supplier_id1'), 'sup2':localStorage.getItem('supplier_id2'), 'date1':localStorage.getItem('from_date'), 'date2':localStorage.getItem('to_date'), 'many2many': data.suppliers}]
            });
            
            return res
        }

    }

    generateUUID() {
        const array = new Uint8Array(16);
        crypto.getRandomValues(array);
    
        // Set the version number (4) and the variant bits
        array[6] = (array[6] & 0x0f) | 0x40;
        array[8] = (array[8] & 0x3f) | 0x80;
    
        return [...array].map((b, i) => {
            const hex = b.toString(16).padStart(2, "0");
            return (i === 4 || i === 6 || i === 8 || i === 10) ? `-${hex}` : hex;
        }).join('');
    }
    async _printPDF() {
        const data = this.props.action.params;
        let response;
    
        // Send data to the backend to generate the PDF
        if ((data.supplier_id1 && data.supplier_id2) || (data.from_date && data.to_date)) {
            response = await this.rpc("/supplier/report/pdf", {
                filter_response: [data.supplier_id1, data.supplier_id2, data.from_date, data.to_date],
                columns: this.state.columns,
                values: this.state.values,
            });
        } else {
            response = await this.rpc("/supplier/report/pdf", {
                filter_response: [localStorage.getItem('supplier_id1'), localStorage.getItem('supplier_id2'), localStorage.getItem('from_date'), localStorage.getItem('to_date')],
                columns: this.state.columns,
                values: this.state.values,
            });
        }
    
        // Create a link element to download the PDF
        const link = document.createElement('a');
        link.href = `data:application/pdf;base64,${response.pdf_base64}`;
        link.download = 'supplier_ledger_report.pdf';
        console.log(link)
        link.click();  
    }

    async _printXLSX() {
        const data = this.props.action.params;
        let response;
    
        try {
            // Send data to the backend to generate the XLSX report
            if ((data.supplier_id1 && data.supplier_id2) || (data.from_date && data.to_date)) {
                response = await this.rpc("/supplier/report/xlsx", {
                    filter_response: [data.supplier_id1, data.supplier_id2, data.from_date, data.to_date],
                    columns: this.state.columns,
                    values: this.state.values,
                });
            } else {
                response = await this.rpc("/supplier/report/xlsx", {
                    filter_response: [localStorage.getItem('supplier_id1'), localStorage.getItem('supplier_id2'), localStorage.getItem('from_date'), localStorage.getItem('to_date')],
                    columns: this.state.columns,
                    values: this.state.values,
                });
                
            }
    
            // Create a link element to download the XLSX file
            const link = document.createElement('a');
            link.href = `data:application/xlsx;base64,${response.xlsx_base64}`;
    
            // Optionally, dynamically name the file based on filters or dates
            link.download = `supplier_ledger_report_${data.from_date || 'start'}_${data.to_date || 'end'}.xlsx`;
            // Trigger the download
            link.click();

        } catch (error) {
            console.error("Error generating the report:", error);
            // Optionally show a user-friendly message
        }
    }
    
    
}

SupplierLedgerReport.template = 'aged_receivable_report.owl_report';
registry.category('actions').add('aged_receivable_report.action_supplier_ledger_report', SupplierLedgerReport);
