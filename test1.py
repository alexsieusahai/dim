import subprocess

process = subprocess.Popen(['python3','test.py'],stdout=subprocess.PIPE)

print(process.poll())
for line in iter(process.stdout.readline, b''):
    print(line.decode(),end='')
process.stdout.close()
print(process.poll())

#while True:
#    output = process.stdout.readline().decode('utf8')
#    if output == '' and process.poll() is not None:
#        break
#    if output:
#        print(output.strip(),end='')
#rc = process.poll() # get return code
