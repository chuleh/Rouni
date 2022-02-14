FROM gorialis/discord.py:3.8.5-buster-master-minimal

WORKDIR /rouni

COPY . ./

RUN pip3 install -r requirements.txt

# Start bot
CMD python3 -u main.py
