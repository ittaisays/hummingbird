$(document).ready(function() {

    $('.delete-user').hide();

    $('.delete_device').click(function() {
        var device = $(this).attr('data-deviceid');
        var user = $(this).attr('data-userprofile');
        $.get('/hummingbird/delete_device/', {device_id: device, user_id: user}, function(data){
            $('#device-div').html(data)
        });
    });

    $(".user-div").hover(function() {
            $(this).find('.delete-user').show();
    },
    function() {
            $(this).find('.delete-user').hide();
    });

    $('.delete-user').click(function() {
        var user;
        user = $(this).attr("data-userprofile");
        $.get('/hummingbird/delete_user/', {user_id: user}, function(data){
        });
        $(this).parent().parent().hide();
    });


});
