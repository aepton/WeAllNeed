/* Author: Joey Baker

*/
function init () {
	if (window.location.hash == ""){
		window.location.hash='#intro';
	}
	else if (window.location.hash == "#filter_open") {
		$('#tagcloud').slideToggle("fast", function () {$(this).toggleClass('selected')});
	}
	else if (window.location.hash == "#about_open") {
		$('#about_text').slideToggle("fast", function () {$(this).toggleClass('selected')});
	}
	else if ($(document.location.hash.replace("sel_","")).length) {
		s=$(window.location.hash.replace("sel_","")).addClass('selected').attr("href").replace("javascript:","");
		eval(s);
	}
}
//onload, we'll call the init function.
window.onload = init;
var po = org.polymaps;


function toggleNeed() {
	if ($("p.need:visible").length) {
		$("p.need").hide();
		$("#need_btn").attr('style','opacity:0.4');
	}
	else {
		$("p.need").show();
		$("#need_btn").removeAttr('style');
	}
}

function toggleThink() {
	if ($("p.think:visible").length) {
		$("p.think").hide();
		$("#think_btn").attr('style','opacity:0.4');
	}
	else {
		$("p.think").show();
		$("#think_btn").removeAttr('style');
	}
}

var map;
var svg;
var base_json_url;

$(document).ready(function() {
	
	//when a quote is called for, we're going to make it the selected quote.
	function rm_false_hash () {
		$("article.selected").removeClass("selected");
		$(window.location.hash.replace("sel_","")).toggleClass("selected");
	}
	window.onhashchange = rm_false_hash;
	
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
	
	$('nav #about').click(function() {
		$('#about_text').slideToggle("fast", function () {$(this).toggleClass('selected')});
	});
	
	getLatestQuotes();
	
	base_json_url = "media/js/static_json/";
	svg = n$("#map").add("svg:svg");
	map = po.map()
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
			var geo_features = [];
			for (i=0; i<data.length; i++) {
				quote = data[i];
				
				article = $("<article id='quote"+quote.id+"'></article>");
				
				article.append($("<p class='person'></p>"));
				if (quote.person_name) {
					article.find(".person").append("<span class='name'>"+quote.person_name+"</span>");
				}
				if (quote.person_age) {
					article.find('.person').append(", <span class='age'>"+quote.person_age+"</span>");
				}
				
				article.append($("<p class='think'>"+quote.quote_text + "</p>"));
				article.append($("<p class='need'>"+quote.quote_text_alt + "</p>"));
				
				article.append($("<div class='infobox'><img src='"+quote.photo_url+"' alt='"+quote.person_name+"'>"));
				
				for (j=0; j < quote.tags.length; j++) {
					article.addClass(quote.tags[j]);
					article.find('p.need, p.think').each(function() {
						$(this).html($(this).html().replace(quote.tags[j], "<span class='highlight'>"+quote.tags[j]+"</span>"));
					})
				}
				
				if (quote.audio_embed) {
					article.find('.infobox').append(quote.audio_embed);
					article.find('object').hide();
				}
				
				$('.infobox').click(function(){
					$(this).toggle(.001, 'normal');
				});
				
				article.click(function(){
					$("article").removeClass('selected');
					$("article object").hide();
					$(this).addClass('selected');
					document.location.hash="sel_"+$(this).attr("id");
					$(this).find('object').show();
					//return false;
				});
				
				article.append($("<hr />"));
				
				$("#quotelist").append(article);
				
				geo_features.push({geometry: {coordinates: [quote.long, quote.lat], type: "Point"}, properties:{"marker_id":quote.id}});
			}
			console.info(geo_features);
			map.add(po.geoJson()
			    .features(geo_features)
				.on("load", loadPoints));
			
			
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
	id_short = "quote" + String(id.target.getAttribute('marker_id'));
	window.location.hash = id_short;
}

