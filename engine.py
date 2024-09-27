# Binomial tree option pricer implementation in Python

# Handle the below option contracts 
# 	- European/American call and put on stock w/ or w/o dividends
#	- European/American call and put on stock indices w/ or w/o dividends
#	- European/American call and put on foreign currency 
#	- European/American call and put on futures contract

import math
from operator import attrgetter


class BinomialTree:
	def __init__(self, option_class: str, option_type: str, asset_type: str, initial_price: float, volatility: float, 
					risk_free_rate: float, strike_price: int, time_step: float, steps_number: int, dividend_rate: float = 0,
					foreign_risk_free_rate: float = 0):
		'''
		Init the tree by initializing the first node
		'''
		self.option_class = option_class
		self.option_type = option_type
		self.asset_type = asset_type
		self.volatility = volatility
		self.risk_free_rate = risk_free_rate
		self.strike_price = strike_price
		self.time_step = time_step
		self.steps_number = steps_number
		self.dividend_rate =  dividend_rate
		self.foreign_risk_free_rate = foreign_risk_free_rate

		self.nodes = []
		self.initial_node = BinomialTreeNode(initial_price, 0, self)

	def build_tree(self, node, step_count=0):
		'''
		Build binomial tree | Optimized to avoid to duplication of nodes
		'''
		if node not in self.nodes:
			next_node_up, next_node_down = node.compute_node(step_count + 1)
			self.nodes.append(node)
			print(node)

			if step_count >= self.steps_number:
				return None

			if next_node_up not in self.nodes:
				self.build_tree(next_node_up, step_count + 1)
			else:
				node_index = self.nodes.index(next_node_up)
				node.up_child = self.nodes[node_index]

			if next_node_down not in self.nodes:
				self.build_tree(next_node_down, step_count + 1)
			else:
				node_index = self.nodes.index(next_node_down)
				node.down_child = self.nodes[node_index]

	def backward_pass(self):
		'''
		Backward pass to compute option fair value
		'''
		self.nodes.sort(key=attrgetter("step_count", "asset_price"))
		self.nodes = list(reversed(self.nodes))

		for node in self.nodes:
			if node.step_count == self.steps_number:
				# Compute payoff at terminal nodes
				if self.option_class == "call":
					payoff = max(node.asset_price - self.strike_price, 0)
				if self.option_class == "put":
					payoff = max(self.strike_price - node.asset_price, 0)

				node.option_price = round(payoff, 2)

			else:
				if self.option_class == "call":
					early_exercise_payoff = max(node.asset_price - self.strike_price, 0)
				if self.option_class == "put":
					early_exercise_payoff = max(self.strike_price - node.asset_price, 0)

				discounted_EV = math.exp(-self.risk_free_rate * self.time_step) * (node.p * node.up_child.option_price + (1 - node.p) * node.down_child.option_price)

				if self.option_type == "european":
					node.option_price = round(discounted_EV, 4)
				if self.option_type == "american":
					node.option_price = round(max(early_exercise_payoff, discounted_EV), 2)
					if early_exercise_payoff > discounted_EV:
						node.is_early_exercise_optimal = True

				node.delta = (node.up_child.option_price - node.down_child.option_price) / (node.up_child.asset_price - node.down_child.asset_price)


class BinomialTreeNode:
	def __init__(self, asset_price: float, step_count: int, tree: BinomialTree):
		self.asset_price = asset_price
		self.tree = tree
		self.option_price = 0
		self.delta = 0
		self.step_count = step_count

		if self.tree.option_type == "american":
			self.is_early_exercise_optimal = False

		# Intermediate values
		self.u = 0
		self.d = 0
		self.a = 0
		self.p = 0

		# Child nodes
		self.down_child = None
		self.up_child = None

	def __str__(self):
		return "Node with asset_price = {}, option_price = {}, step_count = {}".format(self.asset_price, self.step_count, self.option_price)

	def __repr__(self):
		return "Node with asset_price = {}, option_price = {}, step_count = {}".format(self.asset_price, self.step_count, self.option_price)

	def __eq__(self, other):
		return (self.asset_price, self.step_count) == (other.asset_price, other.step_count)

	def __hash__(self):
		return hash((self.asset_price, self.step_count))

	def compute_node(self, step_count):
		'''
		Build the node
		'''
		self.u = math.exp(self.tree.volatility * math.sqrt(self.tree.time_step))
		self.d = math.exp((0 - self.tree.volatility) * math.sqrt(self.tree.time_step))

		if (self.tree.asset_type == "stock" or self.tree.asset_type == "stock_index") and self.tree.dividend_rate > 0: # Handle dividend-paying stocks & stock indices
			self.a = math.exp((self.tree.risk_free_rate - self.tree.dividend_rate) * self.tree.time_step)
		elif self.tree.asset_type == "currency" and self.tree.foreign_risk_free_rate > 0: # Handle currency for foreign risk free rate
			self.a = math.exp((self.tree.risk_free_rate - self.tree.foreign_risk_free_rate) * self.tree.time_step)
		else:
			self.a = math.exp(self.tree.risk_free_rate * self.tree.time_step)

		if self.tree.asset_type == "future":
			self.p = (1 - self.d) / (self.u - self.d)
		else:
			self.p = (self.a - self.d) / (self.u - self.d)

		s0_d = round(self.asset_price * self.d, 2)
		s0_u = round(self.asset_price * self.u, 2)

		self.down_child = BinomialTreeNode(s0_d, step_count, self.tree)
		self.up_child = BinomialTreeNode(s0_u, step_count, self.tree)

		return self.up_child, self.down_child
