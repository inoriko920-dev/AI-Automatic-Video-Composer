# Panduan Pengguna — AI Automatic Video Composer

Panduan ini menjelaskan cara mulai memakai AI Automatic Video Composer (AAVC) secara praktis tanpa perlu membaca dokumen Software Factory internal.

> Status rilis: build publik stabil yang saat ini tercatat adalah `v0.1.1`. Branch `main` dapat berisi maintenance setelah rilis tersebut. Karena artefak `v0.1.1` bersifat frozen, perubahan maintenance di `main` baru masuk ke binary jika dibuat rilis/build baru.

## 1. Menjalankan versi portable Windows

1. Unduh ZIP Windows portable dari GitHub Release resmi.
2. Ekstrak seluruh isi ZIP ke folder biasa. Jangan menjalankan aplikasi langsung dari dalam ZIP.
3. Pastikan struktur folder portable tetap utuh.
4. Jalankan `AI Automatic Video Composer.exe`.

AAVC menggunakan model distribusi portable onedir. File pendukung di dalam folder hasil ekstrak merupakan bagian dari aplikasi dan jangan dipindahkan satu per satu.

## 2. FFmpeg dan ffprobe

AAVC memakai FFmpeg/ffprobe untuk pipeline media dan render, tetapi binary FFmpeg tidak didistribusikan oleh proyek ini.

Slot aplikasi untuk binary tersebut adalah:

```text
tools/ffmpeg/
```

pada folder portable yang sama dengan aplikasi. Gunakan binary FFmpeg/ffprobe yang Anda peroleh dari sumber yang Anda pilih sendiri dan pastikan lisensinya sesuai dengan penggunaan Anda.

Jika FFmpeg/ffprobe tidak tersedia saat operasi media membutuhkannya, proses terkait tidak dapat dijalankan dengan benar.

## 3. Input proyek utama

Alur proyek AAVC dirancang untuk video naratif/infografik berbasis scene.

Input utama yang digunakan oleh engine adalah:

- Scene DOCX dengan daftar scene dan mapping aset.
- Aset gambar canonical dengan pola ID `Axxx`, misalnya `A001.png`, `A002.png`, dan seterusnya.
- Media pendukung sesuai proyek, seperti narasi/audio ketika workflow yang digunakan membutuhkannya.

Pada layar Proyek Baru, tahap awal meminta **Scene DOCX**. UI menjelaskan bahwa setiap scene harus mengikuti kontrak Prompt 1 dan memiliki 1 atau 2 Asset ID canonical `Axxx`.

## 4. Memulai proyek dari UI

Dari layar awal:

1. Pilih **Proyek Baru → Mulai**.
2. Pada layar **Pilih Scene DOCX**, klik **Pilih DOCX**.
3. Pilih file `.docx` yang sesuai kontrak scene AAVC.
4. Setelah file dipilih, tombol **Lanjut** menjadi aktif.
5. Lanjutkan ke editor untuk memeriksa scene, visual, subtitle, animasi, validasi, dan pengaturan ekspor yang tersedia pada build yang sedang digunakan.

Menu **Buka Proyek** membawa pengguna ke shell editor. Format project state internal menggunakan ekstensi `.aavcproj` dan memiliki versioned schema di engine.

## 5. Bagian editor yang tersedia

Repo saat ini memiliki implementasi untuk beberapa area penting berikut:

- layout scene SINGLE dan DOUBLE;
- scene/asset binding berbasis canonical ID;
- subtitle styling dan kompilasi ASS;
- registry animasi visual;
- random animation deterministik;
- validation dan asset relink workflow;
- render pipeline FFmpeg;
- profil kualitas render Documentary Crisp;
- project-state persistence, recovery snapshot, serta engine undo/redo;
- boundary provider AI termasuk integrasi Gemini dan fondasi credential/key pool.

Keberadaan engine tidak selalu berarti setiap tombol pada shell UI sudah terhubung penuh ke sesi proyek pada binary tertentu.

## 6. Kontrol yang sudah mempunyai route UI

Pada source `main` saat panduan ini dibuat, route berikut sudah mempunyai perilaku UI eksplisit:

- **Baru** → membuka flow Proyek Baru.
- **Buka** → membuka editor.
- **Tambah Teks** → membuka area subtitle.
- **Validasi** → membuka Validation Center.
- **Ekspor Video** → membuka pengaturan ekspor.
- **Keluar** → menutup aplikasi.

## 7. Kontrol yang belum terhubung penuh

Pada source `main`, kontrol seperti **Simpan**, **Undo**, **Redo**, **Impor Media**, dan **Rekam Narasi** tidak lagi diam tanpa penjelasan. Jika integrasi sesi proyek belum tersedia pada shell tersebut, aplikasi memberi pesan **Fitur belum terhubung** dan menegaskan bahwa tidak ada perubahan proyek yang dilakukan.

Catatan penting: maintenance UI ini berada setelah frozen release `v0.1.1`. Binary `v0.1.1` yang sudah dipublikasikan tidak otomatis berubah ketika `main` berubah.

## 8. Sebelum ekspor

Sebelum menjalankan ekspor, periksa minimal:

- Scene DOCX dapat dibaca.
- Asset ID yang diminta tersedia dan nama canonical-nya benar.
- Media/audio yang dibutuhkan proyek tersedia.
- Tidak ada asset missing pada Validation Center.
- FFmpeg/ffprobe tersedia untuk operasi yang membutuhkannya.
- Pengaturan subtitle dan animasi sesuai kebutuhan.

Gunakan tombol **Validasi** untuk meninjau masalah yang dapat dideteksi sebelum render.

## 9. Jika proyek bermasalah

Jangan menghapus file proyek asli ketika melakukan recovery.

Repo menyediakan mekanisme versioned project state dan recovery snapshot. Untuk kebijakan backup/recovery yang lebih teknis, lihat `BACKUP_AND_RECOVERY.md`.

Jika asset berpindah folder, gunakan workflow relink/validation daripada mengganti ID canonical secara acak.

## 10. Untuk developer

Baseline pengembangan aktif:

- Python 3.12.10 untuk toolchain Windows yang dipin repo;
- PySide6 / Qt Widgets;
- FFmpeg / ffprobe sebagai external media dependency;
- PyInstaller onedir;
- CI Windows dengan compile, Ruff, strict mypy, pytest, dan verifikasi screenshot STEP09.

Perintah PowerShell utama:

```powershell
./scripts/dev.ps1
./scripts/test.ps1
./scripts/package.ps1
./scripts/verify_portable.ps1
```

## 11. Batas dokumen ini

Panduan ini menjelaskan kemampuan yang dapat dibuktikan dari source dan release metadata repo. Ia tidak menjanjikan bahwa semua kontrol visual telah terhubung end-to-end pada setiap binary historis.

Untuk status release lihat `README.md` dan `RELEASE_NOTES_0.1.1.md`. Untuk kebijakan maintenance lihat `MAINTENANCE.md`. Untuk detail arsitektur dan factory evidence, lihat dokumen lain di `docs/` dan file STEP status di root repo.
