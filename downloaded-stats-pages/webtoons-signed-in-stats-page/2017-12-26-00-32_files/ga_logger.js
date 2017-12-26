/**
 * ga_logger.js
 */
var GaLogger = GaLogger || {
		id : undefined
		, isInit : false
		, dimensions : {}
		, pendingDimensions : {}
		, readInfo : {
			eventLabel : ''
			, callReadComplete : false
		}
		/**
		 * 초기화
		 */
		, init : function(id) {
			if(this.isInit) {
				return;
			}
			
			(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
				(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
				m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
				})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
			
			this.id = id;
			ga('create', this.id, 'auto');
			this.isInit = true;
		}
		
		/**
		 * dimension 설정
		 */
		, set : function(dimension, value) {
			if(this.isInit) {
				ga('set', dimension, value);
				this.dimensions[dimension] = value;
			} else {
				this.pendingDimensions[dimension] = value;
			}
		}
		
		/**
		 * display features plugin 설정
		 */
		, displayfeatures : function() {
			this._ga('require', 'displayfeatures');
		}
		
		/**
		 * PV 호출
		 */
		, pageView : function() {
			this._ga('send', 'pageview');
		}
		
		/**
		 * 회차 read 이벤트 호출
		 */
		, episodeRead : function(eventLabel, dimensions) {
			this.readInfo.eventLabel = eventLabel;
			var oDimension = {
				'dimension2' : dimensions.titleNo
				, 'dimension3' : dimensions.episodeNo
				, 'dimension9' : dimensions.weekday
				, 'dimension11' : dimensions.genre
			};
			this.gaEventLoggingByDimensions('Read', 'Read_Episode', this.readInfo.eventLabel, oDimension);
		}
		
		/**
		 * 회차 read Complete 이벤트 호출
		 */
		, episodeReadComplete : function() {
			if(!this.readInfo.eventLabel) {
				return;
			}
			
			if(this.readInfo.callReadComplete) {
				return;
			}
			
			this.readInfo.callReadComplete = true;
			this.gaEventLoggingByDimensions('Read', 'Read_Complete', this.readInfo.eventLabel);
		}
		
		/**
		 * GA Event 로깅
		 * 
		 * @param eventCategory
		 * @param eventAction
		 * @param eventLabel
		 * @param titleNo
		 * @param episodeNo
		 */
		, gaEventLogging : function(eventCategory, eventAction, eventLabel, titleNo, episodeNo) {
			this._clearDimensions();

			if (titleNo) {
				this.set('dimension2', titleNo);
			}
			
			if(episodeNo) {
				this.set('dimension3', episodeNo);
			}
			
			this._ga('send', 'event', eventCategory, eventAction, eventLabel);
		}
		
		/**
		 * GA Event 로깅
		 * 
		 * @param eventCategory
		 * @param eventAction
		 * @param eventLabel
		 * @param dimensions
		 */
		, gaEventLoggingByDimensions : function(eventCategory, eventAction, eventLabel, dimensions) {
			this._clearDimensions();
			if(dimensions) {
				for(var key in dimensions) {
					this.set(key, dimensions[key]);
				}
			}
			
			this._ga('send', 'event', eventCategory, eventAction, eventLabel);
		}
		
		/**
		 * GA function 수행
		 */
		, _ga : function(command, hitType, category, action, label) {
			this._addPendingDimensions();
			ga(command, hitType, category, action, label);
		}
		
		/**
		 * 추가되지 않은 dimensions 추가
		 */
		, _addPendingDimensions : function() {
			for(var key in this.pendingDimensions) {
				this.set(key, this.pendingDimensions[key]);
			}
		}

		/**
		 * dimensions clear
		 *  - 한번 추가된 dimensions은 페이지가 변경되지 않은한 살아 있기 때문에 이를 clear해준다.
		 *  - dimensions4 (contentLanguage)는 clear하지 않음
		 * @private
         */
		, _clearDimensions : function() {
			if(Object.keys(this.dimensions).length < 1) {
				return;
			}

			for(var key in this.dimensions) {
				if( key != "dimension4") {
					delete this.dimensions[key];
					// ga dimension setting 제거
					ga('set', key, null);
				}
			}
		}
};