FROM gorialis/discord.py:3.8.5-buster-master-minimal

ENV DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN

WORKDIR /rouni

COPY . ./

RUN pip3 install -r requirements.txt

# Start bot
CMD ["python3", "-u", "main.py"]
