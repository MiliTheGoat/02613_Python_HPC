string = "Hello World"
print(string)
with open("context.txt", "w") as file:
    file.write(string)