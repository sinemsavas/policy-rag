# Policy RAG — GitHub İşlem Geçmişi

**Son güncelleme:** 28.10.2026 · **Repo:** [sinemsavas/policy-rag](https://github.com/sinemsavas/policy-rag)

Bu kayıt ilk çalışan commit'i, birleştirilmiş PR #1–#5'i, çalışma dallarını, değişen dosyaları ve erişilen bütün mevcut Actions koşularını açıklar. Kod geçmişinin incelenen son noktası `43b72123f52e9a88a3381ed656d0508f4b28c3e3` commit'idir. Bu dokümantasyonu ekleyen PR, aşağıdaki yeni çalışma bölümünde ayrıca izlenir.

Tarihler GitHub API kayıtlarından alınmış ve Europe/Berlin'e çevrilmiştir: 24 Ekim CEST (UTC+2), 26 ve 28 Ekim CET (UTC+1). Yerel temel 23 Ekim'de hazırlanmıştı; ilk GitHub commit'i 24 Ekim'dir.

## 1. Kanıtın kapsamı ve push kavramı

Commit nesnesi, PR ve Actions kayıtları GitHub'dan doğrulandı. Push komutlarının terminal geçmişi Git geçmişinde tutulmaz. Aşağıdaki push tablosu, görülen `push` tetikli CI olaylarını gösterir; terminalde geçmişte yazılmış her komutun birebir dökümü değildir. İlk aktarımda workflow henüz bulunmadığından o push için CI kaydı yoktur. Bir push birden fazla commit taşıyabilir; bir commit de farklı dallarda tekrar görünebilir.

PR #1–#5'in her biri main üzerinde tek sonuç commit'i oluşturmuştur. Çalışma commit'i ile squash sonucu farklı SHA taşır. Dalların başlangıç commit'leri üzerinde de push CI kayıtları vardır; bu kayıtlar yeni özellik commit'i olarak sayılmaz.

## 2. Main dalındaki bütün başlangıç commit'leri

| Tarih / saat | Commit | Mesajın ilk satırı | Karşılığı |
| --- | --- | --- | --- |
| 24.10.2026 16:34:31 CEST | [`a86723d`](https://github.com/sinemsavas/policy-rag/commit/a86723dc6a4f621516c9e17b666fbf2b26e18738) | feat: bootstrap containerized FastAPI and pgvector | İlk çalışan projenin doğrudan aktarımı |
| 24.10.2026 16:56:03 CEST | [`966e922`](https://github.com/sinemsavas/policy-rag/commit/966e92222debf2712697b9435c5e5b8e17ba359b) | chore: document foundation and add health smoke CI (#1) | [PR #1](https://github.com/sinemsavas/policy-rag/pull/1) |
| 26.10.2026 16:34:07 CET | [`4fc5695`](https://github.com/sinemsavas/policy-rag/commit/4fc5695c1a9e3312b83d94ed201bae24d2828e37) | docs: focus README on project setup and scope (#2) | [PR #2](https://github.com/sinemsavas/policy-rag/pull/2) |
| 26.10.2026 16:53:16 CET | [`b43d6ff`](https://github.com/sinemsavas/policy-rag/commit/b43d6ff581f7cd4f16cc4ff4822315fbcbbb8174) | feat: add reviewed NFIP corpus and verified downloads (#3) | [PR #3](https://github.com/sinemsavas/policy-rag/pull/3) |
| 26.10.2026 17:26:36 CET | [`b6e02ff`](https://github.com/sinemsavas/policy-rag/commit/b6e02ff76c363e8d4f7d1ac5d728fe024c303f71) | feat: extract policy text with original page metadata (#4) | [PR #4](https://github.com/sinemsavas/policy-rag/pull/4) |
| 26.10.2026 18:01:52 CET | [`43b7212`](https://github.com/sinemsavas/policy-rag/commit/43b72123f52e9a88a3381ed656d0508f4b28c3e3) | feat: add configurable page-contained chunking (#5) | [PR #5](https://github.com/sinemsavas/policy-rag/pull/5) |

İlk commit'te dokuz dosya yer aldı: `main.py`, `pyproject.toml`, `uv.lock`, `compose.yaml`, `init.sql`, `Dockerfile`, `.dockerignore`, `.gitignore`, `README.md`. Gerçek `.env` bu dosyalar arasında yoktur. README başlangıçta boştu; kullanılabilir açıklama PR #1'de geldi.

## 3. Dal, çalışma commit'i ve main sonucu eşleştirmesi

| PR | Çalışma dalı | Çalışma commit'i | Main sonucu | Birleştirme zamanı |
| --- | --- | --- | --- | --- |
| [#1](https://github.com/sinemsavas/policy-rag/pull/1) | `chore/foundation-docs-ci` | [`e232914`](https://github.com/sinemsavas/policy-rag/commit/e232914623430f39a8bdfec59857f6ae84d20d29) | [`966e922`](https://github.com/sinemsavas/policy-rag/commit/966e92222debf2712697b9435c5e5b8e17ba359b) | 24.10.2026 16:56:03 CEST |
| [#2](https://github.com/sinemsavas/policy-rag/pull/2) | `docs/readme-project-focus` | [`d779a02`](https://github.com/sinemsavas/policy-rag/commit/d779a02397666e8f0408a92b46a6c9304b3ef5ea) | [`4fc5695`](https://github.com/sinemsavas/policy-rag/commit/4fc5695c1a9e3312b83d94ed201bae24d2828e37) | 26.10.2026 16:34:07 CET |
| [#3](https://github.com/sinemsavas/policy-rag/pull/3) | `feat/public-corpus-acquisition` | [`9364afa`](https://github.com/sinemsavas/policy-rag/commit/9364afaffa6c4f84827536c2803b048d15cf9a58) | [`b43d6ff`](https://github.com/sinemsavas/policy-rag/commit/b43d6ff581f7cd4f16cc4ff4822315fbcbbb8174) | 26.10.2026 16:53:16 CET |
| [#4](https://github.com/sinemsavas/policy-rag/pull/4) | `feat/page-preserving-extraction` | [`6beed00`](https://github.com/sinemsavas/policy-rag/commit/6beed00502accfaf8530c63fb068fe116886541d) | [`b6e02ff`](https://github.com/sinemsavas/policy-rag/commit/b6e02ff76c363e8d4f7d1ac5d728fe024c303f71) | 26.10.2026 17:26:37 CET |
| [#5](https://github.com/sinemsavas/policy-rag/pull/5) | `feat/page-aware-chunking` | [`d1f3c27`](https://github.com/sinemsavas/policy-rag/commit/d1f3c276f78c9d391c1c1907cca66aa2b8fde0b8) | [`43b7212`](https://github.com/sinemsavas/policy-rag/commit/43b72123f52e9a88a3381ed656d0508f4b28c3e3) | 26.10.2026 18:01:53 CET |

Dalların adları tarihsel çalışma kimlikleridir; burada listelenmeleri bugün hâlâ açık dal oldukları anlamına gelmez. İncelenen PR #1–#5'in hepsi birleştirilmiş ve kapalıdır.

## 4. Her PR'da ne yaptık?

### PR #1 — Document setup and add a database-independent health smoke test

[Pull request](https://github.com/sinemsavas/policy-rag/pull/1) · Açılış: 24.10.2026 16:52:05 CEST · Birleştirme: 24.10.2026 16:56:03 CEST

**Amaç:** Boş README'nin yerine çalıştırılabilir kurulum anlatımı, gereksinim sözleşmesi, ayar örneği ve otomatik kontrol eklemek.

**Sonuç:** Gerçek .env repoya alınmadan başkasının kurulum yapabilmesi sağlandı. /health'in veritabanından bağımsız olması bir testle güvenceye alındı. CI kilitli bağımlılıkları kurup test çalıştırmaya başladı.

| Dosya | İşlem | Açıklama |
| --- | --- | --- |
| [.env.example](../.env.example) | Eklendi | Gerekli üç ortam değişkenini boş değerlerle gösteren yeni kurulum örneği. |
| [.github/workflows/ci.yml](../.github/workflows/ci.yml) | Eklendi | Push ve PR olaylarında kilitli ortamı kurup pytest çalıştıran CI. |
| [.gitignore](../.gitignore) | Güncellendi | Gerçek ayarlar, önbellekler ve ilgili yerel veri çıktıları için Git dışlama kuralları. |
| [README.md](../README.md) | Güncellendi | Kurulum, kullanım, mevcut durum ve ilgili teknik notlara bağlantılar. |
| [SPEC.md](../SPEC.md) | Eklendi | Aşamanın numaralı kabul kriterleri ve doğrulama gereksinimleri. |
| [pyproject.toml](../pyproject.toml) | Güncellendi | Geliştirme veya çalışma bağımlılıklarının tanımı. |
| [tests/test_health.py](../tests/test_health.py) | Eklendi | HTTP 200, cevap sözleşmesi ve DB bağlantısı açmama testi. |
| [uv.lock](../uv.lock) | Güncellendi | Yeni bağımlılıklarla uyumlu kilitli paket çözümü. |

**Doğrulama:** Yerel sonuç 1 passed. Mevcut uygulama paketlerinin kilitli sürümleri korundu; pytest/httpx geliştirme grubuna eklendi. Push, PR ve main CI başarıları aşağıdaki kayıtlardadır.

**Çalışma commit'i:**

- [`e232914`](https://github.com/sinemsavas/policy-rag/commit/e232914623430f39a8bdfec59857f6ae84d20d29): `chore: document foundation and add health smoke CI` — 24.10.2026 16:51:54 CEST.

**Main commit'i:** [`966e922`](https://github.com/sinemsavas/policy-rag/commit/966e92222debf2712697b9435c5e5b8e17ba359b).

| Kontrol | Actions kaydı | Gözlenen sonuç |
| --- | --- | --- |
| Çalışma dalı push | [40104407875](https://github.com/sinemsavas/policy-rag/actions/runs/40104407875) | `success` |
| PR | [40104411226](https://github.com/sinemsavas/policy-rag/actions/runs/40104411226) | `success` |
| Main push | [40104691468](https://github.com/sinemsavas/policy-rag/actions/runs/40104691468) | `success` |

### PR #2 — Keep the README focused on project setup and scope

[Pull request](https://github.com/sinemsavas/policy-rag/pull/2) · Açılış: 26.10.2026 16:33:08 CET · Birleştirme: 26.10.2026 16:34:07 CET

**Amaç:** README'yi projenin kurulumu, mimarisi ve kapsamına odaklanacak biçimde sadeleştirmek.

**Sonuç:** Yalnız README metni değiştirildi. Uygulama kodu, bağımlılıklar ve workflow aynı kaldı.

| Dosya | İşlem | Açıklama |
| --- | --- | --- |
| [README.md](../README.md) | Güncellendi | Kurulum, kullanım, mevcut durum ve ilgili teknik notlara bağlantılar. |

**Doğrulama:** Dokümantasyon farkı incelendi. Otomatik iş akışı da push, PR ve main için başarılı oldu; paket halen ilk sağlık testini içeriyordu.

**Çalışma commit'i:**

- [`d779a02`](https://github.com/sinemsavas/policy-rag/commit/d779a02397666e8f0408a92b46a6c9304b3ef5ea): `docs: focus README on project setup and scope` — 26.10.2026 16:32:41 CET.

**Main commit'i:** [`4fc5695`](https://github.com/sinemsavas/policy-rag/commit/4fc5695c1a9e3312b83d94ed201bae24d2828e37).

| Kontrol | Actions kaydı | Gözlenen sonuç |
| --- | --- | --- |
| Çalışma dalı push | [40350399843](https://github.com/sinemsavas/policy-rag/actions/runs/40350399843) | `success` |
| PR | [40350440749](https://github.com/sinemsavas/policy-rag/actions/runs/40350440749) | `success` |
| Main push | [40350601018](https://github.com/sinemsavas/policy-rag/actions/runs/40350601018) | `success` |

### PR #3 — Add a reviewed NFIP corpus with verified source downloads

[Pull request](https://github.com/sinemsavas/policy-rag/pull/3) · Açılış: 26.10.2026 16:52:19 CET · Birleştirme: 26.10.2026 16:53:16 CET

**Amaç:** İlk küçük ve sürümlü belge koleksiyonunu belirlemek ve aynı kaynak byte'larını tekrar edinilebilir hale getirmek.

**Sonuç:** Dwelling, General Property ve RCBAP için GovInfo 01.10.2025 sürümü kataloglandı. PDF başlığı, boyut ve SHA-256 doğrulayan; doğru önbelleği yeniden kullanan indirici eklendi. Ham PDF'ler Git/Docker dışında tutuldu.

| Dosya | İşlem | Açıklama |
| --- | --- | --- |
| [.dockerignore](../.dockerignore) | Güncellendi | Ham/üretilmiş veri ve özel dosyaların build bağlamından çıkarılması. |
| [.gitignore](../.gitignore) | Güncellendi | Gerçek ayarlar, önbellekler ve ilgili yerel veri çıktıları için Git dışlama kuralları. |
| [README.md](../README.md) | Güncellendi | Kurulum, kullanım, mevcut durum ve ilgili teknik notlara bağlantılar. |
| [SPEC.md](../SPEC.md) | Güncellendi | Aşamanın numaralı kabul kriterleri ve doğrulama gereksinimleri. |
| [docs/corpus.json](../docs/corpus.json) | Eklendi | Sürüm, kaynak kimliği, byte/hash ve bölüm sınırları için makine kataloğu. |
| [docs/corpus.md](../docs/corpus.md) | Eklendi | Belge kapsamı, kaynak incelemesi ve indirme/çıkarma notları. |
| [scripts/__init__.py](../scripts/__init__.py) | Eklendi | Veri hazırlama komutları için Python modül paketi. |
| [scripts/download_corpus.py](../scripts/download_corpus.py) | Eklendi | Katalog doğrulama ve güvenilir, tekrarlanabilir kaynak edinme. |
| [tests/test_download_corpus.py](../tests/test_download_corpus.py) | Eklendi | Önbellek, bozuk içerik, dosya yolu ve ağ hata testleri. |

**Doğrulama:** Yerel sonuç 10 passed. Üç gerçek dosyanın kayıtlı boyut ve hash'leri eşleşti; tekrar çalıştırma üç dosyayı indirmeden doğruladı. Bu aşamada bağımlılıklar değişmedi.

**Çalışma commit'i:**

- [`9364afa`](https://github.com/sinemsavas/policy-rag/commit/9364afaffa6c4f84827536c2803b048d15cf9a58): `feat: add reviewed NFIP corpus and verified source downloads` — 26.10.2026 16:51:47 CET.

**Main commit'i:** [`b43d6ff`](https://github.com/sinemsavas/policy-rag/commit/b43d6ff581f7cd4f16cc4ff4822315fbcbbb8174).

| Kontrol | Actions kaydı | Gözlenen sonuç |
| --- | --- | --- |
| Çalışma dalı push | [40353526693](https://github.com/sinemsavas/policy-rag/actions/runs/40353526693) | `success` |
| PR | [40353580555](https://github.com/sinemsavas/policy-rag/actions/runs/40353580555) | `success` |
| Main push | [40353732883](https://github.com/sinemsavas/policy-rag/actions/runs/40353732883) | `success` |

### PR #4 — Extract policy appendix text with original page metadata

[Pull request](https://github.com/sinemsavas/policy-rag/pull/4) · Açılış: 26.10.2026 17:25:25 CET · Birleştirme: 26.10.2026 17:26:37 CET

**Amaç:** PDF sınır sayfalarındaki komşu poliçeleri ayırırken orijinal sayfa konumunu ve basılı etiketi korumak.

**Sonuç:** cfr-plain-v1 profili, hedef bölüm başlıkları ve sayfa metadata'sı ile JSONL üretimi eklendi. Kaynak/text/çıkarma parmak izleri kaydedildi. pypdf 6.21.2 font desteğiyle eklendi; var olan paket sürümleri korundu.

| Dosya | İşlem | Açıklama |
| --- | --- | --- |
| [.dockerignore](../.dockerignore) | Güncellendi | Ham/üretilmiş veri ve özel dosyaların build bağlamından çıkarılması. |
| [.gitignore](../.gitignore) | Güncellendi | Gerçek ayarlar, önbellekler ve ilgili yerel veri çıktıları için Git dışlama kuralları. |
| [README.md](../README.md) | Güncellendi | Kurulum, kullanım, mevcut durum ve ilgili teknik notlara bağlantılar. |
| [SPEC.md](../SPEC.md) | Güncellendi | Aşamanın numaralı kabul kriterleri ve doğrulama gereksinimleri. |
| [docs/corpus.json](../docs/corpus.json) | Güncellendi | Sürüm, kaynak kimliği, byte/hash ve bölüm sınırları için makine kataloğu. |
| [docs/corpus.md](../docs/corpus.md) | Güncellendi | Belge kapsamı, kaynak incelemesi ve indirme/çıkarma notları. |
| [docs/extraction.md](../docs/extraction.md) | Eklendi | Sayfa koruyan çıkarma profili, kayıt sözleşmesi ve gerçek kaynak kontrolleri. |
| [pyproject.toml](../pyproject.toml) | Güncellendi | Geliştirme veya çalışma bağımlılıklarının tanımı. |
| [scripts/download_corpus.py](../scripts/download_corpus.py) | Güncellendi | Katalog doğrulama ve güvenilir, tekrarlanabilir kaynak edinme. |
| [scripts/extract_corpus.py](../scripts/extract_corpus.py) | Eklendi | Doğru poliçe bölümünü sayfa ve kaynak bilgisiyle JSONL'e çıkarma. |
| [tests/test_extract_corpus.py](../tests/test_extract_corpus.py) | Eklendi | Gerçek küçük PDF'lerle başlık, sayfa, metadata ve hata testleri. |
| [uv.lock](../uv.lock) | Güncellendi | Yeni bağımlılıklarla uyumlu kilitli paket çözümü. |

**Doğrulama:** Yerel sonuç 26 passed. Gerçek kaynaklarda 16 + 15 + 16 = 47 sayfa kaydı üretildi. Tekrar çıkarma byte düzeyinde aynı dosyaları verdi. Kaynakların görünür Xref uyarısı extraction.md'de belgelendi.

**Çalışma commit'i:**

- [`6beed00`](https://github.com/sinemsavas/policy-rag/commit/6beed00502accfaf8530c63fb068fe116886541d): `feat: extract policy appendix text with page-level source metadata` — 26.10.2026 17:24:44 CET.

**Main commit'i:** [`b6e02ff`](https://github.com/sinemsavas/policy-rag/commit/b6e02ff76c363e8d4f7d1ac5d728fe024c303f71).

| Kontrol | Actions kaydı | Gözlenen sonuç |
| --- | --- | --- |
| Çalışma dalı push | [40358896371](https://github.com/sinemsavas/policy-rag/actions/runs/40358896371) | `success` |
| PR | [40358978531](https://github.com/sinemsavas/policy-rag/actions/runs/40358978531) | `success` |
| Main push | [40359169911](https://github.com/sinemsavas/policy-rag/actions/runs/40359169911) | `success` |

### PR #5 — Add configurable page-contained chunks with source lineage

[Pull request](https://github.com/sinemsavas/policy-rag/pull/5) · Açılış: 26.10.2026 18:00:33 CET · Birleştirme: 26.10.2026 18:01:53 CET

**Amaç:** Sayfa kayıtlarını ölçülebilir, ayarı kaydedilmiş ve kaynakla birebir eşleşen arama parçalarına bölmek.

**Sonuç:** page-char-v1 ile sayfa sınırlarını aşmayan parçalar, gerçek örtüşme, tam metin offset'leri, deterministik kimlikler, ayrı deney klasörleri ve rapor eklendi. API ve bağımlılıklar değişmedi.

| Dosya | İşlem | Açıklama |
| --- | --- | --- |
| [.dockerignore](../.dockerignore) | Güncellendi | Ham/üretilmiş veri ve özel dosyaların build bağlamından çıkarılması. |
| [.gitignore](../.gitignore) | Güncellendi | Gerçek ayarlar, önbellekler ve ilgili yerel veri çıktıları için Git dışlama kuralları. |
| [README.md](../README.md) | Güncellendi | Kurulum, kullanım, mevcut durum ve ilgili teknik notlara bağlantılar. |
| [SPEC.md](../SPEC.md) | Güncellendi | Aşamanın numaralı kabul kriterleri ve doğrulama gereksinimleri. |
| [docs/chunking.json](../docs/chunking.json) | Eklendi | Versiyonlu 1200 karakter / 200 örtüşme baseline ayarı. |
| [docs/chunking.md](../docs/chunking.md) | Eklendi | Algoritma, provenance, kullanım, iki ayarın gözlenen sonuçları. |
| [docs/extraction.md](../docs/extraction.md) | Güncellendi | Sayfa koruyan çıkarma profili, kayıt sözleşmesi ve gerçek kaynak kontrolleri. |
| [scripts/chunk_corpus.py](../scripts/chunk_corpus.py) | Eklendi | Sayfa içi tam kesitler, deterministik chunk kimlikleri ve koşu raporu. |
| [tests/test_chunk_corpus.py](../tests/test_chunk_corpus.py) | Eklendi | Boyut, örtüşme, Unicode, kapsama, kimlik ve hatalı girdi testleri. |

**Doğrulama:** Yerel sonuç 75 passed. Aynı 47 sayfada 1200/200 ile 225, 800/120 ile 328 chunk oluştu. İki koşuda kaynak metnin 213.403 karakteri kapsandı; varsayılan koşunun tekrarı byte düzeyinde aynı kaldı. Bunlar retrieval veya cevap kalitesi metrikleri değildir.

**Çalışma commit'i:**

- [`d1f3c27`](https://github.com/sinemsavas/policy-rag/commit/d1f3c276f78c9d391c1c1907cca66aa2b8fde0b8): `feat: add configurable page-contained chunking with source lineage` — 26.10.2026 17:59:58 CET.

**Main commit'i:** [`43b7212`](https://github.com/sinemsavas/policy-rag/commit/43b72123f52e9a88a3381ed656d0508f4b28c3e3).

| Kontrol | Actions kaydı | Gözlenen sonuç |
| --- | --- | --- |
| Çalışma dalı push | [40364499780](https://github.com/sinemsavas/policy-rag/actions/runs/40364499780) | `success` |
| PR | [40364565903](https://github.com/sinemsavas/policy-rag/actions/runs/40364565903) | `success` |
| Main push | [40364777254](https://github.com/sinemsavas/policy-rag/actions/runs/40364777254) | `success` |

## 5. Erişilen bütün push ve PR CI olayları

Bu dokümantasyon değişikliğinden önce API'nin döndürdüğü 19 Actions koşusunun tamamı başarılıdır: 14 push ve 5 pull_request olayı. Dalın başlangıç commit'i için oluşan koşular da korunmuştur. Tablo kronolojik sıradadır.

| Tarih / saat | Tetikleyici | Dal | Commit | Actions / sonuç |
| --- | --- | --- | --- | --- |
| 24.10.2026 16:52:06 CEST | `push` | `chore/foundation-docs-ci` | [`e232914`](https://github.com/sinemsavas/policy-rag/commit/e232914623430f39a8bdfec59857f6ae84d20d29) | [40104407875](https://github.com/sinemsavas/policy-rag/actions/runs/40104407875) · `success` |
| 24.10.2026 16:52:08 CEST | `pull_request` | `chore/foundation-docs-ci` | [`e232914`](https://github.com/sinemsavas/policy-rag/commit/e232914623430f39a8bdfec59857f6ae84d20d29) | [40104411226](https://github.com/sinemsavas/policy-rag/actions/runs/40104411226) · `success` |
| 24.10.2026 16:56:06 CEST | `push` | `main` | [`966e922`](https://github.com/sinemsavas/policy-rag/commit/966e92222debf2712697b9435c5e5b8e17ba359b) | [40104691468](https://github.com/sinemsavas/policy-rag/actions/runs/40104691468) · `success` |
| 26.10.2026 16:32:17 CET | `push` | `docs/readme-project-focus` | [`966e922`](https://github.com/sinemsavas/policy-rag/commit/966e92222debf2712697b9435c5e5b8e17ba359b) | [40350292673](https://github.com/sinemsavas/policy-rag/actions/runs/40350292673) · `success` |
| 26.10.2026 16:32:56 CET | `push` | `docs/readme-project-focus` | [`d779a02`](https://github.com/sinemsavas/policy-rag/commit/d779a02397666e8f0408a92b46a6c9304b3ef5ea) | [40350399843](https://github.com/sinemsavas/policy-rag/actions/runs/40350399843) · `success` |
| 26.10.2026 16:33:11 CET | `pull_request` | `docs/readme-project-focus` | [`d779a02`](https://github.com/sinemsavas/policy-rag/commit/d779a02397666e8f0408a92b46a6c9304b3ef5ea) | [40350440749](https://github.com/sinemsavas/policy-rag/actions/runs/40350440749) · `success` |
| 26.10.2026 16:34:11 CET | `push` | `main` | [`4fc5695`](https://github.com/sinemsavas/policy-rag/commit/4fc5695c1a9e3312b83d94ed201bae24d2828e37) | [40350601018](https://github.com/sinemsavas/policy-rag/actions/runs/40350601018) · `success` |
| 26.10.2026 16:51:24 CET | `push` | `feat/public-corpus-acquisition` | [`4fc5695`](https://github.com/sinemsavas/policy-rag/commit/4fc5695c1a9e3312b83d94ed201bae24d2828e37) | [40353422704](https://github.com/sinemsavas/policy-rag/actions/runs/40353422704) · `success` |
| 26.10.2026 16:52:03 CET | `push` | `feat/public-corpus-acquisition` | [`9364afa`](https://github.com/sinemsavas/policy-rag/commit/9364afaffa6c4f84827536c2803b048d15cf9a58) | [40353526693](https://github.com/sinemsavas/policy-rag/actions/runs/40353526693) · `success` |
| 26.10.2026 16:52:22 CET | `pull_request` | `feat/public-corpus-acquisition` | [`9364afa`](https://github.com/sinemsavas/policy-rag/commit/9364afaffa6c4f84827536c2803b048d15cf9a58) | [40353580555](https://github.com/sinemsavas/policy-rag/actions/runs/40353580555) · `success` |
| 26.10.2026 16:53:19 CET | `push` | `main` | [`b43d6ff`](https://github.com/sinemsavas/policy-rag/commit/b43d6ff581f7cd4f16cc4ff4822315fbcbbb8174) | [40353732883](https://github.com/sinemsavas/policy-rag/actions/runs/40353732883) · `success` |
| 26.10.2026 17:24:15 CET | `push` | `feat/page-preserving-extraction` | [`b43d6ff`](https://github.com/sinemsavas/policy-rag/commit/b43d6ff581f7cd4f16cc4ff4822315fbcbbb8174) | [40358777177](https://github.com/sinemsavas/policy-rag/actions/runs/40358777177) · `success` |
| 26.10.2026 17:24:59 CET | `push` | `feat/page-preserving-extraction` | [`6beed00`](https://github.com/sinemsavas/policy-rag/commit/6beed00502accfaf8530c63fb068fe116886541d) | [40358896371](https://github.com/sinemsavas/policy-rag/actions/runs/40358896371) · `success` |
| 26.10.2026 17:25:28 CET | `pull_request` | `feat/page-preserving-extraction` | [`6beed00`](https://github.com/sinemsavas/policy-rag/commit/6beed00502accfaf8530c63fb068fe116886541d) | [40358978531](https://github.com/sinemsavas/policy-rag/actions/runs/40358978531) · `success` |
| 26.10.2026 17:26:39 CET | `push` | `main` | [`b6e02ff`](https://github.com/sinemsavas/policy-rag/commit/b6e02ff76c363e8d4f7d1ac5d728fe024c303f71) | [40359169911](https://github.com/sinemsavas/policy-rag/actions/runs/40359169911) · `success` |
| 26.10.2026 17:59:31 CET | `push` | `feat/page-aware-chunking` | [`b6e02ff`](https://github.com/sinemsavas/policy-rag/commit/b6e02ff76c363e8d4f7d1ac5d728fe024c303f71) | [40364388826](https://github.com/sinemsavas/policy-rag/actions/runs/40364388826) · `success` |
| 26.10.2026 18:00:13 CET | `push` | `feat/page-aware-chunking` | [`d1f3c27`](https://github.com/sinemsavas/policy-rag/commit/d1f3c276f78c9d391c1c1907cca66aa2b8fde0b8) | [40364499780](https://github.com/sinemsavas/policy-rag/actions/runs/40364499780) · `success` |
| 26.10.2026 18:00:37 CET | `pull_request` | `feat/page-aware-chunking` | [`d1f3c27`](https://github.com/sinemsavas/policy-rag/commit/d1f3c276f78c9d391c1c1907cca66aa2b8fde0b8) | [40364565903](https://github.com/sinemsavas/policy-rag/actions/runs/40364565903) · `success` |
| 26.10.2026 18:01:55 CET | `push` | `main` | [`43b7212`](https://github.com/sinemsavas/policy-rag/commit/43b72123f52e9a88a3381ed656d0508f4b28c3e3) | [40364777254](https://github.com/sinemsavas/policy-rag/actions/runs/40364777254) · `success` |

CI dosyasının varlığı, o çalışmanın geçtiğinin kanıtı değildir; tablodaki sonuçlar gerçek koşulardan alınmıştır. Güncel ve sonraki koşular [Actions sayfasından](https://github.com/sinemsavas/policy-rag/actions) izlenebilir.

## 6. GitHub'a gönderilenler ve yerelde kalanlar

| İçerik | Nerede tutuluyor? | Gerekçe |
| --- | --- | --- |
| Kod, ayar örneği, lock, altyapı ve testler | GitHub | Kurulum ve davranışın tekrar üretilebilmesi |
| Kaynak URL/hash/sürüm kataloğu | GitHub | Aynı kaynakların doğrulanabilmesi |
| README, SPEC ve teknik notlar | GitHub | Kullanım, kabul kriteri ve kararların izlenmesi |
| Gerçek `.env` | Yerel, Git ve build dışında | Gerçek yapılandırma ve parolalar |
| Kaynak PDF'ler | Yerel `data/raw/` | Katalog üzerinden yeniden edinilir |
| Sayfa ve chunk çıktıları | Yerel `data/processed/`, `data/chunks/` | Sürümlü kod/ayar/kaynakla yeniden üretilir |
| PostgreSQL dosyaları | Docker volume | Veritabanı kalıcılığı; repo dosyası değildir |

## 7. Yeni çalışma — birleşik proje dokümantasyonu

**Tarih:** 28.10.2026. Bu değişiklik, geçmiş çalışmayı anlatan Türkçe proje rehberini, bu GitHub dökümünü ve ayrıntılı gelecek planını ekler. README bunlara bağlanır; corpus notundaki eski durum ifadesi chunking'in tamamlandığını gösterecek şekilde düzeltilir. Uygulama, bağımlılıklar ve workflow değiştirilmez.

**Teslim kaydı:** [PR #6 — Add detailed Turkish project guide, GitHub history, and roadmap](https://github.com/sinemsavas/policy-rag/pull/6). Çalışma dalı `docs/project-handbook`; ilk belge yayım commit'i [`9005d64`](https://github.com/sinemsavas/policy-rag/commit/9005d64e28ff2a563929108d0d34a111d25f73ae). PR 28.10.2026 14:20:50 CET tarihinde açıldı. Bu kayıt daha sonra aynı PR içinde eklendi; güncel son commit ve birleştirme durumu PR sayfasında izlenir.

| Dosya | Yapılan iş |
| --- | --- |
| [docs/project-guide.md](project-guide.md) | Başlangıçtan bugüne ayrıntılı anlatım, dosya haritası, mimari, komutlar, veri sözleşmeleri, testler ve sorun çözümleri |
| [docs/github-history.md](github-history.md) | İlk altı main commit'i, beş önceki PR, bütün değişen dosyalar, dal/commit eşleştirmeleri ve 19 tarihsel CI kaydı; bu PR'nin teslim kaydı |
| [docs/roadmap.md](roadmap.md) | On iki adımın durumu; sonraki aşamalar için uygulama sırası ve tamamlanma kanıtı |
| [README.md](../README.md) | Üç ayrıntılı belgeye giriş bağlantıları |
| [docs/corpus.md](corpus.md) | Chunking durumunun düzeltilmesi ve ana rehbere bağlantı |

**Yerel doğrulama:** Mevcut paket `75 passed` verdi. İlk belge revizyonunda 113 göreli bağlantı, açık bölüm bağlantıları, tablo sütunları ve 32 kod bloğu kontrol edildi. Diğer takip edilen dosyalar kaynak commit'inin Git blob hash'leriyle eşleştirildi. Üç PDF'nin boyut/SHA-256 bilgileri ve iki mevcut koşunun 47 sayfa, 225/328 chunk, 213.403 kaynak karakteri sonuçları yeniden kontrol edildi. Bu teslim kaydı eklendikten sonra dokümantasyon bağlantı ve biçim kontrolleri tekrar uygulandı.

| İlk belge revizyonunun kontrolü | Actions kaydı | Gözlenen sonuç |
| --- | --- | --- |
| Çalışma dalı push, `9005d64` | [40695574561](https://github.com/sinemsavas/policy-rag/actions/runs/40695574561) | `success` |
| PR, `9005d64` | [40695591143](https://github.com/sinemsavas/policy-rag/actions/runs/40695591143) | `success` |

Bu iki bağlantı ilk revizyonun kayıtlarıdır; PR sayfası sonraki belge kayıt güncellemesinin kontrollerini de gösterir. Dokümanın kendi son SHA'sı ve birleştirme sonrası main koşusu, sonraki geçmiş güncellemesinde kesin bağlantılarıyla eklenebilir.

## 8. Sonraki değişikliklerin kayıt şablonu

Bir sonraki özellik eklendiğinde önceki PR'nin nihai main commit'i ve birleştirme sonrası CI kaydı kesinleşmiş olarak eklenir. Güncel dokümantasyon commit'inin kendi SHA'sı içeride önceden bilinemeyeceğinden kendi PR bağlantısı yeterlidir.

```text
Tarih:
PR numarası ve başlığı:
Amaç ve gözlenen sonuç:
Çalışma dalı:
Çalışma commit(ler)i:
Main sonuç commit'i (birleştirme sonrası):
Eklenen/güncellenen dosyalar ve görevleri:
Yerel komutlar ve gerçek sonuç:
Push / PR / main CI bağlantıları ve durumları:
Veri veya model deneyi varsa kimlikler ve ölçüm sınırları:
Sonraki adım:
```

Rehber: [project-guide.md](project-guide.md) · Plan: [roadmap.md](roadmap.md) · Sözleşme: [SPEC.md](../SPEC.md)
