/* Author: Joey Baker

*/
function init () {
	window.location.hash='#intro';
}
//onload, we'll call the init function.
window.onload = init;
//when we click on an article (a quote), we'll change the hash of the window to it's id
$('article').click(function(){
	var id = $(this).attr('id');
	window.location.hash=id;
});
