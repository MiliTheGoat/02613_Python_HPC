grades = []
for i in range(len(sys.argv)-1):
    grades.append(int(sys.argv[i+1]))
avg = sum(grades)/len(grades)
if avg <5:
    result = "Fail"
else:
    result = "Pass"
final = str(avg) + " " + result
print(final)