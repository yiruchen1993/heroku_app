FROM python:3.7
ENV TZ=Asia/Taipei
# RUN mkdir -p /code
# ADD linebot_backend.py /code/linebot_backend.py
# ADD Pipfile /code/Pipfile
# ADD Pipfile.lock /code/Pipfile.lock
# RUN pipenv lock --requirements > requirements.txt
# ADD Pipfile /code/requirements.txt
# RUN pip install -r /code/requirements.txt
# CMD ["python", "/code/linebot_backend.py"]

# both files are explicitly required!
ADD linebot_backend.py ./
ADD requirements.txt ./
RUN pip install -r ./requirements.txt
CMD ["python", "linebot_backend.py"]