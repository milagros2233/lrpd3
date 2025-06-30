FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    unixodbc-dev \
    make \
    curl \
    apt-transport-https \
    gnupg \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

RUN pip install --upgrade setuptools

# Eliminar paquetes en conflicto
RUN apt-get remove --purge -y libodbc2 libodbccr2 libodbcinst2 unixodbc-common && \
    apt-get autoremove -y && \
    apt-get clean


# Instalar ODBC Driver 18 para SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --force-yes msodbcsql18

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
