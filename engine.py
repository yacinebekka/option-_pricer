### Binomial tree class implementation

## Handle only both European call and put numerical precision to be checked

import math

class BinomialTreeNode:
	def __init__(self, initial_price: float, volatility: float, risk_free_rate: float, strike_price: int, time_step: float, option_class: str):
		self.initial_price = initial_price
		self.volatility = volatility
		self.risk_free_rate = risk_free_rate
		self.strike_price = strike_price
		self.time_step = time_step
		self.option_class = option_class
		self.option_price = None


	def __str__(self):
		return """{} option with S0 = {}, volatility = {}, risk_free_rate = {}, 
						strike_price = {}, time_step = {}, option_price = {}""".format(self.option_class,
																						self.initial_price,
																						self.volatility,
																						self.risk_free_rate,
																						self.strike_price,
																						self.time_step,
																						self.option_price)

	def __repr__(self):
		return """{} option with S0 = {}, volatility = {}, risk_free_rate = {}, 
						strike_price = {}, time_step = {}, option_price = {}""".format(self.option_class,
																						self.initial_price,
																						self.volatility,
																						self.risk_free_rate,
																						self.strike_price,
																						self.time_step,
																						self.option_price)
	def compute_node(self):
		u = round(math.exp(self.volatility * math.sqrt(self.time_step)), 4)
		d = round(math.exp((0 - self.volatility) * math.sqrt(self.time_step)), 4)
		a = round(math.exp(self.risk_free_rate * self.time_step), 4)
		p = round((a - d) / (u - d), 4)

		if self.option_class == "call":
			f_u = round(max(0, u * self.initial_price - self.strike_price), 4)
			f_d = round(max(0, d * self.initial_price - self.strike_price), 4)

		if self.option_class == "put":
			f_u = round(max(0, self.strike_price - u * self.initial_price), 4)
			f_d = round(max(0, self.strike_price - d * self.initial_price), 4)	

		f = round(math.exp(-self.risk_free_rate * self.time_step) * (p * f_u + (1 - p) * f_d), 4)	

		S0_d = self.initial_price * round(math.exp(self.volatility * math.sqrt(self.time_step)), 4)
		S0_u = self.initial_price * round(math.exp((0 - self.volatility) * math.sqrt(self.time_step)), 4)

		delta = (f_u - f_d) / (S0_d - S0_u)

		self.option_price = f

		return f, u, d, a, p, delta

	def return_next_nodes(self):
		next_up_node = BinomialTreeNode(self.initial_price * round(math.exp(self.volatility * math.sqrt(self.time_step)), 4), 
											self.volatility, self.risk_free_rate, self.strike_price, self.time_step, self.option_class)
		next_down_node = BinomialTreeNode(self.initial_price * round(math.exp((0 - self.volatility) * math.sqrt(self.time_step)), 4), 
											self.volatility, self.risk_free_rate, self.strike_price, self.time_step, self.option_class)

		return next_up_node, next_down_node


class BinomialTree:
	## Manage multi-step pricing
	def __init__(self, option_class: str, option_type: str, initial_price: float, volatility: float, risk_free_rate: float, strike_price: int, time_step: float, steps_number: int):
		'''
		Init the tree by initializing the first node
		'''
		self.initial_node = BinomialTreeNode(initial_price, volatility, risk_free_rate, strike_price, time_step, option_class)
		self.steps_number = steps_number
		self.tree_elements = []

	def traverse_tree(self, node, step_count=0):
		'''
		Traverse the binomial tree in a lazy manner, option pricing is not properly computed yet (probably due to numerical precision - TBC)

		TODO : Add support for american option pricing
		'''
		print(node)

		f, u, d, a, p, delta = node.compute_node()
		self.tree_elements.append((f, delta, node.initial_price, step_count))

		if step_count >= self.steps_number:
			return f

		next_node_up, next_node_down = node.return_next_nodes()

		up_option_value = self.traverse_tree(next_node_up, step_count + 1)
		down_option_value = self.traverse_tree(next_node_down, step_count + 1)

		return f
