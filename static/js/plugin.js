
$(document).ready(function(){
// ==customer======================================================================================
    $('.customer-form').click(function(){
        $.ajax({
            url: '/CreateCustomer',
            type: 'get',
            dataType:'json',
            beforeSend: function(){
                $('#modal-customer').modal('show');
            },
            success: function(data){
                $('#modal-customer .modal-content').html(data.html_form);
            }
        });
    });
    $('#modal-customer').on('submit','.create-form', function(){
        var form = $(this);
        $.ajax({
            url: form.attr('data-url'),
            data: form.serialize(),
            type: form.attr('method'),
            dataType: 'json',
            success: function(data){
                if(data.form_is_valid){
                    $('#customer-list .this-class').html(data.customer_list);
                    $('#modal-customer').modal('hide');
                } else {
                    $('#modal-customer .modal-content').html(data.html_form)
                }
            }
        })
        return false;
    })
});
