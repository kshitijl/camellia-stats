/**
 * facebook_logger.js
 */

var FacebookLogger = FacebookLogger || {
		id : undefined
		, isInit : false
		/**
		 * 초기화
		 */
		, init : function(id) {
			!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','//connect.facebook.net/en_US/fbevents.js');
			this.id = id;
			fbq('init', this.id);
			this.isInit = true;
		}

		/**
		 * PV
		 */
		, pageView : function() {
			this.log({
				'method' : "track"
				, 'action' : "PageView"
			});
		}
		
		/**
		 * ViewContent
		 */
		, viewContent : function(title, episodeNo) {
			this.log({
				'method' : "track"
				, 'action' : "ViewContent"
				, 'params' : {
					'content_ids' : [title + "_EP" + episodeNo]
					, 'content_type' : "product"
				}
			});
		}
		
		/**
		 * options : {
		 * 		method
		 * 		, action
		 * 		, params
		 * }
		 */
		, log : function(options) {
			if(!this.isInit) {
				return;
			}
			
			if(!options) {
				console.log("FACEBOOK paramater error.");
				return;
			}
			
			fbq(options.method, options.action, options.params);
		}
};