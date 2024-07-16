(()=>{window.stock||(window.stock={});stock.subscribe_to_newsletter=function(e,t){return frappe.call({type:"POST",method:"frappe.email.doctype.newsletter.newsletter.subscribe",btn:t,args:{email:e.email},callback:e.callback})};})();
//# sourceMappingURL=stock-web.bundle.J6OB2FBC.js.map
