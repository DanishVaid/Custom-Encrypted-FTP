new_file = open('1000mb.txt', 'w')

for i in range(10):
    curr_file = open('100mb.txt', 'r')
    line = curr_file.readline()
    while line:
        new_file.write(line)
        line = curr_file.readline()
    curr_file.close()