
### Binomial tree class implementation

import math

class BinomialTreeNode:
	def __init__(self, initial_price: float, volatility: float, risk_free_rate: float, strike_price: int, time_step: float):
		self.initial_price = initial_price
		self.volatility = volatility
		self.risk_free_rate = risk_free_rate
		self.strike_price = strike_price
		self.time_step = time_step

	def get_option_price_at_node(self):

		u = math.exp(self.volatility * math.sqrt(self.time_step))
		d = math.exp((0 - self.volatility) * math.sqrt(self.time_step))
		a = math.exp(self.risk_free_rate * self.time_step)
		p = (a - d) / (u - d)

		f_u = max(0, u * self.initial_price - self.strike_price)
		f_d = max(0, d * self.initial_price - self.strike_price)

		print(p, u, d, a, f_u, f_d)

		return math.exp(-self.risk_free_rate * self.time_step) * (p * f_u + (1 - p) * f_d)


class BinomialTree:
	## Manage multi-step pricing
	def __init__(self):
		pass