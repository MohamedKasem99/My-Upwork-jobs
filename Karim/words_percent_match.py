from fuzzwuzz.fuzzywuzzy.fuzz_1 import QRatio
x = "1"
print("Welcome. Here's a simple script for you to check the match percentage between words\n>>>>>Anything above 80 will be considered the same<<<<<")
while x == "1":
    word_1 = input("Enter first word: ")
    word_2 = input("Enter second word: ")
    print("\nWords match by : ", QRatio(word_1, word_2), "%\n\n")
    x = input("Enter 1 to enter another word\nEnter 2 to exit\nchoice: ")
    while x != "1" and x != "2":
        print("Enter a valid input (1 or 2): ")
        x = input("Enter 1 to enter another word\nEnter 2 to exit: ")