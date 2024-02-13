(() => {
  // ../stock/stock/public/js/website_utils.js
  if (!window.stock)
    window.stock = {};
  stock.subscribe_to_newsletter = function(opts, btn) {
    return frappe.call({
      type: "POST",
      method: "frappe.email.doctype.newsletter.newsletter.subscribe",
      btn,
      args: { "email": opts.email },
      callback: opts.callback
    });
  };
})();
//# sourceMappingURL=stock-web.bundle.45KKIKJJ.js.map
