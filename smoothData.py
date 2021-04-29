import sys

if(len(sys.argv) < 2):
    print("Usage: smoothData.py <csv>")
    exit(1)

csv = []
with open (sys.argv[1], "r") as f:
    f.readline()
    for line in f:
        csv.append(line.strip())
    
areas = []
wilds = []
trainers = []
for line in csv:
    lineSplit = line.split(",")
    areas.append(lineSplit[0])
    wilds.append(float(lineSplit[1]))
    trainers.append(float(lineSplit[2]))
    

for i in range (1, len(areas)):
    if(wilds[i] < 1):
        prev = wilds[i-1]
        
        nextIndex = i
        
        hasNext = True
        while(wilds[nextIndex] == 0):
            if i+1 < len(areas):
                nextIndex += 1
            else:
                #Reached the end
                hasNext = False
                break
        
        if hasNext:
            next = wilds[nextIndex]

            diff = next-prev
            count = nextIndex - i + 1

            step = diff/count

            wilds[i] = -(prev + step)

            for j in range (i, count):
                wilds[j] = -(wilds[j-1] + step)

for i in range (1, len(areas)):
    if(trainers[i] < 1):
        prev = trainers[i-1]
        
        nextIndex = i
        
        hasNext = True
        while(trainers[nextIndex] == 0):
            if i+1 < len(areas):
                nextIndex += 1
            else:
                #Reached the end
                hasNext = False
                break
        
        if hasNext:
            next = trainers[nextIndex]

            diff = next-prev
            count = nextIndex - i + 1

            step = diff/count

            trainers[i] = -(prev + step)

            for j in range (i, count):
                trainers[j] = -(trainers[j-1] + step)
                
print("area,wilds,trainers")
for i in range(len(areas)):
    print(f'{areas[i]},{wilds[i]},{trainers[i]}')
    
if(len(sys.argv) > 2):
    exit(0)
    
with open (sys.argv[1], "w") as out:
    out.write("area,wilds,trainers\n")
    for i in range(len(areas)):
        out.write(f'{areas[i]},{wilds[i]},{trainers[i]}\n')