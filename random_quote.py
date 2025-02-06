import random

# Read quotes from the file
with open("quotes.txt", "r", encoding="utf-8") as file:
    quotes = file.readlines()

# Strip any leading/trailing whitespace and filter out empty lines
quotes = [quote.strip() for quote in quotes if quote.strip()]

# Print a random quote
if quotes:
    print(random.choice(quotes))
else:
    print("No quotes found in the file.")

