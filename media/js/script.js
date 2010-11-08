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


function toggleNeed() {
	if ($("article.need:visible").length) {
		$("article.need").hide();
		$("#need_btn").attr('style','opacity:0.4');
	}
	else {
		$("article.need").show();
		$("#need_btn").removeAttr('style');
	}
}

function toggleThink() {
	if ($("article.think:visible").length) {
		$("article.think").hide();
		$("#think_btn").attr('style','opacity:0.4');
	}
	else {
		$("article.think").show();
		$("#think_btn").removeAttr('style');
	}
}

$(document).ready(function() {
	
    //fitlering for the tagcloud
	$('#tagcloud li a, #qNav li a').click(function() {
		//var filterVal = $(this).text().toLowerCase().replace(' ','-');
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
				console.log(quote.tags);
				article = $("<article id='quote"+quote.id+"'></article>");
				if (quote.use_first_question) {
					article.addClass("think");
				}
				else {
					article.addClass("need");
				}
				
				for (j=0; j < quote.tags.length; j++) {
					article.addClass(quote.tags[j]);
				}
				article.append($("<p class='person'><span class='name'>"+quote.person_name+"</span>, <span class='age'>"+quote.person_age+"</span></p>"))
				article.append($("<p class='think'>"+quote.quote_text+"</p>"));
				article.append($("<p class='need'>"+quote.quote_text_alt+"</p>"));
				
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
				$("#quotelist").append($("<hr />"));
				//console.log(article);
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

function loadPoints(e) {
	for (var i = 0; i < e.features.length; i++) {
		var c = n$(e.features[i].element),
			g = c.parent().add("svg:g", c);

		g.attr("transform", "translate(" + c.attr("cx") + "," + c.attr("cy") + ")");

		c.attr("opacity",0);
		g.add("svg:image")
			.attr("width", "32").attr("height", "45")
			.attr("xlink:href", "media/images/pin.png")
			.attr("style","fill:#ff0000;")
			.attr("marker_id",e.features[i].data.properties.marker_id);
		// g.attr("onclick",ddd);
		g.element.addEventListener('click', pinClicked,false);
		// c.)
	}
}
function pinClicked(id) {
	id_short = String(id.target.getAttribute('marker_id'));
	window.location.hash = id_short;
}

