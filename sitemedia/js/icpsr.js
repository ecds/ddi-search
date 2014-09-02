$(function(){
	$("select[name='per_page'], select[name='sort']").selectpicker({style: 'btn-default', menuStyle: 'dropdown-inverse'});
	$('.no-js').removeClass('no-js');
});

$(document).ready(function(){

	var $navbarAffix = $('.navbar-affix');

	if($navbarAffix.length>0){
		function anchorTags(){

			var $navbarAffix = $('.navbar-affix'),
			$navbarFixedTop = $('.navbar-fixed-top')
			$adjSection = $('.navbar-affix+section'),
			offsetTop = $navbarAffix.offset().top-$navbarAffix.height();
			$navbarAffix.affix({
				offset: {
					top: offsetTop
				}
			});
			$adjSection.on('affixed.bs.affix',function(){
				$(this).css({'padding-top':$navbarAffix.height()});
			});
			$('body').scrollspy({ target: '.navbar-affix', offset: 2*$navbarAffix.height()+$navbarFixedTop.height()})
		}
		anchorTags();
		$(window).resize(function(){
			anchorTags();
		})

	}

	var $animateScrollLinks = $(".nav.animate li a");

	if($animateScrollLinks.length>0){
		$animateScrollLinks.on('click',function(evt){
			evt.preventDefault();

			var spacerH = parseInt($(".navbar-fixed-top").height()+ $('.navbar-affix').height()),
			full_url = $(this).attr('href'),
			parts = full_url.split("#"),
			trgt = parts[1],
			target_offset = $("#"+trgt).offset(),
			target_top = target_offset.top-spacerH;

			$(window).resize(function(){
				spacerH = parseInt($(".navbar-fixed-top").height()+ $('.navbar-affix').height());
			})

			$('html, body').animate({scrollTop:target_top+"px"}, 500);
		})
	}

	$('.location-marker .glyphicon').tooltip();

	var q = window.location.search,
	params = {
		load_results: 'load=',
		search_term: 'term=',
		per_page: 'per_page=',
		sort: 'sort=',
		adv:  'adv=',
		topic: 'topic='
	};

	q = q.substring(1,q.length);

	var load = q.substring(q.indexOf(params.load_results)+params.load_results.length, q.indexOf(params.search_term)),
	term = getParam(q,params.search_term),
	per_page = getParam(q,params.per_page),
	sort = getParam(q,params.sort);

	function getParam(q,term){
		var str = q.substring(q.indexOf(term)+term.length, q.length);
		if(str.indexOf('&')>0)
			str = str.substring(0,str.indexOf('&'));
		return str;
	}
	if(window.location.search==''&& $(".container#search").length>0){
		$("#no-results-found").remove();
	}
	if(load.replace('&','')=='true'){
		//loadResults();
	}

	if(q.indexOf(params.search_term)>0){
		$('#id_keyword').val(unescape(term));
	}

	if(q.indexOf(params.adv)>0){
		$('.adv.group').slideToggle(0);
		$('.adv.switch').addClass('active');
	}

	var $perPage = $("#id_per_page + .btn-group .dropdown-toggle .filter-option"),
	currentVisiblePageNumber = $.trim($perPage.html());

	var $sort = $("#id_sort + .btn-group .dropdown-toggle .filter-option"),
	currentVisibleSort = $.trim($sort.html());

	if(currentVisiblePageNumber !==per_page){
		getCurrentDropdownSetting('per_page', per_page);
	}
	var firstSortOption = $("#id_sort+div .dropdown-menu li[rel='0']").text();
	if(currentVisibleSort !==sort && sort!=firstSortOption){
		getCurrentDropdownSetting('sort', sort);
	}

	function getCurrentDropdownSetting(id, value){
		var val = unescape(value)
		$("#id_"+id+" + .btn-group li span").each(function(){
			var num = $(this).html();
			if(num.length>0){
				num = $.trim(num);
			}
			if(num == val){
				$(this).parents('.dropdown-menu').siblings('button').find('.filter-option').html(num);
				$(this).parents('li').addClass('selected').siblings().removeClass('selected');
			}
		});
	}

	var $form = $('form');

	$( "input" )
	.keyup(function() {
		var value = $( this ).val();
		$(this).attr('value',value);
	});

	$('#search .option select').bind('change',function(){
		search.get();
	});

	$('.browse .option select').bind('change',function(){
		var topic = getParam(q,params.topic),
		search = '?topic='+topic+'&amp;'+ getQueryStringFromForm('.browse'),
		url = window.location.origin + window.location.pathname + search;

		window.location = url;
	});

	$form.on('keyup',function(e){
		e.preventDefault();
		var code = e.keyCode || e.which,
		$input = $(document.activeElement);

		if(code == 13){
			$(this).submit();
		}
	});
	$(".home form").on('submit',function(e){
		e.preventDefault();
		search.get(true);
	});
	$('#submit, #submit2').on('click', function(e){
		e.preventDefault();
		search.get();
	});

	$('.home #submit, .home #submit2').on('click', function(e){
		e.preventDefault();
		search.get(true);
	});

	var $scrollbar = $('.scrollbar');
	if($scrollbar.length>0){

		$scrollbar.scroller({
			horizontal: true
		}).animate({'opacity':1},1000,function(){
			$scrollbar.scroller("scroll", '.active');
		});
		$scrollbar.scroller("scroll", '.active');

	}
	$("#date-range input").datepicker( {
		format: "yyyy",
		viewMode: "years",
		minViewMode: "years"
	});

});//end doc.ready

var search = {
	get: getResults,
	load: loadResults
}


function getResults(move){
	var $form = $('form'),
	protocol = window.location.protocol,
	host = window.location.host,
	path = window.location.pathname;
	query = getQueryStringFromForm($form),
	$keywordInput = $('.input-group input#id_keyword'),
	keyword=$keywordInput.attr('value');

	if(path.indexOf('search')<0){
		path='/search/';
	}
	request = protocol+'//'+host+path+'?'+query;

	// if(keyword!='' && keyword!==undefined){
		$('.dropdown-menu, .dropdown-arrow').hide();

		if(move){
			moveElementsForResults(request);
		}
		else{
			loadResults(request, query);
		}
	// }
	// //keyword input is empty
	// else{
	// 	$keywordInput.parent().addClass('has-error');
	// 	$keywordInput.parent().shake();
	// }
}

function loadResults(request_url){

	var $loader = $('.loader'),
	$results = $('.results');

	$('.loader').slideDown(500);
	$('.loader').animate({'opacity':'1'},1000);

	$('.results').animate({'opacity':'0'},300)

	$.get(request_url,function(data){
		changeLocation(request_url);
	});
}

function moveElementsForResults(url){
	var $header = $('#search h1'),
	$recent = $('.recent'),
	$filter = $('.page-options'),
	$footer =$('.footer');

	if($filter.not(":visible").length>0){
		$filter.slideUp(0);
	}
	$('.slideup').slideUp(500);
	$footer.hide();

	$('.loader').slideDown(500);

	$('.home').css({'background-color':'#F7F7F7'});
	if($filter.not(":visible").length>0){
		$filter.slideDown(500)
		$filter.fadeIn(500);
	}
	$recent.fadeOut(500);
	$header.slideUp(500, function(){
		$(this).animate({'opacity':'0'},1000,function(){
			changeLocation(url);
		})

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
			if($this.attr('name')!=undefined){
				if(count>0){
					str+='&amp;';
				}
				var value = $this.attr('value') || $this.val() || '';

				str+=$this.attr('name')+'='+escape(value);
			}
			count++;
		}
	});
	$form.find('select').each(function(){
		var $this = $(this);
		if($this.parent('.sr-only').length<=0){
			if(count>0){
				str+='&amp;';
			}
			str+=$this.attr('name')+'='+$.trim($this.children('option:selected').html());
			count++;
		}
	});
	if($('.adv.group:visible').length>0){
		str+='&amp;adv=true';
	}
	return str;
}


function replaceQueryString(url,param,value) {
	var re = new RegExp("([?|&])" + param + "=.*?(&|$)","i");
	if (url.match(re))
		return url.replace(re,'$1' + param + "=" + value + '$2');
	else
		return url + '&' + param + "=" + value;
}

//Shake function
(function( $ ){
	$.fn.shake = function() {
		var $this = $(this);

		$this.animate({'left':'-20px'},40, function(){
			$(this).animate({left:'10px'},80, function(){
				$(this).animate({'left':'0px'},50)
			})
		});

		return this;
	};
})( jQuery );


//debug
function log(){
	console.log.apply(console, arguments);
}

