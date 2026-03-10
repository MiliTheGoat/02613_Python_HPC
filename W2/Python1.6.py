import sys
numbers = []
for i in range(len(sys.argv)-1):
    numbers.append(int(sys.argv[i+1]))
even_numbers = []
for number in numbers:
    if number % 2 == 0:
        even_numbers.append(number)
print(even_numbers)