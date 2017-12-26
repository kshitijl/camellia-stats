/**
 * 랭킹
 */
var Ranking = eg.Class({

	construct : function(option) {
		this._initVars(option);
		if (this._layer != null) {
			this._setEvent();
		}
	},

	/**
	 * 파라미터 초기화
	 *
	 * @param option {HashTable} 옵션
	 */
	_initVars : function(option) {
		this._template = Handlebars.compile($(option.templateId).html());
		this._genreNameMap = option.genreNameMap;
		this._apiInfo = option.apiInfo;

		this._layer = $(option.layerId);
		if (this._layer != null) {
			this._filterArea = this._layer.find('._filterArea');
			this._filterLayer = this._filterArea.find('._filterLayer');
			this._titleListArea = this._layer.find('._titleListArea');

			new LayerManager(this._filterLayer[0]).link(this._filterArea.find('a.checked')[0]).link(this._filterLayer[0]);
		}
	},

	/**
	 * 이벤트 핸들러 지정
	 */
	_setEvent : function() {
		this._filterArea
			.on('click', 'a.checked', $.proxy(this._openFilterLayer, this))
			.on('click', '._filterItem', $.proxy(this._onClickFilterItem, this));
	},

	/**
	 * 필터 레이어 보이기
	 *
	 * @param event {Wrapping Event} Event
	 */
	_openFilterLayer : function(event) {
		event.preventDefault();
		this._filterLayer.show();
	},

	/**
	 * 필터 클릭 이벤트 처리
	 *
	 * @param event {Wrapping Event} Event
	 */
	_onClickFilterItem : function(event) {
		event.preventDefault();

		var selectedFilter = event.target;

		var filterParamValue = $(selectedFilter).data('filter');
		var filterParamName = this._apiInfo.filterParamName;
		var data = {};
		data[filterParamName] = filterParamValue;
		data['count'] = this._apiInfo.count;

		$.ajax({
			url : this._apiInfo.url,
			timeout : 5000,
			data : data
		}).then($.proxy(function(res) {
			this._refresh(res);
			this._setFilterSelect(selectedFilter);
		}, this));

		this._filterLayer.hide();
	},

	/**
	 * 목록 갱신
	 *
	 * @param titleList {Array} 타이틀 json 배열
	 */
	_refresh : function(titleList) {
		if (!titleList || titleList.length == 0) {
			return;
		}

		var htmlList = [];
		for (var i = 0, n = titleList.length; i < n; i++) {
			var title = titleList[i];
			title['ranking'] = i + 1;
			if (this._genreNameMap) {
				title['genreName'] = this._genreNameMap[title.representGenre];
			}
			title['cssGenreName'] = title.representGenre.toLowerCase();

			var authorName = title.writingAuthorName || title.pictureAuthorName;

			if(title.pictureAuthorName && title.writingAuthorName != title.pictureAuthorName) {
				authorName = authorName + ' / ' + title.pictureAuthorName;
			}

			title.authorName = authorName;

			var html = this._template(title);
			htmlList.push(html);
		}
		this._titleListArea.html(htmlList.join('\n'));
	},

	/**
	 * 필터 선택 변경
	 *
	 * @param el {Element} 선택한 필터
	 */
	_setFilterSelect : function(el) {
		// 이전 선택 해제
		var checkIcon = this._filterLayer.find('.ico_chk');
		checkIcon.remove();

		// 신규 선택
		var wel = $(el);
		wel.append(checkIcon);
		this._filterArea.find('a.checked').html(wel.html());
	},

	/**
	 * 현재 선택된 필터 조회
	 *
	 * @return {String} 선택된 필터 파라미터
	 */
	getSelectedFilter : function() {
		return this._filterLayer.find('span.ico_chk').parent('._filterItem').data('filter');
	}
});