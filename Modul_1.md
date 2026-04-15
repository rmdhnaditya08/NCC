# 📋 Laporan Open Recruitment NCC 2026 — Modul 1

Webhook Logger Service

**Nama** : Mochamad Ramadhan Aditya Rachman 

**NRP** : 5025241129 

---

## 1. Deskripsi Singkat Service

**Webhook Logger** adalah service sederhana yang dibangun menggunakan **Python** dan **Flask**. Service ini berfungsi sebagai penerima, pencatat, dan inspector payload webhook dari berbagai sumber eksternal seperti platform pembayaran, GitHub, dan layanan lainnya.

Service ini merupakan alternatif *self-hosted* dari layanan seperti Webhook.site, sehingga pengembang memiliki kontrol penuh atas data webhook yang diterima.

### Fitur Utama

- ✅ Menerima payload webhook melalui HTTP POST
- ✅ Menyimpan log webhook secara persisten menggunakan Docker Volume
- ✅ Menampilkan seluruh log yang masuk melalui endpoint GET
- ✅ Menyediakan endpoint `/health` untuk health check
- ✅ Mendukung penghapusan log melalui endpoint DELETE

### Teknologi yang Digunakan

| Teknologi | Keterangan |
|---|---|
| Python 3.11 | Bahasa pemrograman utama |
| Flask 3.0.0 | Web framework |
| Docker | Containerisasi service |
| Docker Compose | Orkestrasi container |
| Multi-stage Build | Optimasi ukuran image |

### Struktur Project

```
webhook-logger/
├── app.py              # Source code utama
├── requirements.txt    # Dependensi Python
├── Dockerfile          # Konfigurasi build image (multi-stage)
└── docker-compose.yml  # Konfigurasi menjalankan service
```

---

## 2. Penjelasan Endpoint `/health`

Endpoint `/health` dirancang sebagai titik pemeriksaan kesehatan (*health check*) service. Endpoint ini digunakan untuk memverifikasi bahwa service sedang berjalan dan dapat merespons request dengan normal.

### Daftar Endpoint

| Endpoint | Method | Response Code | Deskripsi |
|---|---|---|---|
| `/health` | GET | `200 OK` | Health check — mengecek apakah service berjalan |
| `/webhook` | POST | `200 OK` | Menerima payload webhook dari luar |
| `/logs` | GET | `200 OK` | Menampilkan semua webhook yang masuk |
| `/logs/clear` | DELETE | `200 OK` | Menghapus semua log yang tersimpan |

### Implementasi Kode

```python
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "200 OK",
        "message": "Service is running"
    }), 200
```

### Contoh Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "status": "200 OK",
    "message": "Service is running"
}
```

### Cara Test

```bash
    curl -v http://localhost:5000/health
```

---

## 3. Bukti Endpoint Dapat Diakses

Health Check di Lokal

<img width="815" height="448" alt="image" src="https://github.com/user-attachments/assets/eb1dd67b-8389-42c1-9e88-54ca14d0edc1" />

---

## 4. Proses Build dan Run Docker

### 4.1 Multi-Stage Dockerfile

Dockerfile menggunakan teknik **multi-stage build** yang membagi proses menjadi dua tahap:

```dockerfile
# ==============================
# STAGE 1 — Builder
# ==============================
FROM python:3.11 AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/packages -r requirements.txt


# ==============================
# STAGE 2 — Final (Production)
# ==============================
FROM python:3.11-slim AS final

WORKDIR /app

COPY --from=builder /app/packages /app/packages
COPY app.py .

ENV PYTHONPATH=/app/packages

RUN mkdir -p /app/logs

EXPOSE 5000

CMD ["python", "app.py"]
```


### 4.2 Docker Compose

```yaml
services:
  webhook-logger:
    build: .
    container_name: webhook-logger
    ports:
      - "5000:5000"
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
    volumes:
      - ./logs:/app/logs
```

### 4.3 Perintah Build & Run

```bash
# Build dan jalankan service
docker compose up -d --build

# Cek status container
docker compose ps

# Lihat log container secara live
docker compose logs -f

# Stop dan hapus container
docker compose down
```

<img width="1437" height="655" alt="image" src="https://github.com/user-attachments/assets/5ae293d3-a864-4e91-af8a-c4468093fe97" />

---

## 5. Proses Deployment ke VPS
Proses deployment dilakukan pada Virtual Machine dengan sistem operasi Ubuntu 24.04 LTS yang dijalankan di platform Azure for Students.

### 5.1 Push Image ke Docker Hub

```bash
# Login ke Docker Hub
docker login

# Tag image
docker tag webhook-logger rmdhnaditya08/webhook-logger:latest

# Push image
docker push rmdhnaditya08/webhook-logger:latest
```

### 5.2 Pull dan Jalankan di VPS

```bash
# Jalankan dengan port 80
sudo docker run -d -p 80:5000 --name webhook-logger \
  --restart unless-stopped \
  rmdhnaditya08/webhook-logger:latest

# Verifikasi
sudo docker ps
```

### 5.3 Verifikasi Deployment

```bash
curl http://20.189.79.171/health
```

<img width="743" height="203" alt="image" src="https://github.com/user-attachments/assets/1afecd18-d4e0-47c5-b96f-15c58271292e" />

---

## 6. Kendala yang Dihadapi

1. Kesulitan Mencari VPS yang gratis


