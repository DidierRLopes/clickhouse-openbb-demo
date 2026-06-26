# ClickHouse Explorer for OpenBB Workspace

Explore ClickHouse sample datasets (UK Housing Prices & NYC Taxi Trips) inside [OpenBB Workspace](https://pro.openbb.co).

## Datasets

### UK Housing Prices

27M+ property transactions from the UK Land Registry (1995–present)

<img width="800" alt="CleanShot 2026-04-18 at 17 34 40@2x" src="https://github.com/user-attachments/assets/91f13940-3640-4a9e-aff9-cef4e7431fff" />

### NYC Taxi Trips

3M+ taxi rides with fares, distances, and pickup zones

<img width="800" alt="CleanShot 2026-04-18 at 17 34 24@2x" src="https://github.com/user-attachments/assets/ad3bda42-f818-4c86-91ae-0f6e20d3b1b1" />

## Setup

### 1. ClickHouse Cloud

1. Sign up at [clickhouse.cloud](https://clickhouse.cloud/) and create a new service
2. When the service is created, you'll be shown the connection credentials — **save the password**, it is only displayed once
3. Once the service is running, click **Connect** to find your connection details

### 2. Environment variables

```bash
cp .env.example .env
```

Edit `.env` with your ClickHouse credentials:

| Variable | Required | Default | Where to find |
|---|---|---|---|
| `CLICKHOUSE_HOST` | Yes | — | ClickHouse Cloud console → your service → **Connect** → the hostname (e.g. `abc123.us-east-1.aws.clickhouse.cloud`) |
| `CLICKHOUSE_PASSWORD` | Yes | — | Shown once when you create the service. If lost, reset it under **Settings** → **Reset password** |
| `CLICKHOUSE_PORT` | No | `8443` | Default HTTPS native port — no need to change unless your service uses a custom port |
| `CLICKHOUSE_USER` | No | `default` | The default admin user created with every ClickHouse Cloud service |

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Load sample data

```bash
source .env && export CLICKHOUSE_HOST CLICKHOUSE_PORT CLICKHOUSE_USER CLICKHOUSE_PASSWORD
python setup.py
```

This creates two databases (`uk` and `nyc_taxi`) and loads the sample datasets. The UK dataset (~27M rows) may take several minutes.

### 5. Start the server

```bash
source .env && export CLICKHOUSE_HOST CLICKHOUSE_PORT CLICKHOUSE_USER CLICKHOUSE_PASSWORD
python main.py
```

The server starts on `http://localhost:7781`.

### 6. Connect to OpenBB Workspace

1. Go to [pro.openbb.co/app/connections](https://pro.openbb.co/app/connections)
2. Add a custom backend with URL `http://localhost:7781`

<img width="1394" height="781" alt="CleanShot 2026-06-26 at 17 27 23" src="https://github.com/user-attachments/assets/d9ab278c-dbd5-4bee-9edc-c602a1ab45b9" />

3. Two dashboards will appear in the [Apps page](https://pro.openbb.co/app): **UK Housing Prices** and **NYC Taxi Trips**

<img width="809" height="535" alt="CleanShot 2026-06-26 at 17 28 23" src="https://github.com/user-attachments/assets/3077399b-db18-496f-9343-0f73581fa19d" />

