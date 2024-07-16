frappe.ui.form.on("Vehicle Request", {
  refresh(frm) {
  },

  before_workflow_action: async (frm) => {

    const workflowState = frm.doc.workflow_state;

    if (
      workflowState === "Pending Administration Approval" ||
      workflowState === "Pending DAF Approval" ||
      workflowState === "Approved"
    ) {

      let dialog = new frappe.ui.Dialog({
        title: __('Enter your comment'),
        fields: [
          {
            label: 'Comment',
            fieldname: 'comment',
            fieldtype: 'Small Text',
            reqd: true,
          }
        ],
        primary_action: function () {
          const comment = dialog.get_value('comment');

          if (!comment) {
            frappe.msgprint(__('Comment is mandatory. Please enter a comment.'));
            return;
          }

          frappe.call({
            method: "frappe.desk.form.utils.add_comment",
            args: {
              reference_doctype: frm.doctype,
              reference_name: frm.docname,
              content: comment,
              comment_email: frappe.session.user,
              comment_by: frappe.session.user_fullname
            },
            callback: function (r) {
              if (!r.exc) {
                dialog.hide();
              } else {
                console.log("Error adding comment:", r.exc);
              }
            }
          });
        },
        primary_action_label: __('Confirm approval'),
      });

      dialog.$wrapper.find('.modal-header .close').prop('disabled', true);

      dialog.fields_dict.comment.$input.on('input', function () {
        const comment = dialog.get_value('comment');
        dialog.$wrapper.find('.modal-header .close').prop('disabled', !comment);
      });

      dialog.$wrapper.find('.modal-header .close').remove();

      dialog.$wrapper.find('.modal-header').append(
        '<button class="btn btn-default btn-xs pull-right close-dialog" disabled>Close</button>'
      );

      dialog.$wrapper.find('.modal-header .close-dialog').on('click', function () {
        dialog.hide();
      });
      dialog.show();
    } else {
      console.log("Workflow state did not match any condition");
    }
  },
});
