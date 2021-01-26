from bipwallet import wallet
from bipwallet.utils import *
import configparser
import requests
import datetime
import pyqiwi
import time
import bit
import re


def seed():
	return wallet.generate_mnemonic()


def unix(sdate):
	return round(time.mktime(datetime.datetime.strptime(sdate, "%Y-%m-%dT%H:%M:%SZ").timetuple()))


def date(sunix):
	return datetime.datetime.fromtimestamp(sunix).strftime('%Y-%m-%d %H:%M:%S')


def defense_bitcoin(text):
	match = re.fullmatch(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', text)
	return match


def fmoney(money):
	return '{:,}'.format(money)


class Config:
	def __init__(self, filename):
		self.filename = filename
		self.config = configparser.ConfigParser()
		self.config.read(filename)

	def update(self):
		self.config = configparser.ConfigParser()
		self.config.read(self.filename)

	def save(self):
		with open(self.filename, "w") as file:
			self.config.write(file)


class Bitcoin:
	def __init__(self, seed, index):
		self.index, self.seed = index, seed
		self.address, self.wif = self.generate(seed)

	def set(self, index):
		self.index = index
		self.address, self.wif = self.generate(self.seed)

	def generate(self, seed):
		master_key = HDPrivateKey.master_key_from_mnemonic(seed)

		root_keys = HDKey.from_path(master_key, "m/44'/0'/0'/0")[-1].public_key.to_b58check()
		xpublic_key = root_keys

		address = Wallet.deserialize(xpublic_key, network='BTC').get_child(self.index, is_prime=False).to_address()
		rootkeys_wif = HDKey.from_path(master_key, f"m/44'/0'/0'/0/{self.index}")[-1]

		xprivatekey = rootkeys_wif.to_b58check()
		wif = Wallet.deserialize(xprivatekey, network='BTC').export_to_wif()

		return address, wif

	def transactions(self):
		try:
			response = []
			wallets = self.information(self.address)["txrefs"]

			for t in wallets:
				m = 1
				if t["tx_input_n"] == 0: m = -1
				response.append({"hash": t["tx_hash"], "time": unix(t["confirmed"]), "value": t["value"] * m, "confirmations": t["confirmations"]})

			return response
		except KeyError:
			return []

	def information(self, wallet):
		url = f'https://api.blockcypher.com/v1/btc/main/addrs/{wallet}'
		response = requests.get(url).json()

		return response

	def send(self, address, money, fee, currency="btc"):
		key = bit.Key(self.wif)
		transaction_hash = key.create_transaction([(address, money, currency)], fee=fee, absolute_fee=True)

		response = requests.post('https://blockchain.info/pushtx', data={'tx': transaction_hash}).text

		return response

	def balance(self, wallet, currency="sat"):
		satoshi = self.information(wallet)["final_balance"]

		if currency.lower() == "sat":
			return satoshi

		elif currency.lower() == "btc":
			return round(satoshi / 100000000, 8)

		else:
			return round(satoshi / 100000000 * self.rate(currency))

	def rate(self, currency="RUB"):
		return int(requests.get('https://blockchain.info/ticker').json()[currency.upper()]["last"])
