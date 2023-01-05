FROM python:3.10

# Set the working directory to /app
WORKDIR /cyclic-arbitrage

# Copy the current directory contents into the container at /app
COPY . /cyclic-arbitrage

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Run the app when the container launches
CMD ["python", "-u", "main.py"]
