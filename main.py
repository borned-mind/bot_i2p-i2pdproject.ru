from Bot import Bot
def main():
	try:
		bot = Bot()
		bot.Receive()
	except Exception as exc:
		print str(exc)

main()
