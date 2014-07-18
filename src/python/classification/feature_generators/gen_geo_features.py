
class geo_feature_generator:
	self.states = 
	

	def __init__(self):


	def gen_geo_features(self, entity, features = ['geo_inferred_text_has_state', 'geo_inferred_text_has_city']):
		return {f: eval(f)(entity) for f in features}



	def geo_inferred_text_has_state(self, entity):



	def geo_inferred_text_has_city(self, entity):

