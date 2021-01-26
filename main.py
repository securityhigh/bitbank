from utils import *
from os import system
from time import time
from colorama import Fore


config_file = "config.ini"
log_file = ".history"

version = 'v0.1b'
logs = ''

config_object = Config(config_file)
config = config_object.config
bitcoin = Bitcoin(config["BITCOIN"]["seed"], 1)


def logout():
	text = ''

	try:
		with open(log_file) as file:
			text = file.read()

	except:
		pass

	with open(log_file, 'w') as file:
		file.write(text + logs)

	system("clear")
	print("[logout]")


def main():
	system("clear")
	print(f"Используйте команду 'help' для просмотра команд. [{version}, OVNL.IN]")

	try:
		while True:
			handler(input(Fore.LIGHTGREEN_EX + f'(bitbank:{bitcoin.index}) > ' + Fore.RESET))

	except KeyboardInterrupt:
		logout()


def handler(message):
	global bitcoin, logs

	if message.strip() == '':
		return

	args = message.split(" ")
	logs += '\n[' + date(time()) + '] ' + message

	if args[0] == "help" or args[0] == "ls":
		print("\n rate :: курс Bitcoin")
		print(" balance :: баланс кошелька")
		print(" address :: адрес для пополнения")
		print(" history :: последние 3 транзакции")
		print(" send <address> <currency> <money> <fee> :: совершить транзакцию\n")

		print(" seed :: ваш секретный ключ кошелька")
		print(" quit :: закрыть программу")
		print(" clear :: очистить экран")
		print(" set <index> :: сменить кошелек")
		print(" auth <seed> :: авторизироваться временно под другим seed")
		print(" deauth :: вернуться к прежнему кошельку")
		print(" install :: генерация нового секретного ключа и сброс счетов\n")

		print(" ? index - индекс кошелька, бесконечное количество на одном ключе")
		print(" ? currency - rub, btc, usd")
		print(" ? money - указывается в валюте, которая в currency")
		print(" ? fee - комиссия для майнеров, указывается в сатоши, от 1000")
		print(" ? seed - 12 слов, которые являются ключом к вашем кошелькам")
		print(" ? 1000 сатоши - 0.00001 BTC\n")

	elif args[0] == "balance":
		btc = bitcoin.balance(bitcoin.address, "btc")
		rub = bitcoin.balance(bitcoin.address, "rub")
		usd = bitcoin.balance(bitcoin.address, "usd")

		print(f"\n Баланс кошелька #{bitcoin.index}")
		print(" BTC:", btc)
		print(" RUB:", rub)
		print(" USD:", usd, "\n")

	elif args[0] == "rate":
		rub = fmoney(bitcoin.rate("rub"))
		usd = fmoney(bitcoin.rate("usd"))

		print("\n RUB:", rub)
		print(" USD:", usd, "\n")

	elif args[0] == "address":
		print(f"\n Адрес кошелька #{bitcoin.index}\n {bitcoin.address}\n")

	elif args[0] == "seed":
		print(f"\n {bitcoin.seed} \n")

	elif args[0] in ["cls", "clear", "clr"]:
		system("clear")

	elif args[0] in ["exit", "quit", "close"]:
		raise KeyboardInterrupt

	elif args[0] == "set":
		if len(args) == 2 and args[1].isdigit():
			bitcoin.set(int(args[1]))

		else:
			print("\n set <index>\n Смена индекса кошелька, позволяет иметь огромное количество адресов на одном seed.\n")

	elif args[0] == "auth":
		if len(args) > 2:
			bitcoin = Bitcoin(' '.join(args[1:]), 1)

		else:
			print("\n auth <seed>\n Временная смена секретного значения seed для смены кошелька на другой.\n")

	elif args[0] == "deauth":
		bitcoin = Bitcoin(config["BITCOIN"]["seed"], 1)

	elif args[0] == "install":
		seeds = config["BITCOIN"]["seed"]

		if len(seeds) < 5:
			config["BITCOIN"]["seed"] = seed()

		else:
			a = input("\n Регенерация ключей приведет к потере всех счетов и средств, вы уверены? [y/N]: ")

			if a == "y":
				a = input(" Точно? [y/N]: ")

				if a == "y":
					with open("seed.old", "w") as file:
						file.write(seeds)

					config["BITCOIN"]["seed"] = seed()
					bitcoin = Bitcoin(config["BITCOIN"]["seed"])
					print(f" Новый ключ сгенерирован в {filename}, старый скопирован в файл 'seed.old'.\n")

				else:
					print('')

			else:
				print('')

		config_object.save()

	elif args[0] == "history":
		transactions = bitcoin.transactions()

		c = 0
		for t in transactions:
			if c == 0: print('')
			if c == 3: break
			print(" hash:", t["hash"])
			print(" btc:", format(t["value"] / 100000000, "0.8f"))
			print(" date:", date(t["time"]))
			print(" confirmations:", t["confirmations"])
			print('')
			c += 1

	elif args[0] in ["transaction", "send"]:
		if len(args) == 5:
			try:
				if defense_bitcoin(args[1]):
					wallet = args[1]
					if args[2].lower() in ["rub", "btc", "usd"]:
						currency = args[2].lower()
						
						if currency == "btc":
							money = float(args[3])

						else:
							money = int(args[3])

						if args[4].isdigit() and int(args[4]) > 1000:
							fee = int(args[4])

							response = bitcoin.send(wallet, money, fee, currency)
							print("", response)

						else:
							print("\n Неверное значение fee, минимальное 1000.\n")
					else:
						print("\n Неверное значение currency.\n")
				else:
					print("\n Неверное указан адрес кошелька.\n")

			except ValueError:
				print("\n Неверно указана сумма перевода.\n")

		else:
			print("\n send <address> <currency> <money> <fee>\n Совершение перевода на другой BTC кошелек.\n")


if __name__ == "__main__":
	main()