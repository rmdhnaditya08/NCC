# 📋 Laporan Open Recruitment NCC 2026 — Pertemuan 1

> **Webhook Logger Service**

| | |
|---|---|
| **Nama** | [Isi Nama Kamu] |
| **NRP** | [Isi NRP Kamu] |
| **Bahasa / Framework** | Python / Flask |
| **Docker Image** | `docker.io/[username]/webhook-logger:latest` |

---

## 📑 Daftar Isi

1. [Deskripsi Singkat Service](#1-deskripsi-singkat-service)
2. [Penjelasan Endpoint /health](#2-penjelasan-endpoint-health)
3. [Bukti Endpoint Dapat Diakses](#3-bukti-endpoint-dapat-diakses)
4. [Proses Build dan Run Docker](#4-proses-build-dan-run-docker)
5. [Proses Deployment ke VPS](#5-proses-deployment-ke-vps)
6. [Kendala yang Dihadapi](#6-kendala-yang-dihadapi)

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

### 3.1 Health Check di Lokal

> 📌 *Tambahkan screenshot hasil `curl http://localhost:5000/health`*

### 3.2 Health Check Publik (VPS)

> 📌 *Tambahkan screenshot hasil `curl http://<IP-VPS>:5000/health`*

### 3.3 Webhook Diterima

> 📌 *Tambahkan screenshot hasil POST ke `/webhook` dan GET ke `/logs`*

### 3.4 Container Berjalan

> 📌 *Tambahkan screenshot `docker compose ps` atau Docker Desktop yang menunjukkan container running*

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

**Perbandingan ukuran image:**

| | Tanpa Multi-Stage | Dengan Multi-Stage |
|---|---|---|
| Ukuran image | ~900MB | ~150MB |
| Build tools ikut terbawa | ✅ Ya | ❌ Tidak |
| Production ready | ❌ | ✅ |

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

> 📌 *Tambahkan screenshot proses `docker compose up -d --build` berjalan sukses*

---

## 5. Proses Deployment ke VPS

### 5.1 Push Image ke Docker Hub

```bash
# Login ke Docker Hub
docker login

# Tag image
docker tag webhook-logger [username]/webhook-logger:latest

# Push image
docker push [username]/webhook-logger:latest
```

### 5.2 Pull dan Jalankan di VPS

```bash
# Pull image dari Docker Hub
docker pull [username]/webhook-logger:latest

# Jalankan container
docker run -d -p 5000:5000 --name webhook-logger \
  --restart unless-stopped \
  [username]/webhook-logger:latest
```

### 5.3 Konfigurasi Firewall

```bash
# Buka port 5000
sudo ufw allow 5000
```

### 5.4 Verifikasi Deployment

```bash
curl http://<IP-VPS>:5000/health
```

> 📌 *Tambahkan screenshot verifikasi endpoint berjalan di VPS*

---

## 6. Kendala yang Dihadapi

| No | Kendala | Solusi | Status |
|---|---|---|---|
| 1 | `Dockerfile` tidak terbaca saat `docker build` — error: *no such file or directory* | File tersimpan sebagai `Dockerfile.txt`. Diperbaiki dengan rename menjadi `Dockerfile` tanpa ekstensi | ✅ Terselesaikan |
| 2 | Container name conflict — error: *container name already in use* | Container lama dihapus terlebih dahulu dengan `docker stop && docker rm` sebelum menjalankan ulang | ✅ Terselesaikan |
| 3 | [Isi kendala lain jika ada] | [Isi solusi] | |

### Pembelajaran

- Memahami cara kerja Docker dan containerisasi aplikasi Python
- Memahami perbedaan antara `docker run` dan `docker compose`
- Memahami konsep multi-stage build untuk mengoptimalkan ukuran image
- Memahami alur deploy image dari lokal → Docker Hub → VPS

---

*Open Recruitment Admin NCC 2026 — Pertemuan 1*
