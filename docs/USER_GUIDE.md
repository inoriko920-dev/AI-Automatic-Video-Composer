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

Saat render, AAVC mencari FFmpeg pada slot app-local tersebut terlebih dahulu, lalu pada system `PATH`. Jika FFmpeg tidak ditemukan, render dihentikan dengan pesan error; aplikasi tidak mengunduh binary secara otomatis.

## 3. Input proyek utama

Alur proyek AAVC dirancang untuk video naratif/infografik berbasis scene.

Input utama yang digunakan oleh engine adalah:

- Scene DOCX dengan daftar scene dan mapping aset.
- Aset gambar canonical dengan pola ID `Axxx`, misalnya `A001.png`, `A002.png`, dan seterusnya.
- Media pendukung sesuai proyek, seperti narasi/audio dan subtitle ketika workflow yang digunakan membutuhkannya.

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

Aset yang belum ditemukan tetap dapat ditangani melalui validation/relink workflow. Narasi dan subtitle tidak dipaksa pada flow pembuatan awal dan dapat ditambahkan setelah project aktif melalui **Impor Media**.

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

Pada source `main` setelah maintenance project-session, new-project-session, real-export-render, real-validation-center, supported-media-import, live-subtitle-source, dan live-editor-overview, kontrol berikut memiliki perilaku eksplisit:

- **Baru** → membuka flow Proyek Baru; DOCX + Folder Aset dipakai untuk membangun dan menyimpan sesi canonical `.aavcproj`.
- **Buka** → membuka file picker `.aavcproj`, memuat project, lalu masuk editor.
- **Simpan** → menyimpan current `ProjectState` ke path project aktif secara atomic melalui repository.
- **Undo** → memundurkan perubahan model pada `ProjectHistory` jika tersedia.
- **Redo** → mengulangi perubahan model pada `ProjectHistory` jika tersedia.
- **Impor Media** → memasukkan subtitle SRT atau audio narasi yang didukung ke project aktif melalui history.
- **Tambah Teks** → membaca `subtitle_source` project aktif dan menampilkan cue/timing SRT yang sebenarnya.
- **Validasi** → menghitung issue dari `ProjectState` aktif dan membuka Validation Center dengan data nyata.
- **Ekspor Video** → membuka pengaturan ekspor; **Mulai Render** menjalankan render pipeline FFmpeg nyata untuk project aktif.
- **Keluar** → menutup aplikasi.

Jika **Simpan** dipilih tanpa project aktif, aplikasi memberi penjelasan bahwa penyimpanan belum tersedia untuk sesi tersebut. Undo/Redo yang tidak memiliki aksi juga memberi feedback dan tidak merusak state project.

## 7. Editor Overview dari project aktif

Pada source `main` setelah maintenance live-editor-overview, editor yang dibuka setelah **Buat/Buka Project** tidak lagi memakai daftar Scene/Aset demo sebagai data project.

Bagian yang sekarang berasal dari `ProjectState` aktif:

- judul project;
- resolusi dan FPS;
- durasi total dan jumlah scene;
- jumlah aset READY dan belum READY;
- nama file narasi dan subtitle bila sudah diimpor;
- seluruh daftar Scene beserta nomor, mode SINGLE/DOUBLE, durasi, dan canonical Asset ID;
- seluruh asset binding beserta status, nama file, dan source quote.

Aset yang belum ditemukan ditampilkan sebagai `MISSING`/belum READY, bukan thumbnail contoh. Overview dibangun ulang setelah Create/Open dan setelah perubahan model melalui Undo/Redo, Relink, atau Impor Media.

**Pratinjau project nyata dan timeline editing belum terhubung pada tahap ini.** Pada live overview, area preview menampilkan penjelasan bahwa preview belum aktif dan timeline dinonaktifkan. Hal ini sengaja dilakukan agar data demo lama tidak tampak seperti hasil project aktif. Fixture editor lama tetap dipertahankan hanya untuk no-session STEP09 visual-reference capture.

## 8. Validasi project dan relink aset

Pada source `main` setelah maintenance real-validation-center, tombol validasi tidak lagi mengandalkan contoh statis ketika ada project aktif.

Application service `validate_project()` saat ini mendeteksi issue yang memang didukung engine, antara lain:

- asset yang belum `READY` / file canonical belum terikat dengan benar;
- durasi scene yang terlalu pendek menurut rule validation saat ini.

Badge validasi pada toolbar mengikuti state project aktif:

- **merah** jika ada error;
- **kuning** jika tidak ada error tetapi ada warning;
- **hijau / Validasi OK** jika tidak ada issue.

Di Validation Center:

1. Ringkasan Error/Peringatan dihitung dari hasil validasi project aktif.
2. Issue dikelompokkan ke kategori Project, Media, dan Scene; kategori AI/Render tetap 0 jika engine belum menghasilkan issue untuk kategori tersebut.
3. **Validasi Ulang** membaca `ProjectState` terbaru dari session, bukan memakai data lama.
4. Untuk issue asset belum READY, tombol **Relink** membuka file picker gambar pengganti.
5. Relink dijalankan melalui `RelinkAsset` di `ProjectHistory`, sehingga dapat di-**Undo**.
6. Relink mengubah state di memori; tekan **Simpan** untuk menulis perubahan ke `.aavcproj`.

Fixture `2 Error, 3 Peringatan` yang lama hanya dipertahankan sebagai fallback tanpa sesi untuk frozen STEP09 visual-reference capture. Pada penggunaan normal, toolbar editor tidak tersedia dari Home/New Project sebelum ada project aktif.

## 9. Ekspor video nyata pada source main

Pada source `main` setelah maintenance real-export-render, dialog ekspor meneruskan pilihan yang didukung ke render engine:

- **MP4 (H.264)** → `libx264`.
- **MP4 (H.265)** → `libx265`.
- Preset encoder yang tersedia pada dialog diteruskan ke FFmpeg.
- Resolusi **1920×1080**, **2560×1440**, atau **3840×2160** benar-benar mengubah frame render.
- Frame rate **30 fps** atau **60 fps** benar-benar diteruskan ke render plan/FFmpeg.
- Slider kualitas dipetakan ke CRF pada rentang yang aman untuk UI saat ini.
- Pilihan ketajaman mengubah `sharpen_amount` pada render-quality settings.
- Jika **Sertakan Subtitle** dipilih dan project memiliki `subtitle_source`, SRT dikompilasi menjadi ASS lalu dibakar ke video.
- Jika **Tanpa Subtitle** dipilih, subtitle tidak dimasukkan ke render tersebut.
- Jika project memiliki `narration_audio`, audio tersebut ikut diteruskan ke `RenderPlan`.

Sebelum FFmpeg dijalankan, AAVC membangun `RenderPlan` dan menjalankan preflight. Asset yang belum READY, narasi yang hilang, subtitle hasil kompilasi yang hilang, resolusi/FPS tidak valid, atau error render lain akan menghentikan proses dan ditampilkan sebagai error UI.

Render UI pertama ini bersifat **synchronous**: aplikasi menampilkan wait cursor/status selama FFmpeg bekerja dan tidak menampilkan progress persentase palsu. **GPU acceleration** dan **Pengaturan Lanjutan** sengaja dinonaktifkan pada dialog karena pipeline tersebut belum diimplementasikan; jangan menganggap keduanya sudah berfungsi.

Jika tidak ada project aktif, **Mulai Render** ditolak dan pengguna diminta membuat atau membuka project terlebih dahulu.

## 10. Impor Media yang didukung

Pada source `main` setelah maintenance supported-media-import, tombol **Impor Media** menggunakan file picker nyata dan hanya menerima tipe yang sudah terhubung sampai render pipeline.

Format yang didukung:

- subtitle: `.srt`;
- audio narasi: `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg`.

AAVC menentukan peran media dari ekstensi file:

- `.srt` disimpan sebagai `subtitle_source`;
- format audio yang didukung disimpan sebagai `narration_audio`.

Perubahan dijalankan melalui `ProjectSession.execute()`, sehingga import media masuk `ProjectHistory` dan dapat di-**Undo/Redo**. Path disimpan sebagai absolute resolved path. Setelah import berhasil, tekan **Simpan** untuk menulis perubahan ke file `.aavcproj`.

Format lain ditolak dengan pesan yang jelas. `background_source` belum diaktifkan melalui tombol ini karena render pipeline saat ini belum menggunakannya. Tombol **Rekam Narasi** juga belum dianggap sebagai import audio; perekaman mikrofon membutuhkan recording engine tersendiri.

## 11. Melihat subtitle SRT project

Pada source `main` setelah maintenance live-subtitle-source, tombol **Tambah Teks** tidak lagi memakai cue demo ketika ada project aktif.

1. Impor `.srt` melalui **Impor Media**.
2. Tekan **Tambah Teks**.
3. AAVC membaca file `subtitle_source` dari disk melalui parser SRT yang sama dengan pipeline subtitle.
4. Daftar menampilkan jumlah cue, timing milidetik, dan teks yang sebenarnya.
5. Cue yang mulai sebelum cue sebelumnya selesai diberi tanda overlap `⚠`.
6. Memilih cue menampilkan teks, waktu mulai, dan waktu selesai cue tersebut.
7. **Muat Ulang SRT** membaca ulang source dari disk, sehingga perubahan eksternal pada SRT dapat ditampilkan tanpa membuka ulang project.

Pada tahap ini panel detail bersifat **read-only**. Tombol **Tambah Cue**, **Pisah Cue**, dan **Gabung** sengaja dinonaktifkan karena repo belum memiliki writer/history model yang aman untuk mutasi isi SRT. Ini mencegah UI terlihat bekerja padahal perubahan tidak dapat dipersist dengan benar.

Jika project belum memiliki `subtitle_source`, **Tambah Teks** meminta pengguna mengimpor SRT terlebih dahulu. Jika file source hilang atau tidak dapat diparse, aplikasi menampilkan error dan tidak menggantinya dengan data demo. Fixture subtitle lama tetap dipakai hanya untuk no-session STEP09 visual-reference capture.

## 12. Kontrol yang belum terhubung penuh

Pada source `main`, **Rekam Narasi** masih belum memiliki recording engine dan tetap memberi pesan **Fitur belum terhubung** tanpa mengubah project. Preview project nyata, timeline editing, beberapa menu placeholder, dan Bantuan Cepat juga belum merupakan workflow final.

Catatan penting: maintenance project-session/new-project-session/real-export-render/real-validation-center/supported-media-import/live-subtitle-source/live-editor-overview berada setelah frozen release `v0.1.1`. Binary `v0.1.1` yang sudah dipublikasikan tidak otomatis berubah ketika `main` berubah.

## 13. Sebelum ekspor

Sebelum menjalankan ekspor, periksa minimal:

- Scene DOCX dapat dibaca.
- Asset ID yang diminta tersedia dan nama canonical-nya benar.
- Media/audio yang dibutuhkan proyek tersedia.
- Badge/Validation Center tidak menunjukkan asset missing yang belum diperbaiki.
- FFmpeg tersedia pada `tools/ffmpeg/` atau system `PATH`.
- Subtitle source valid jika burn-in subtitle digunakan.
- Pengaturan resolusi, FPS, codec, kualitas, dan ketajaman sesuai kebutuhan.

Gunakan tombol **Validasi** untuk meninjau masalah yang dapat dideteksi sebelum render.

## 14. Jika proyek bermasalah

Jangan menghapus file proyek asli ketika melakukan recovery.

Repo menyediakan mekanisme versioned project state dan recovery snapshot. Untuk kebijakan backup/recovery yang lebih teknis, lihat `BACKUP_AND_RECOVERY.md`.

Jika asset berpindah folder, gunakan workflow relink/validation daripada mengganti ID canonical secara acak.

## 15. Untuk developer

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

## 16. Batas dokumen ini

Panduan ini menjelaskan kemampuan yang dapat dibuktikan dari source dan release metadata repo. Ia tidak menjanjikan bahwa semua kontrol visual telah terhubung end-to-end pada setiap binary historis.

Untuk status release lihat `README.md` dan `RELEASE_NOTES_0.1.1.md`. Untuk kebijakan maintenance lihat `MAINTENANCE.md`. Untuk detail arsitektur dan factory evidence, lihat dokumen lain di `docs/` dan file STEP status di root repo.
