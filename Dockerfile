FROM python:3.7
ENV TZ=Asia/Taipei

# both files are explicitly required!
ADD linebot_backend.py ./
ADD requirements.txt ./
RUN pip install -r ./requirements.txt
CMD ["python", "linebot_backend.py"]