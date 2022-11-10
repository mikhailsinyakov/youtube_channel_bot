FROM archlinux

WORKDIR /usr/src/app

COPY . .

RUN pacman -Syu --noconfirm
RUN pacman -Sy python-pip --noconfirm
RUN pacman -S tk --noconfirm
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]