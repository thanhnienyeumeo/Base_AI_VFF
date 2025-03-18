FROM python:3

WORKDIR /app

ENV ACCEPT_EULA=Y
RUN apt-get update && apt-get install -y --no-install-recommends\
    curl gcc g++ gnupg \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    unixodbc \
    unixodbc-dev \    
    && rm -rf /var/lib/apt/lists/*


# Add SQL Server ODBC Driver 17 for Ubuntu 18.04
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql17 mssql-tools \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3","main.py"]
# CMD ["sleep","infinity"]