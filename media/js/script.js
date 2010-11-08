/* Author: Joey Baker

*/
function init () {
	if (window.location.hash == ""){
		window.location.hash='#intro';
	}
	else if (window.location.hash == "#filter_open") {
		$('#tagcloud').slideToggle("fast", function () {$(this).toggleClass('selected')});
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
		$('#tagcloud li a').removeClass("current");
		$(this).addClass("current");
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
	
	getLatestQuotes();
	
	var base_json_url = "media/js/static_json/";
	var svg = n$("#map").add("svg:svg");
	var map = po.map()
	    .container($n(svg))
		.center({lat:37.7818, lon:-122.4154})
		.zoom(16)
		.zoomRange([15,18])
		.add(po.interact()).add(po.compass().pan("none"));
		// map.add(po.hash());
	
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
		url: 'http://tenderneeds.appspot.com/quotes',
		dataType:'jsonp',
		success: function(data) {
			console.log(data);
			for (i=0; i<data.length; i++) {
				quote = data[i];
				article = $("<article id='quote"+quote.id+"'></article>");
				if (quote.use_first_question) {
					article.addClass("think");
				}
				else {
					article.addClass("need");
				}
				$(quote.tags).each(function(tag) {
					article.addClass(tag);
				});
				article.append(quote.quote_text);
				
				article.append($("<div class='infobox'><img src='"+quote.photo_url+"' alt='"+quote.person_name+"'>"));
				
				article.click(function(){
					$("article").removeClass('selected');
					$(this).addClass('selected');
					document.location.hash="sel_"+$(this).attr("id");
					//return false;
				});
				
				$('.infobox').click(function(){
					$(this).toggle(.001, 'normal');
				});
				
				$("#quotelist").append(article);
				console.log(article);
			}
			
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


