### Binomial tree class implementation

## Handle only both European call and put numerical precision to be checked

import math
from operator import attrgetter

class BinomialTreeNode:
	def __init__(self, initial_price: float, volatility: float, risk_free_rate: float, strike_price: int, time_step: float, option_class: str, step_count: int):
		self.initial_price = initial_price
		self.volatility = volatility
		self.risk_free_rate = risk_free_rate
		self.strike_price = strike_price
		self.time_step = time_step
		self.option_class = option_class
		self.option_price = 0
		self.delta = 0
		self.step_count = step_count

		# Intermediate values
		self.u = 0
		self.d = 0
		self.a = 0
		self.p = 0

		# Child nodes
		self.down_child = None
		self.up_child = None

	def __str__(self):
		return ("{} option with S0 = {}, volatility = {}, risk_free_rate = {}, " 
						"strike_price = {}, time_step = {}, option_price = {} "
						"step_count = {}"												).format(self.option_class,
																						self.initial_price,
																						self.volatility,
																						self.risk_free_rate,
																						self.strike_price,
																						self.time_step,
																						self.option_price,
																						self.step_count)

	def __repr__(self):
		return ("{} option with S0 = {}, volatility = {}, risk_free_rate = {}," 
						"strike_price = {}, time_step = {}, option_price = {}"
						"step_count = {}"												).format(self.option_class,
																						self.initial_price,
																						self.volatility,
																						self.risk_free_rate,
																						self.strike_price,
																						self.time_step,
																						self.option_price,
																						self.step_count)
	def compute_node(self, step_count):
		'''
		Build the node
		'''
		self.u = math.exp(self.volatility * math.sqrt(self.time_step))
		self.d = math.exp((0 - self.volatility) * math.sqrt(self.time_step))
		self.a = math.exp(self.risk_free_rate * self.time_step)
		self.p = (self.a - self.d) / (self.u - self.d)

		S0_d = round(self.initial_price * self.d, 4)
		S0_u = round(self.initial_price * self.u, 4)

		self.down_child = BinomialTreeNode(S0_d, self.volatility, self.risk_free_rate, self.strike_price, self.time_step, self.option_class, step_count)
		self.up_child = BinomialTreeNode(S0_u, self.volatility, self.risk_free_rate, self.strike_price, self.time_step, self.option_class, step_count)

		return self.up_child, self.down_child


## TODO --> Reorganize the attributes of the tree and the nodes (ie : option type and class can be managed at tree level rather than at node level)

class BinomialTree:
	def __init__(self, option_class: str, option_type: str, initial_price: float, volatility: float, risk_free_rate: float, strike_price: int, time_step: float, steps_number: int):
		'''
		Init the tree by initializing the first node
		'''
		self.initial_node = BinomialTreeNode(initial_price, volatility, risk_free_rate, strike_price, time_step, option_class, 0)
		self.steps_number = steps_number
		self.tree_elements = []

	def build_tree(self, node, step_count=0):
		'''
		Build binomial tree
		'''
		next_node_up, next_node_down = node.compute_node(step_count + 1)
		self.tree_elements.append(node)
		print(node)

		if step_count >= self.steps_number:
			return None

		self.build_tree(next_node_up, step_count + 1)
		self.build_tree(next_node_down, step_count + 1)

	def backward_pass(self):
		self.tree_elements.sort(key=attrgetter("step_count"))
		self.tree_elements = list(reversed(self.tree_elements))

		for node in self.tree_elements:
			if node.step_count == self.steps_number:
				# Compute payoff at terminal nodes
				if self.initial_node.option_class == "call":
					payoff = max(node.initial_price - node.strike_price, 0)
				if self.initial_node.option_class == "put":
					payoff = max(node.strike_price - node.initial_price, 0)

				node.option_price = round(payoff, 4)

			else:
				discounted_EV = math.exp(-node.risk_free_rate * node.time_step) * (node.p * node.up_child.option_price + (1 - node.p) * node.down_child.option_price)
				node.option_price = round(discounted_EV, 4)
