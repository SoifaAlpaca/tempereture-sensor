import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
file_path = 'data.csv'#Must execute the script in the same folder as the data or change the path
data = pd.read_csv(file_path)

ntcdata = data['ntcdata']
lmdata = data['lmdata']
dsdata = data['dsdata']

plt.plot(ntcdata, color=(0, 101/255, 189/255))  # Blue
plt.plot(lmdata, color="#31a748")  # Green
plt.plot(dsdata, color="#f15929")  # Orange

plt.xlabel('Time s')
plt.ylabel('Temperature $^{\\circ}$C')
plt.title('Temperature $^{\\circ}$C vs. Time s')
plt.legend(['NTC', 'LM35', 'DS18B20'])
plt.show()