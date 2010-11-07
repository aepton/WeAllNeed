/* Author: Joey Baker

*/
function init () {
	if (window.location.hash == ""){
		window.location.hash='#intro';
	}
	else if ($(document.location.hash.replace("sel_","")).length) {
		s=$(document.location.hash.replace("sel_","")).addClass('selected').attr("href").replace("javascript:","");
		eval(s);
	}
}
//onload, we'll call the init function.
window.onload = init;
var po = org.polymaps;

$(document).ready(function() {
	
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
	
	getLatestQuotes();
	
	var base_json_url = "media/js/static_json/";
	var svg = n$("#map").add("svg:svg");
	var map = po.map()
	    .container($n(svg))
		.add(po.interact()).add(po.compass().pan("none"))
		.add(po.hash());
	
	map.add(po.geoJson()
		.url(base_json_url + "surrounding_area.json")
		.id("surrounding")
		.tile(false));

	map.add(po.geoJson()
		.url(base_json_url + "tenderloin.json")
		.id("tenderloin")
		.tile(false));

	map.add(po.geoJson()
		.url(base_json_url + "street_names.json")
		.id("streets_loc")
		.tile(false)
		.on("load", load));

	
});

function getLatestQuotes() {
	$.ajax({
		url: '/quotes',
		//dataType:'jsonp',
		success: function(data) {
			console.log(data);
		},
		error: function() {
			console.log("error");
		}
	});
}


function load(e) {
	var fontSize = .7 * Math.pow(2, e.tile.zoom - 12);
	console.info(fontSize);
	for (var i = 0; i < e.features.length; i++) {
		var c = n$(e.features[i].element),
			g = c.parent().add("svg:g", c);
		
		g.attr("transform", "translate(" + c.attr("cx") + "," + c.attr("cy") + ")")
			.add("svg:text")
			.attr("font-size", fontSize)
			.attr("class", "street-names")
			.attr("transform", "rotate(" + e.features[i].data.properties.rotate + ")");

		g.element.firstChild.textContent = e.features[i].data.properties.street_name;

	}
}


