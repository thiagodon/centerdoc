$('#bt_backup').on('click', function(e){
    if ($(this).attr('href')!='/backup/')
        return true;
    e.preventDefault();
	  $("#modal-progress").modal("show");	
    $.get('/backup/', function(response){
       if (response.is_valid){
           $('.alert-success').fadeIn('fast');
           $('#im_result').html('<img src="/media/image/ok.png">');
           setTimeout(function() { 
                $('.alert').fadeOut('fast');
                $("#modal-progress").modal("hide");
                $('#bt_backup').attr("href", response.url)
                $('#bt_backup').html("Download Backup")
                $('#bt_backup').removeClass("btn-secondary").addClass("btn-primary");

                // var div = '<a href="'+response.url+'" download>Download Backup</a>';
                // $('#download').html(div);
            }, 3000);
       }else{
            $('.alert-danger').fadeIn('fast');
            $('#im_result').html('<img src="/media/image/error.png">');
            setTimeout(function() { 
                $('.alert').fadeOut('fast');
                $("#modal-progress").modal("hide");
                window.location.href = response.url;
            }, 3000);
       }
    });
    return false;
});

// $('#bt_backup').on('click', function(e){
//     e.preventDefault();
//       $("#modal-progress").modal("show");   
//     $.get('/backup/', function(response){
//        if (response.is_valid){
//             $('.alert-danger').fadeIn('fast');
//             $('#im_result').html('<img src="/media/image/error.png">');
//             setTimeout(function() { 
//                 $('.alert').fadeOut('fast');
//                 $("#modal-progress").modal("hide");
//                 window.location.href = response.url;
//             }, 3000);
//        }else{
//            $('.alert-success').fadeIn('fast');
//            $('#im_result').html('<img src="/media/image/ok.png">');
//            setTimeout(function() { 
//                 $('.alert').fadeOut('fast');
//                 $("#modal-progress").modal("hide");
//                 var blob=new Blob([response]);
//                 var link=document.createElement('a');
//                 link.href=window.URL.createObjectURL(blob);
//                 link.download="myFileName.zip";
//                 link.click();
//             }, 3000);
//        }
//     });
//     return false;
// });