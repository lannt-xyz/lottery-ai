#!/bin/bash
# Navigate to the directory containing your Docker context, if necessary
cd /home/lanntxyz/LotteryAi

# Run the Docker container
docker run -d --rm --name tele-notify \
    -v /etc/localtime:/etc/localtime:ro \
    -v $(pwd)/.envcp:/app/.env:ro \
    -v $(pwd)/models:/app/models \
    -v $(pwd)/crawing-data:/app/crawing-data \
    -v $(pwd)/data:/app/data \
    lotteryai_common python -m Tele.TeleMessage
