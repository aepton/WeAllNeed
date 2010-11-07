/* Author: Joey Baker

*/
function init () {
	if (window.location.hash == ""){
		window.location.hash='#intro';
	}
	else {
		s=$(document.location.hash.replace("sel_","")).addClass('selected').attr("href").replace("javascript:","");
		eval(s);
	}
}
//onload, we'll call the init function.
window.onload = init;

$(document).ready(function() {
	$("#quotelist").jScrollPane();
    //fitlering for the tagcloud
	$('#tagcloud li a').click(function() {
		var filterVal = $(this).text().toLowerCase().replace(' ','-');
		window.location.hash = filterVal;
  
        if(filterVal == 'all') {  
            $('article.hidden').slideDown('normal').removeClass('hidden');  
        } else {  
            $('article').each(function() {  
                if(!$(this).hasClass(filterVal)) {  
                    $(this).fadeOut('fast').addClass('hidden');  
                } else {  
                    $(this).slideDown('normal').removeClass('hidden');
 					//TODO: this if statement should set the hash to the id of the quote if there is only one quote of that type
					if ($(filterVal).length == 1) {
						window.location.hash = this.attr('id');
					}
                }  
            });  
        }
        return false;  
    });

	$('nav #filters').click(function() {
		$('#tagcloud').slideToggle("fast", function () {$(this).toggleClass('selected')});
	});
	
	//when we click on an article (a quote), we'll change the hash of the window to it's id
	$('article').click(function(){
		$("article").removeClass('selected');
		$(this).addClass('selected');
		document.location.hash="sel_"+$(this).attr("id");
		//return false;
	});
});