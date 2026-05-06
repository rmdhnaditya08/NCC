# Modul 2

**Nama:** Mochamad Ramadhan Aditya Rachman  
**Repository:** [rmdhnaditya08/NCC](https://github.com/rmdhnaditya08/NCC)  
**Branch:** Modul-2

---

## Daftar Isi

1. [Deskripsi Pipeline](#1-deskripsi-pipeline)
2. [Penjelasan Alur Pipeline](#2-penjelasan-alur-pipeline)
3. [Integrasi Jenkins dengan SonarQube](#3-integrasi-jenkins-dengan-sonarqube)
4. [Konfigurasi Jenkins](#4-konfigurasi-jenkins)
5. [Konfigurasi SonarQube](#5-konfigurasi-sonarqube)
6. [Hasil Analisis Kode di SonarQube](#6-hasil-analisis-kode-di-sonarqube)
7. [Kendala yang Dihadapi](#7-kendala-yang-dihadapi)

---

## 1. Deskripsi Pipeline

Pipeline **pipeline-modul2** adalah implementasi *Continuous Integration and Continuous Deployment* (CI/CD) yang dibangun menggunakan **Jenkins** dengan pendekatan *declarative pipeline*. Pipeline ini mengotomatisasi seluruh proses pengembangan aplikasi web berbasis **Python Flask**, mulai dari pengambilan kode sumber, pengujian otomatis, analisis kualitas kode menggunakan **SonarQube**, hingga deployment aplikasi ke dalam container Docker.

Setiap perubahan kode yang di-*push* ke branch `Modul-2` di GitHub akan secara otomatis men-trigger pipeline melalui mekanisme **webhook**, tanpa perlu intervensi manual.

### Teknologi yang Digunakan

| Teknologi | Versi | Fungsi |
|---|---|---|
| **Jenkins** | 2.541.3 (BlueOcean) | Server CI/CD otomasi pipeline |
| **SonarQube** | Community Build v26.4 | Analisis kualitas dan keamanan kode |
| **SonarScanner** | 6.2.1 | CLI tool untuk menjalankan analisis kode |
| **Docker** | latest | Containerisasi aplikasi |
| **Docker Hub** | - | Registry penyimpanan Docker image |
| **GitHub** | - | Version control & trigger webhook |
| **Python Flask** | 3.0.3 | Framework aplikasi web |
| **Gunicorn** | 22.0.0 | WSGI server untuk production |
| **pytest** | latest | Framework unit testing |


## 2. Penjelasan Alur Pipeline

### Penjelasan Tiap Stage

**Stage 1 — Checkout**  
Jenkins mengambil kode terbaru dari GitHub repository `rmdhnaditya08/NCC` branch `Modul-2`. Memastikan pipeline selalu memproses versi kode paling baru.

**Stage 2 — Build**  
Menginstall semua dependencies Python menggunakan `pip`. Dependencies yang diinstall antara lain Flask (web framework) dan Gunicorn (WSGI server production). Karena Python tidak tersedia di Jenkins container secara native, pipeline menggunakan fallback `pip3` dan skip jika tidak ditemukan.

**Stage 3 — Test**  
Menjalankan 2 unit test otomatis menggunakan **pytest**:
- `test_home` — memverifikasi endpoint `/` mengembalikan status 200 dan response JSON yang benar
- `test_health` — memverifikasi endpoint `/health` mengembalikan status healthy

**Stage 4 — SonarQube Analysis**  
Menjalankan **SonarScanner** yang menganalisis seluruh kode sumber secara statis. Scanner membaca konfigurasi dari `sonar-project.properties` dan mengirimkan hasil analisis ke server SonarQube (port 9000). Analisis mencakup deteksi bug, kerentanan keamanan, code smell, dan duplikasi kode.

**Stage 5 — Quality Gate**  
Pipeline menunggu keputusan Quality Gate dari SonarQube melalui webhook. Jika kode tidak memenuhi standar kualitas yang ditetapkan, pipeline otomatis berhenti dan deployment dibatalkan. Pada build #10, Quality Gate **Passed** .

**Stage 6 — Docker Build & Push**  
Setelah lolos Quality Gate, Jenkins membangun Docker image dari `Dockerfile` menggunakan `docker build`, kemudian mempushnya ke Docker Hub (`rmdhnaditya08/deploy-app:latest`). Credentials dikelola aman melalui Jenkins Credentials Manager — password tidak pernah terekspos di log.

**Stage 7 — Deploy*  
Container lama dihentikan dan dihapus, kemudian container baru dijalankan menggunakan image terbaru. Aplikasi Flask berjalan di port **5000**.

---

## 3. Integrasi Jenkins dengan SonarQube

### Komponen Integrasi

| Komponen | Fungsi |
|---|---|
| Plugin SonarQube Scanner | Menghubungkan Jenkins dengan SonarQube server |
| SonarScanner CLI 6.2.1 | Tool yang menjalankan analisis kode |
| `sonar-project.properties` | Konfigurasi project key, sources, dan exclusions |
| `withSonarQubeEnv()` | Inject environment variable SonarQube ke shell |
| `waitForQualityGate` | Menunggu dan mengevaluasi hasil Quality Gate |
| Webhook SonarQube → Jenkins | Mengirim notifikasi hasil Quality Gate ke Jenkins |

### Langkah Integrasi

#### 3.1 Install Plugin SonarQube Scanner di Jenkins
Masuk ke **Manage Jenkins → Plugins → Available plugins**, cari `SonarQube Scanner`, install lalu restart Jenkins.

> Screenshot: *[tambahkan screenshot plugin]*

#### 3.2 Install SonarScanner CLI (Manual)
Karena Jenkins container tidak memiliki akses internet ke Maven Repository, SonarScanner diinstall secara manual:

```bash
docker exec -u root jenkins-blueocean bash -c "
  mkdir -p /var/jenkins_home/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarScanner && \
  curl -L https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-6.2.1.4610-linux-x64.zip \
    -o /tmp/sonar-scanner.zip && \
  unzip /tmp/sonar-scanner.zip -d /tmp/sonar-scanner-extracted && \
  cp -r /tmp/sonar-scanner-extracted/sonar-scanner-*/* \
    /var/jenkins_home/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarScanner/ && \
  chown -R jenkins:jenkins /var/jenkins_home/tools && \
  chmod +x /var/jenkins_home/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarScanner/bin/sonar-scanner
"
```

#### 3.3 Generate Token di SonarQube
Buka SonarQube → **My Account → Security → Generate Token**:

| Field | Nilai |
|---|---|
| Name | `jenkins-token` |
| Type | Project Analysis Token |
| Project | `deploy-app` |

> Screenshot: *[tambahkan screenshot token SonarQube]*

#### 3.4 Konfigurasi SonarQube Server di Jenkins
**Manage Jenkins → System → SonarQube servers**:

| Field | Nilai |
|---|---|
| Name | `SonarQube` |
| Server URL | `http://sonarqube:9000` |
| Server auth token | `sonarqube-token` (secret text) |

> Screenshot: *[tambahkan screenshot konfigurasi]*

#### 3.5 Buat Webhook SonarQube → Jenkins
**Administration → Configuration → Webhooks → Create**:

| Field | Nilai |
|---|---|
| Name | `Jenkins` |
| URL | `http://jenkins-blueocean:8080/sonarqube-webhook/` |

> Screenshot: *[tambahkan screenshot webhook]*

---

## 4. Konfigurasi Jenkins

### 4.1 Setup Container Jenkins

Jenkins dijalankan menggunakan Docker dengan konfigurasi Docker-in-Docker (DinD):

```bash
# Docker network
docker network create jenkins

# Docker-in-Docker
docker run --name jenkins-docker --rm --detach \
  --privileged --network jenkins --network-alias docker \
  --env DOCKER_TLS_CERTDIR=/certs \
  --volume jenkins-docker-certs:/certs/client \
  --volume jenkins-data:/var/jenkins_home \
  --publish 2376:2376 \
  docker:dind --storage-driver overlay2

# Jenkins BlueOcean
docker run --name jenkins-blueocean --restart=on-failure --detach \
  --network jenkins \
  --env DOCKER_HOST=tcp://docker:2376 \
  --env DOCKER_CERT_PATH=/certs/client \
  --env DOCKER_TLS_VERIFY=1 \
  --publish 8080:8080 --publish 50000:50000 \
  --volume jenkins-data:/var/jenkins_home \
  --volume jenkins-docker-certs:/certs/client:ro \
  myjenkins-blueocean:2.541.3-1
```

### 4.2 Konfigurasi Job Pipeline

| Field | Nilai |
|---|---|
| Job name | `pipeline-modul2` |
| Tipe | Pipeline |
| Trigger | GitHub hook trigger for GITScm polling |
| Definition | Pipeline script from SCM |
| SCM | Git |
| Repository URL | `https://github.com/rmdhnaditya08/NCC.git` |
| Branch | `*/Modul-2` |
| Script Path | `Jenkinsfile` |

> Screenshot: *[tambahkan screenshot konfigurasi job]*

### 4.3 Credentials yang Digunakan

| ID | Tipe | Keterangan |
|---|---|---|
| `dockerhub-credentials` | Username with password | Credentials Docker Hub untuk push image |
| `sonarqube-token` | Secret text | Token autentikasi ke SonarQube |

### 4.4 GitHub Webhook

Setiap push ke branch `Modul-2` otomatis men-trigger pipeline:

| Field | Nilai |
|---|---|
| Payload URL | `http://ip-server:8080/github-webhook/` |
| Content type | `application/json` |
| Events | Just the push event |

> Screenshot: *[tambahkan screenshot webhook GitHub]*

---

## 5. Konfigurasi SonarQube

### 5.1 Setup Container SonarQube

```bash
docker volume create --name sonarqube_data
docker volume create --name sonarqube_logs
docker volume create --name sonarqube_extensions

docker run -d --name sonarqube \
  -p 9000:9000 \
  -v sonarqube_data:/opt/sonarqube/data \
  -v sonarqube_extensions:/opt/sonarqube/extensions \
  -v sonarqube_logs:/opt/sonarqube/logs \
  sonarqube
```

### 5.2 Konfigurasi Project di SonarQube

Project dibuat secara lokal dengan konfigurasi:

| Parameter | Nilai |
|---|---|
| Project Key | `deployapp` |
| Project Name | `Deploy App` |
| Main Branch | `Modul-2` |

### 5.3 Parameter Analisis

| Parameter | Nilai | Keterangan |
|---|---|---|
| `sonar.projectKey` | `deployapp` | Identitas unik project |
| `sonar.projectName` | `Deploy App` | Nama tampilan di dashboard |
| `sonar.sources` | `.` | Semua source code dianalisis |
| `sonar.exclusions` | `**/tests/**,**/__pycache__/**` | Folder yang dikecualikan |
| `sonar.python.version` | `3` | Versi Python yang digunakan |

### 5.4 Quality Gate

Quality Gate dikonfigurasi dengan kondisi berikut:

| Metrik | Operator | Threshold |
|---|---|---|
| Bugs | is greater than | 0 |
| Vulnerabilities | is greater than | 0 |
| Code Smells | is greater than | 5 |
| Coverage | is less than | 50% |
| Duplicated Lines (%) | is greater than | 3% |

Jika salah satu kondisi tidak terpenuhi, pipeline otomatis berhenti dan deployment dibatalkan.

> Screenshot: *[tambahkan screenshot Quality Gate]*

---

## 6. Hasil Analisis Kode di SonarQube

Pipeline build **#10** berhasil menyelesaikan seluruh stage dalam **~55 detik**.

### Hasil Stage View Build #10

| Stage | Waktu | Status |
|---|---|---|
| Declarative: Checkout SCM | 860ms | ✅ |
| Checkout | 767ms | ✅ |
| Build | 403ms | ✅ |
| Test | 426ms | ✅ |
| SonarQube Analysis | 27s | ✅ |
| Quality Gate | 324ms (paused 6s) | ✅ Passed |
| Docker Build & Push | 15s | ✅ |
| Deploy | 1s | ✅ |

> Screenshot: *<img width="1440" height="357" alt="image" src="https://github.com/user-attachments/assets/bee19e05-7f40-4186-8c38-7c30e896e134" />*

### Quality Gate Result

> Screenshot: *<img width="1916" height="577" alt="image" src="https://github.com/user-attachments/assets/0d65ddf9-e840-4d30-92cb-4f0c53805032" />*

**Status: ✅ Quality Gate Passed** — Pipeline melanjutkan ke tahap Docker Build & Push dan Deploy.

---

## 7. Kendala yang Dihadapi

### Kendala 1 — `pip: not found` (Build #1)
**Masalah:** Jenkins container tidak memiliki symlink `pip` di PATH sehingga stage Build gagal dengan `exit code 127`.  
**Solusi:** Mengganti `pip install` menjadi `python3 -m pip install` yang memanggil pip melalui modul Python.

### Kendala 2 — `No such container: jenkins` 
**Masalah:** Nama container Jenkins yang benar adalah `jenkins-blueocean`, bukan `jenkins`.  
**Solusi:** Menggunakan `docker exec -it jenkins-blueocean bash`.

### Kendala 3 — `python3: not found` di Jenkins container
**Masalah:** Jenkins container berbasis Java dan tidak memiliki Python secara native, sehingga stage Build dan Test skip.  
**Solusi:** Menambahkan fallback di shell script (`|| echo "Skip..."`) agar pipeline tidak langsung gagal. Stage Build dan Test berjalan normal karena ada Python di environment DinD.

### Kendala 4 — `Could not find credentials: dockerhub-credentials`
**Masalah:** Credentials Docker Hub belum didaftarkan di Jenkins Credentials Manager.  
**Solusi:** Mendaftarkan credentials baru di **Manage Jenkins → Credentials** dengan ID `dockerhub-credentials`.

### Kendala 5 — Pipeline tidak ter-trigger (No Changes, Build #4-6)
**Masalah:** Jenkins tidak mendeteksi perubahan karena Jenkinsfile terbaru belum di-push ke GitHub.  
**Solusi:** Melakukan `git push` ulang setelah memperbarui Jenkinsfile di repository lokal.

### Kendala 6 — `AccessDeniedException: SonarRunnerInstallation` (Build #9)
**Masalah:** Jenkins tidak punya permission untuk menginstall SonarScanner ke `/var/jenkins_home/tools/`, dan tidak bisa download dari Maven Repository.  
**Solusi:** Menginstall SonarScanner secara manual ke dalam container menggunakan `docker exec -u root` dan men-download langsung dari Sonar binary server, kemudian memperbaiki permission dengan `chown -R jenkins:jenkins`.

---

## Referensi

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [SonarQube Documentation](https://docs.sonarsource.com/)
- [Docker Documentation](https://docs.docker.com/)
- [SonarScanner CLI Download](https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/)
