#!/bin/bash
# Navigate to the directory containing your Docker context, if necessary
cd /home/lanntxyz/LotteryAi

# Run the Docker container
docker run -d --rm --name craw-data \
  -v /etc/localtime:/etc/localtime:ro \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/crawing-data:/app/crawing-data \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e CRAWING_TARGET=KQXSVN \
  lotteryai_craw
