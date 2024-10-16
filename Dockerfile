# Use the official Python image as the base image
FROM python:3.11.2

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY ./requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY ./Craw/*.py ./Craw/
COPY ./DB/*.py ./DB/
COPY ./PredictedDecision/*.py ./PredictedDecision/
COPY ./Logging/*.py ./Logging/
COPY ./Tele/*.py ./Tele/
COPY ./Train/*.py ./Train/
COPY ./Utils/*.py ./Utils/

# CMD [ "python", "-m", "Tele.TeleMessage" ]
