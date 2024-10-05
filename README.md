
#Adaptive Authentication System

Overview

The Adaptive Authentication System is a security solution that enhances user authentication by integrating behavioral biometrics with traditional authentication methods. This project leverages neural networks to analyze keystroke dynamics and detect anomalies, ensuring a more secure and adaptive authentication process.

Features

Real-Time Keystroke Analysis: Captures keystroke timings to analyze user behavior during login.
Neural Network Integration: Utilizes a trained neural network model to detect anomalies in user behavior.
Admin Interface: A user-friendly Tkinter-based UI for managing the authentication system, including user registration and system monitoring.
Cloud Integration: Securely uploads data to an S3 bucket for enhanced security and accessibility.
Time and Internet Status Display: Real-time display of the current time and internet connection status within the UI.

Usage

Admin Interface


Login: Use the admin credentials to log in to the system.
Register Users: Register new users through the admin interface.
Monitor Activity: View and manage authentication logs, user activities, and system status.
Exit: Close the entire application via the admin interface.

Adaptive Authentication

Users authenticate by entering their credentials and are then analyzed for keystroke dynamics.
The neural network evaluates the keystroke patterns and determines if the login attempt is legitimate.
Alerts or additional security measures are triggered if anomalies are detected.

Implementation Areas

Organizations: Secure access to company systems and data.
Institution Labs: Enhance security for lab computers and networks.
Network Administrators: Monitor and manage authentication across multiple systems.

Contributing
If you'd like to contribute, please fork the repository, create a feature branch, and submit a pull request. Contributions are welcome!

License
This project is licensed under the License. See the LICENSE file for more details.