$(document).ready(function () {

    var league = $('#league').val();
    var teams = $('#team-data').data();

    $('#league').on('change', function() {
      league = this.value

      $.each(teams, function(key,value) {
            $("#team").empty();
            $.each(value, function(index,v) {
                //console.log(v);
                if (v.country_code == league) {
                    console.log(v.id);
                    $("#team").append("<option value=" + v.id + ">" + v.full_name + "</option>");
                }
            });
      });
    });

});