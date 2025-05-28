# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
# This layer will be cached if requirements.txt doesn't change
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY . /app

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py"]
