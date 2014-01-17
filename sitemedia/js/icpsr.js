$(function(){
	$("select[name='per_page'], select[name='sort']").selectpicker({style: 'btn-default', menuStyle: 'dropdown-inverse'});
});	

$(document).ready(function(){
	var q = window.location.search,
	params = {
		load_results: 'load=',
		search_term: 'term='
	};

	q = q.substring(1,q.length);

	var load = q.substring(q.indexOf(params.load_results)+params.load_results.length, q.indexOf(params.search_term)),
	term = q.substring(q.indexOf(params.search_term)+params.search_term.length, q.length);

	if(load.replace('&','')=='true'){
		//loadResults();
	}
	if(q.indexOf(params.search_term)>0){
		$('#id_keyword').val(unescape(term));
	}
	var card = '.cards > div';
	$(document).on('click',card, function(){
		$article=$(this).not('.clone');

		$copy = $article.clone().addClass('clone');

		// var position =$(this).offset(),
		// top = position.top,
		// left = position.left;

		// $copy.css({
		// 	'top'	: top,
		// 	'left'	: left
		// });

		// var centerTop = Math.max(0, (($(window).height() - $copy.outerHeight()) / 2) + $(window).scrollTop())/2 + "px",
		// centerLeft = Math.max(0, (($(window).width() - $copy.outerWidth()) / 2) + $(window).scrollLeft())/2 + "px";


		$copy.insertAfter($article).find('article')
		.css({'left':'0px','max-height':'100%'});

		$copy
		.removeClass('col-sm-6')
		.addClass('col-sm-5');

		$('.cards > div').not('.clone').animate({'opacity':'0.2'});

		$copy.on('click', function(){
			close(this);	
		});

		function close(elem){
			$(elem).animate({'margin-left':'0%'},500);
			$(elem).remove();
			$(card).not('.clone').animate({'opacity':'1'});
		}

	});


	$( "input" )
  	.keyup(function() {
    var value = $( this ).val();
    $(this).attr('value',value);
	});

	$('form').on('keyup',function(e){
		e.preventDefault();
		var code = e.keyCode || e.which,
		$input = $(document.activeElement);

		if(code == 13){
			$(this).submit();
		}
	}).on('submit',function(e){
		search.get();
	});

	$('#submit').on('click', function(){
		search.get();
		//moveElementsForResults();
	});
});

var search = {

	get: getResults,
	load: loadResults
}


function getResults(){
	var $form = $('form'),
	protocol = window.location.protocol,
	host = window.location.host,
	path = window.location.pathname;
	query = getQueryStringFromForm($form);

	if(path.indexOf('serach')<0){
		path='/search/';
	}
	request = protocol+'//'+host+path+'?'+query;
	log(request);
	//loadResults(request, query);
}

function loadResults(request_url){
	$.get(request_url,function(data){
		$data = $('<div/>').attr('class','cards');
		$data.append(data);
		$results = $('.results');
		$results_listing = $('.results .result-listing');

		$results_listing.css({'opacity':'0'}).html($data);
		$('.results')
		.css({'opacity':'0'})
		.removeClass('hidden')
		.animate({'opacity':'1'},500,function(){
			$results_listing.animate({'opacity':'1'},500);
		});
		if(".home"){
			moveElementsForResults(request_url);
		}
		else{
			changeLocation(request_url);
		}
	});
}

function moveElementsForResults(url){
	var $header = $('#search h1'),
	$recent = $('.recent'),
	$filter = $('.filter'),
	$footer =$('.footer');

	if(!$filter.hasClass('show')){
		$filter.slideUp(0);
	}
	$footer.hide();
	$('.home').css({'background-color':'#F7F7F7'});
	$filter.slideDown(500)
	$filter.fadeIn(500);
	$recent.fadeOut(500);
	$header.slideUp(500, function(){
		changeLocation(url);
	});
}
function changeLocation(url){
	window.location=url;
}


function getQueryStringFromForm(form){
	var $form = $(form);
	if($form.length<0){
		return '';
	}
	var str ='', count=0;
	$form.find('input').each(function(){
		var $this = $(this);
		if($this.parent('.sr-only').length<=0){
			if(count>0){
				str+='&amp;';
			}
			str+=$this.attr('name')+'='+escape($this.attr('value'));
			count++;
		}
	});
	$form.find('select').each(function(){
		var $this = $(this);
		if($this.parent('.sr-only').length<=0){
			if(count>0){
				str+='&amp;';
			}
			str+=$this.attr('name')+'='+$this.children('option:selected').html().trim();
			count++;
		}
	});
	return str;
}

//debug 
function log(){
	console.log.apply(console, arguments);
}


function replaceQueryString(url,param,value) {
	var re = new RegExp("([?|&])" + param + "=.*?(&|$)","i");
	if (url.match(re))
		return url.replace(re,'$1' + param + "=" + value + '$2');
	else
		return url + '&' + param + "=" + value;
}
