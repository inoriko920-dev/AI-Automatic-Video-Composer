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

## 4. Memulai atau membuka proyek dari UI

Untuk membuat proyek baru pada source `main` setelah maintenance new-project-session:

1. Pilih **Proyek Baru → Mulai**.
2. Pada layar **Pilih Scene DOCX**, klik **Pilih DOCX**.
3. Pilih file `.docx` yang sesuai kontrak scene AAVC.
4. Setelah file dipilih, tombol **Lanjut** menjadi aktif.
5. Klik **Lanjut**, lalu pilih **Folder Aset** yang berisi file canonical `A001.png`, `A002.png`, dan seterusnya.
6. AAVC membaca DOCX dan membangun `ProjectState` serta asset binding dari folder yang dipilih.
7. Pilih lokasi penyimpanan project `.aavcproj`.
8. File project disimpan terlebih dahulu; hanya setelah penyimpanan berhasil project baru menjadi sesi aktif dan editor dibuka.

Jika pengguna membatalkan pemilihan Folder Aset atau lokasi penyimpanan, sesi project yang sebelumnya aktif tidak diganti. Jika penyimpanan project baru gagal, sesi lama juga tetap dipertahankan.

Aset yang belum ditemukan tetap dapat ditangani melalui validation/relink workflow. Narasi, subtitle, dan media tambahan belum dipaksa pada flow pembuatan awal ini dan dapat ditambahkan melalui workflow yang tersedia pada build terkait.

Untuk membuka project state yang sudah ada:

1. Pilih **Buka Proyek** atau tombol **Buka**.
2. Pilih file `.aavcproj`.
3. AAVC memuat file melalui `ProjectRepository` dan membuat sesi aktif baru hanya setelah load berhasil.
4. Jika file rusak/tidak valid, project aktif sebelumnya tetap dipertahankan.
5. Setelah berhasil dibuka, judul window mengikuti nama project dan editor ditampilkan.

Format project state internal menggunakan ekstensi `.aavcproj` dan memiliki versioned schema di engine.

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

## 6. Kontrol yang sudah mempunyai perilaku UI nyata di source main

Pada source `main` setelah maintenance project-session dan new-project-session, kontrol berikut memiliki perilaku eksplisit:

- **Baru** → membuka flow Proyek Baru; DOCX + Folder Aset dipakai untuk membangun dan menyimpan sesi canonical `.aavcproj`.
- **Buka** → membuka file picker `.aavcproj`, memuat project, lalu masuk editor.
- **Simpan** → menyimpan current `ProjectState` ke path project aktif secara atomic melalui repository.
- **Undo** → memundurkan perubahan model pada `ProjectHistory` jika tersedia.
- **Redo** → mengulangi perubahan model pada `ProjectHistory` jika tersedia.
- **Tambah Teks** → membuka area subtitle.
- **Validasi** → membuka Validation Center.
- **Ekspor Video** → membuka pengaturan ekspor.
- **Keluar** → menutup aplikasi.

Jika **Simpan** dipilih tanpa project aktif, aplikasi memberi penjelasan bahwa penyimpanan belum tersedia untuk sesi tersebut. Undo/Redo yang tidak memiliki aksi juga memberi feedback dan tidak merusak state project.

## 7. Kontrol yang belum terhubung penuh

Pada source `main`, kontrol seperti **Impor Media** dan **Rekam Narasi** belum memiliki integrasi sesi penuh dari shell utama. Aplikasi tidak lagi diam tanpa penjelasan; ketika fitur belum tersedia, pengguna mendapat pesan **Fitur belum terhubung** dan tidak ada perubahan project yang dilakukan.

Beberapa menu placeholder dan Bantuan Cepat juga masih berfungsi sebagai shell UI, bukan workflow final.

Catatan penting: maintenance UI/project-session ini berada setelah frozen release `v0.1.1`. Binary `v0.1.1` yang sudah dipublikasikan tidak otomatis berubah ketika `main` berubah.

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
