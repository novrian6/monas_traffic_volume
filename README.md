This project fetches real-time traffic speed from TomTom API every minute and records the data into a CSV file.
The traffic volume is then calculated using the logistic function as shown in the formula below:


k = K_j/ (1 + e^{alpha * (v - v_c)}}


where:
	•	 K_j  = 150 vehicles/km (jam density at full congestion)
	•	 v_c  = 30 km/h (critical speed where max flow occurs)
	•	 \alpha  = 0.1 (shape parameter)
	•	 v  = real-time speed from TomTom API
	•	 k  = traffic density (vehicles per km)
	•	Traffic volume is calculated as  k \times v  (density × speed)
 
 Why Use This Formula?
	•	Captures congestion effects: At low speeds, density increases exponentially.
	•	Smooth transition: It avoids unrealistic sharp transitions between free flow and congestion.
	•	More accurate for urban roads: Compared to simple linear models, this function better models real-world conditions.

Features

✅ Fetches real-time traffic speed every 1 minute.
✅ Records data into a CSV file for historical analysis.
✅ Calculates traffic volume using the logistic formula above.
✅ Displays bar chart (histogram) for the current traffic volume.
✅ Displays line chart for historical traffic trends.

The application steps:
	1.	The script queries TomTom API every 1 minute for speed data from multiple locations.
	2.	It calculates the traffic volume based on speed and jam density.
	3.	The data is saved to a CSV file for future analysis.
	4.	The web dashboard displays:
	•	A bar chart for current traffic conditions.
	•	A line chart showing historical trends with timestamps in dd-MMM-yy hh:mm format.
