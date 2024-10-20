App Safety Checker
Overview
This is a simple Flask web application that helps users determine if an app is safe to use based on the number of bad reviews found in Google search results. The application performs a Google search for a given query and checks for the presence of "bad" reviews in the results.

Features
Search Functionality: Users can enter the name of an app, and the application will search for relevant information.
Bad Reviews Detection: The app simulates the detection of bad reviews by looking for the term "bad" in the search results.
Safety Evaluation: It evaluates whether the app is considered safe based on the number of bad reviews found.
Requirements
Python 3.x
Flask
requests
googlesearch-python
You can install the required packages using pip:

bash
Copy code
pip install Flask requests googlesearch-python
How to Run the Application
Clone the repository:

bash
Copy code
git clone https://github.com/<your_username>/app-safety-checker.git
cd app-safety-checker
Run the Flask application:

bash
Copy code
python app.py
Open your web browser and navigate to http://127.0.0.1:5000/.

Usage
Enter the name of the app you want to check in the input field.
Click the "Submit" button.
The application will display the number of bad reviews found and indicate whether the app is safe to use.
License
This project is licensed under the MIT License. Feel free to modify and distribute as needed.

Acknowledgments
Thanks to Flask for the framework.
Thanks to the googlesearch-python library for making Google search requests easier.
