$('#id_arquivo').attr("multiple","true");
$('#form_pagina').on('submit', function(e){
	e.preventDefault();
	var myForm = document.getElementById('form_pagina');
	formData = new FormData(myForm);
    if ($('#pagina_id').val()){
    $.get('/pagina/paginacao/', {'id': $('#pagina_id').val(), 'livro': $('#livro_id').val(), 'pagina': $('#id_pagina').val(), 'lado': $('#id_lado').val()}, function(data){
        if (!data.is_valid){
            alert(data.msg);
        }
    }).done(function (data){
        if (data.is_valid){
          $("#modal-progress").modal("show");   
          $.ajax({
            url         : this.action,
            data        : formData,
            cache       : false,
            contentType : false,
            processData : false,
            type        : 'POST',
            error: function() {
                $("#modal-progress").modal("hide");
            },
            success : function(data){
                if (data.is_valid){
                   $('.alert-success').fadeIn('fast');
                   $('#im_result').html('<img src="/media/image/ok.png">');
                   setTimeout(function() { 
                    $('.alert').fadeOut('fast');
                    $("#modal-progress").modal("hide");
                    window.location.href = data.url;
                    }, 3000);
                }else{
                    $('.alert-danger').fadeIn('fast');
                    $('#im_result').html('<img src="/media/image/error.png">');
                    setTimeout(function() { 
                        $('.alert').fadeOut('fast');
                        $("#modal-progress").modal("hide");
                        window.location.href = data.url;
                    }, 3000);
                }
            },  
            }); 
        }
    });
    }else{
        $("#modal-progress").modal("show");   
      $.ajax({
        url         : this.action,
        data        : formData,
        cache       : false,
        contentType : false,
        processData : false,
        type        : 'POST',
        error: function() {
            $("#modal-progress").modal("hide");
        },
        success : function(data){
            if (data.is_valid){
               $('.alert-success').fadeIn('fast');
               $('#im_result').html('<img src="/media/image/ok.png">');
               setTimeout(function() { 
                $('.alert').fadeOut('fast');
                $("#modal-progress").modal("hide");
                window.location.href = data.url;
                }, 3000);
            }else{
                $('.alert-danger').fadeIn('fast');
                $('#im_result').html('<img src="/media/image/error.png">');
                setTimeout(function() { 
                    $('.alert').fadeOut('fast');
                    $("#modal-progress").modal("hide");
                    window.location.href = data.url;
                }, 3000);
            }
        },  
        }); 
    }
});
$('.confirm-remove').on('click', function(){
    return confirm('Deseja realmente remover?');
});
$('.check_pagina').on('change',function(){
    $.get('/pagina/paginacao/', {'pagina': $('#id_pagina').val(), 'livro': $('#livro_id').val(), 'lado': $('#id_lado').val(), 'id': $('#pagina_id').val()}, function(data){
        if (!data.is_valid){
            return alert(data.msg);
        }
    }); 
});
$('#bt_pro').on('click', function(e){
    e.preventDefault();
    parse = $(this).attr('alt').split('||');
    id = parse[0];
    livro = parse[1];
    var acao = "proi";
    if (livro!='None')
        acao = "prop";
    $.get('/pagina/editp/', {'acao': acao, 'id': id}, function(data){
        window.location.href = data.url;
    });

});
$('#bt_ant').on('click', function(e){
    e.preventDefault();
    parse = $(this).attr('alt').split('||');
    id = parse[0];
    livro = parse[1];
    var acao = "anti";
    if (livro!='None')
        acao = "antp";
    $.get('/pagina/editp/', {'acao': acao, 'id': id}, function(data){
        window.location.href = data.url;
    });
});
