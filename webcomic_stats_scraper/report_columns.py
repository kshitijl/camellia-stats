column_data_from_client = [
    ("tapas.subs", "Tap Subs"),
    ("tapas.subs.diff", "T New Subs"),
    ("tapas.views", "T Views"),
	  ("tapas.views.diff", "T New Views"),
	  ("webtoons.subs", "W Subs"),
	  ("webtoons.subs.diff", "W New Subs"),
	  ("webtoons.views", "Webtoons Views"),
	  ("webtoons.views.diff", "Webtoons New Views"),
	  ("webtoons.monthly_pvs", "Webtoon month views"),
	  ("webtoons.monthly_pvs.diff", "Webtoons New Views (Monthly)"),
	  ("webtoons.likes", "Webtoons Likes"),
	  ("webtoons.rating", "Webtoons Rating"),
	  ("rank-in.tapas.trending-comics", "Trending Position"),
	  ("rank-in.tapas.popular-comics", "Popular Position")
]

column_inverse_mapping = dict([(client_name,our_name) for (our_name,client_name) in column_data_from_client])
columns_in_order       = [client_name for (_, client_name) in column_data_from_client]

def our_name_for(x):
    return column_inverse_mapping[x]

