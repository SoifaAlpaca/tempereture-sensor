import serial
import time
import matplotlib.pyplot as plt
import pandas as pd
# timeout is 1 second for reading
ser = serial.Serial('COM6', 115200, timeout=2)
time.sleep(2)  # wait for the Serial to initialize

number = 50  # number of lines to read

ntcdata = []
lmdata = []
dsdata = []
for i in range(number):  # range is the number of lines to read
    line = ser.readline()
    if line:
        string = line.decode()  # convert the byte string to a normal string
        print(string)
        ntcdata.append(float(string.split(',')[0]))
        lmdata.append(float(string.split(',')[1]))
        dsdata.append(float(string.split(',')[2]))

ser.close()

df = pd.DataFrame({
    'lmdata': ntcdata,
    'ntcdata': lmdata,
    'dsdata': dsdata
})

df.to_csv('data.csv', index=False)
plt.plot(ntcdata, color=(0, 101/255, 189/255))
plt.plot(lmdata, color=("#31a748"))
plt.plot(dsdata, color=("#f15929"))

plt.xlabel('Time s')
plt.ylabel('Temperature $^{\\circ}$C')
plt.title('Temperature $^{\\circ}$C vs. Time s')
plt.legend(['NTC', 'LM35', 'DS18B20'])
plt.show()

df.to_csv('data.csv', index=False)

# graph color change
