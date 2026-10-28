# Policy RAG — Ayrıntılı Yol Haritası

**Son güncelleme:** 28.10.2026

Bu dosya bundan sonra geliştirilecek özelliklerin amacını, sırasını, girdilerini ve tamamlanma koşullarını açıklar. Aşağıdaki teknik taslaklar, henüz kodlanmamış aşamalarda uygulama planıdır. Model, hizmet, şema ve bütçe seçimleri ilgili aşamada doğrulanıp kaydedilir. Güncel çalışan akış [proje rehberinde](project-guide.md), geçmiş değişiklikler [GitHub kaydında](github-history.md) bulunur. Davranış sözleşmesi [SPEC.md](../SPEC.md) olmaya devam eder.

## 1. Başlangıçtaki 12 adımın güncel durumu

| No | Aşama | Durum | Sonuç / kalan iş |
| --- | --- | --- | --- |
| 1 | Çalışan temeli Git ve GitHub'a kaydetmek | Tamamlandı | İlk commit, repo, README ve PR #1 |
| 2 | Amaç, kısıt ve kabul kriterlerini yazmak | Tamamlandı | SPEC ve mevcut dokümantasyon |
| 3 | İlk belge koleksiyonunu seçmek | Tamamlandı | Üç sürümlenmiş FEMA/NFIP kaynağı, katalog ve indirme; PR #3 |
| 4 | PDF'den metin çıkarmak | Tamamlandı | Belge/sayfa bilgili 47 kayıt; PR #4 |
| 5 | Chunking ve embedding | Kısmen tamamlandı | Chunking bitti; embedding ve pgvector'a yükleme sırada |
| 6 | Anlamsal arama | Planlandı | Arama ve form/sürüm filtreleri |
| 7 | Kaynaklı cevap üretimi | Planlandı | İlk LLM bağlantısı, yapılandırılmış cevap, atıf ve abstention |
| 8 | Evaluation seti ve ilk ölçümler | Planlandı | 40–50 soru ve tekrar üretilebilir ölçüm |
| 9 | Kontrollü iyileştirme karşılaştırmaları | Planlandı | Chunk/model/reranking deneyleri |
| 10 | Monitoring, arayüz ve CI/CD | Kısmen tamamlandı | Pytest CI var; entegrasyon, image build, metrik ve panel eklenecek |
| 11 | AWS ve Bedrock | Planlandı | Bütçe, barındırma, veritabanı kararı ve ikinci LLM bağlantısı |
| 12 | MCP ve portföy sunumu | Planlandı | Ortak uygulama mantığını kullanan araç, demo ve gerçek sonuçlar |

TypeScript yardımcı araç ve sertifika hazırlığı, ana akışa eklenebilecek isteğe bağlı çalışmalardır. Çalışan sistemin önkoşulu veya tamamlanmış teslimi sayılmaz.

<a id="embedding"></a>
## 2. Sıradaki aşama: embedding ve pgvector'a yükleme

### Amaç ve eldeki girdiler

Metin parçalarını anlamsal benzerlik aramasında kullanılabilecek vektörlere dönüştüreceğiz. Her vektör, kaynak chunk'a ve onun belge/sürüm/sayfa ilişkisine bağlanacak.

Girdiler üç `.chunks.jsonl` dosyası, tamamlanmış `report.json`, kaynak kataloğu ve çalışan PostgreSQL/pgvector servisidir. İlk temel veri ayarı `page-char-v1-1200-200` ve 225 chunk'tır. Bu sayı başka chunk ayarıyla değişebilir; yükleyici sayıyı sabit yazmak yerine rapordan doğrulayacak.

### Uygulama sırası

1. Embedding sağlayıcısını/modelini seç; İngilizce belgeler, hedef sorgu dili, 16 GB yerel ortam, GPU gereksinimi, kullanım koşulları ve maliyeti birlikte değerlendir.
2. Model kimliği, sürüm, vektör boyutu, token sınırı, giriş hazırlama kuralı ve benzerlik ölçüsünü kaydet. Doküman ve sorgu vektörlerinin uyumlu aynı yapılandırmayla üretileceğini tanımla.
3. Mevcut `init.sql` yaklaşımına ek olarak şema geçişi düzeni kur. Tabloları yalnızca boş veritabanında oluşacak başlangıç SQL'ine bırakma.
4. Chunk raporunu, dosya hash'lerini ve kayıtları yükleme öncesi doğrula. Tamamlanmamış veya farklı deneylere ait dosyaları karıştırma.
5. Metinleri kontrollü batch'lerle vektörleştir. Token sınırı aşılırsa sessiz kesme yerine açık hata veya kayıtlı bir yeniden parçalama politikası kullan.
6. Başarılı yüklemeyi kaynak/ayar bilgileriyle transaction sınırları içinde sakla. Tekrar çalıştırmada aynı veriyi çoğaltmayan bir kimlik kuralı kullan.
7. Hata, yeniden deneme, yarıda kesilme ve farklı model sürümü durumlarını test et. Ücretli çağrı varsa tüketimi ve toplam maliyeti kaydet.

### Önerilen kayıt ayrımı

Kesin tablo adları migration sırasında belirlenecek. Aşağıdaki ayrım veri ilişkilerinin taslağıdır:

| Kayıt türü | Korunacak bilgiler |
| --- | --- |
| Belge/sürüm | `document_id`, kaynak URL/hash, sürüm, çıkarma profili |
| Chunk | `chunk_id`, metin/hash, kaynak sayfa, basılı etiket, offset ve chunking ayarı |
| Embedding yapılandırması | Sağlayıcı/model/sürüm, boyut, giriş hazırlama ve mesafe kuralı |
| Embedding kaydı | Chunk kimliği, yapılandırma kimliği, vektör ve üretim durumu |
| Yükleme koşusu | Girdi raporu/hash'leri, başarı/hata sayıları ve işlem sonucu |

Bir chunk için birden çok model veya deney kaydı olabilir. Farklı boyuttaki veya farklı anlam uzayındaki vektörler tek arama içinde karıştırılmamalıdır. Kimlik kuralı, yalnız metni değil embedding yapılandırmasını da hesaba katmalıdır.

### Tamamlanma kanıtı

- Seçilen model ve token/boyut kontrolleri belgelenmiş olacak.
- Üç belgenin beklenen bütün chunk'ları, kaynak ilişkileriyle saklanacak.
- Aynı veri ve ayarla tekrar yükleme kayıt sayısını artırmayacak.
- Bozuk girdi, model hatası ve boyut uyuşmazlığı kontrollü hata üretecek.
- Gerçek pgvector ile entegrasyon testi ve örnek yükleme raporu bulunacak.
- Çalıştırma komutları ve gerekli yeni değişkenler README/örnek ayara eklenecek.

İlgili gereksinimler: **R-01, R-02**. Bu aşama bittiğinde vektör veri tabanı oluşur; kaynaklı cevap üretimi ayrıca geliştirilir.

<a id="retrieval"></a>
## 3. Anlamsal arama

### Amaç

Kullanıcının sorusunu vektörleştirip ilgili kaynak parçalarını bulacağız. İlk kontrol, modelin güzel bir cevap yazması değil, doğru belge ve sayfanın arama sonucuna gelmesidir.

### Uygulama sırası

1. Sorgu hazırlama ve embedding işlemini dokümanlarla uyumlu kur.
2. Bir retrieval servisinde pgvector benzerlik sorgusunu ve `top_k` gibi ayarları uygula.
3. Belge türü, sürüm veya koleksiyon filtresi gerekiyorsa açık giriş alanları ekle.
4. Her sonuçta parça metni, skor/mesafe, belge kimliği ve sayfa bilgilerini döndür.
5. Servisi örnek sorular ve elle doğrulanmış ilgili sayfalarla kontrol et.
6. İlk küçük koleksiyonda doğrudan aramayı referans al. Yaklaşık indeks gerekirse hız ve retrieval etkisini ayrı karşılaştır.
7. Başarılı sonuç, sıfır sonuç ve servis hatasını birbirinden ayıran API sözleşmesini yaz.

Benzer hükümler üç formda tekrar edebileceği için yanlış formdan gelen çok benzer bir chunk özellikle incelenecek. Gerekirse kapsam belirsizliği kullanıcıya gösterilecek veya belge seçimi istenecek. İngilizce kaynaklarla Türkçe sorgu hedeflenirse bu davranış ayrıca değerlendirme soruları içerecek.

### Tamamlanma kanıtı

Retrieval girişi/çıktısı belgelenmiş, gerçek DB sorgusu test edilmiş ve örnek sorular için ilgili sayfa/parçalar kaydedilmiş olacak. Skorun hangi yönde daha iyi olduğu açıklanacak. Kayıtlı bir değerlendirme yapılmadan rastgele benzerlik eşiğine “güven eşiği” denmeyecek.

Arama endpoint'inin adı ve şeması bu aşamada seçilecek; mevcut API'de şu an böyle bir endpoint bulunmuyor. İlgili gereksinimler: **R-01, R-02, R-06, R-07**.

<a id="answers"></a>
## 4. LLM ile kaynaklı cevap üretimi

### Amaç ve başlangıç kararı

Doğru parçalar bulunabildiğinde ilk cevap üretim bağlantısı için başlangıç planındaki **Anthropic API** kullanılacak. Belirli model kimliği, sürümü, bağlam/token sınırları ve fiyat bilgisi uygulama aşamasında doğrulanacak. Bu seçim embedding modelinin de aynı sağlayıcıdan geleceği anlamına gelmez.

### Cevap sözleşmesi

| Durum | Planlanan davranış |
| --- | --- |
| Yeterli kanıt var | Kaynağa dayalı cevap; önemli her iddia için destekleyici atıf |
| Belgelerde yeterli kanıt yok | Açık `insufficient_evidence` sonucu ve cevap belirlenemediği açıklaması |
| Poliçe/sürüm kapsamı belirsiz veya çelişkili | Belirsizliği/çelişkiyi gösterme veya netleştirme |
| Sağlayıcı, ağ veya servis hatası | Operasyonel hata; kanıt yetersizliği olarak gösterilmez |

### Uygulama sırası

1. Soru, getirilen kanıt ve cevap beklentisini ayıran prompt/sürüm düzeni oluştur.
2. Kaynak metnindeki yönergeleri uygulama talimatı olarak kabul etme; belgeleri veri olarak işle.
3. Pydantic ile yapılandırılmış cevap ve atıf şeması tanımla.
4. Modelin yalnızca kendisine verilen parça kimliklerini kullanmasını sağla; çıktıdaki her kimliği getirilen kayıtlarla doğrula.
5. Atıfları belge adı, sürüm, orijinal PDF sayfası ve basılı etiketle göster.
6. Desteksiz kapsam, istisna, limit veya atıf üretimini başarısızlık olarak ele al.
7. Zaman aşımı, yeniden deneme, token sınırı ve sağlayıcı hata sözleşmesini test et.
8. Desteklenen, cevaplanamayan, kapsamı belirsiz ve belge içi yanıltıcı yönerge içeren örnekler ekle.

Atıf kimliğinin geçerli olması yalnızca kaynağa bağlanabilirliği kanıtlar. Atıf metninin cevaptaki iddiayı desteklemesi ayrıca değerlendirilecektir. Aynı şekilde modelin cevap üretmesi, aramanın ilgili kanıtı doğru getirdiğini tek başına göstermez.

### Tamamlanma kanıtı

Belgelenmiş cevap şeması, örnek kaynaklı cevap, açık abstention örneği ve servis hatası örneği bulunacak. Atıf doğrulama ve hata sözleşmesi testleri geçecek. Gerçek çağrılarda kullanılan model/prompt/ayar ve tüketim kaydedilecek. İlgili gereksinimler: **R-03–R-07**.

<a id="evaluation"></a>
## 5. Evaluation seti ve ilk ölçümler

### Amaç

Sistemin güçlü ve zayıf taraflarını sabit, kaynağa dayalı sorular üzerinde ölçmek istiyoruz. Başlangıç planı **40–50 soru** hazırlamaktır; bu set henüz oluşturulmadı.

Her soru için beklenen cevap veya abstention, kaynak belge/sayfa, cevaplanabilirlik etiketi ve kapsam kaydedilecek. Sorular üç formu, benzer hükümleri, form farklarını, sayfa sınırlarını, belirsizlikleri ve belgelerde cevabı olmayan durumları kapsayacak. Sorular yalnızca model çıktısından doğru varsayılmayacak; referanslar kaynakla kontrol edilecek.

### Uygulama sırası

1. Soru formatını ve puanlama yöntemini tanımla.
2. Soruları kaynak sayfalarla birlikte sürümle.
3. Ayar geliştirmede kullanılan soruları karşılaştırmada saklanan bölümden ayır.
4. Corpus, kod, model, prompt, chunking, embedding ve varsa reranking kimliğini her koşuda kaydet.
5. Retrieval ve cevap sonuçlarını ayrı kaydet; hatanın hangi aşamada oluştuğunu gör.
6. İlk baseline raporunu ve hata örneklerini yayımla.

### Ölçümler

| Ölçüm | Cevapladığı soru | Raporda belirtilecek sınır |
| --- | --- | --- |
| Retrieval başarısı, ör. Recall@k | Beklenen kaynak ilk k aday arasında mı? | Etiketleme sayfa mı chunk mı; birden çok doğru kaynak var mı? |
| Cevap doğruluğu | Beklenen bilgi doğru mu? | Kullanılan rubrik ve kısmi doğruluk kuralı |
| Atıf doğruluğu ve groundedness | İddialar kaynakla destekleniyor mu? | Kimlik kontrolü ile anlamsal destek ayrı gösterilir |
| Abstention davranışı | Kanıt yokken cevap vermekten kaçınıyor mu? | Gereksiz abstention ve desteksiz cevap ayrı sayılır |
| Latency | İstek ne kadar sürüyor? | Örnek sayısı, ortam ve p50/p95 gibi özetler |
| Token ve tahmini maliyet | Bir sorgunun tüketimi nedir? | Sağlayıcı/model, fiyat tarihi, embedding ve cevap maliyet ayrımı |

Bir otomatik model hakemi kullanılırsa rubrik, hakem modeli ve sınırlamalar yazılacak; mümkün olan örnekler insan tarafından kaynakla kontrol edilecek. Başarı eşiği, sonuç görüldükten sonra geçmişe dönük seçilmeyecek. Küçük setten elde edilen sonuçların genellenebilirlik sınırı açıklanacak.

### Tamamlanma kanıtı

40–50 sürümlü soru, referanslar, puanlama açıklaması, tekrar çalıştırma komutu ve gerçek sonuç dosyaları bulunacak. Ölçülmeyen alanlar boş veya “ölçülmedi” olarak kalacak. İlgili gereksinimler: **E-01–E-03**.

<a id="experiments"></a>
## 6. Kontrollü iyileştirmeler

İlk ölçümden sonra sistematik karşılaştırmalar yapılacak. Eldeki `1200/200` ve `800/120` chunk sayıları ilk iki veri hazırlama ayarıdır; henüz kalite karşılaştırması değildir.

| Deney alanı | Değiştirilecek unsur | Sabit tutulacak temel |
| --- | --- | --- |
| Chunk boyutu/örtüşmesi | Kayıtlı ayarlar | Kaynak sürümü, soru seti, cevap modeli |
| Metin normalizasyonu | Ayrı sürümlü profil, ör. tireleme kuralı | Kaynak ve değerlendirme yöntemi |
| Embedding modeli | Model, boyut, giriş hazırlama | Sorular ve mümkün olduğunca diğer aşamalar |
| Retrieval | `top_k`, filtreler ve gerekirse hibrit yaklaşım | Referans kaynaklar ve baseline |
| Reranking | İkinci sıralama yöntemi | İlk aday kümesi veya açıkça kayıtlı karşılaştırma düzeni |
| Cevap modeli/prompt | Tek seferde kontrol edilen değişiklik | Kanıt kümesi ve soru seti |

Her deneyde değişen değişken, beklenen etki, çalıştırma komutu, kimlikler, gerçek sonuçlar ve regresyonlar kaydedilecek. Kalite, süre ve maliyet birlikte değerlendirilecek. Daha karmaşık bir yöntemin eklenmesi tek başına iyileştirme sayılmayacak.

**Tamamlanma kanıtı:** Baseline'a karşı yeniden üretilebilir rapor; kazanan/kaybeden örnekler; seçilen ayarın gerekçesi ve sınırlaması. İlgili gereksinim: **E-04**.

<a id="operations"></a>
## 7. Monitoring, Streamlit ve CI/CD genişletmesi

### Monitoring

İstek kimliği, retrieval süresi, model süresi, toplam süre, token kullanımı, tahmini maliyet ve hata türleri kaydedilecek. Kimlik bilgileri loglara yazılmayacak. Başlangıçtaki boş belge koleksiyonuna dayanarak gerçek kişisel verilerin loglanması normal kabul edilmeyecek; veri/log kapsamı açık seçilecek.

Ücret hesabında kullanılan sağlayıcı, model ve fiyat tarihi kayıtlı olacak. Operasyonel hata ile `insufficient_evidence` ayrı sayılacak. Başarı oranı, servis erişilebilirliği ve kaynaklı cevap kalitesi birbirinin yerine kullanılmayacak.

### Streamlit arayüzü

Soru girişi, belge/kapsam seçimi, getirilen parçalar, kaynaklı cevap ve açıklanabilir hata/abstention durumu için küçük bir panel hazırlanacak. Panel API ile aynı iş mantığını kullanacak. Gerekirse deney ve operasyon sonuçları da görüntülenecek. Şu anda repoda Streamlit uygulaması yoktur.

### CI/CD

Bugün push ve PR'da bütün pytest paketi çalışıyor. Sıradaki kontroller gerçek PostgreSQL/pgvector entegrasyonu, `/ready` hata yolları, yükleme/retrieval davranışı ve Docker image build olacaktır. Ücretli sağlayıcı çağrıları her PR'da kontrolsüz çalıştırılmayacak; değerlendirme koşularının tetiklenmesi ve bütçesi ayrı tanımlanacak.

Image build ile deploy farklı aşamalardır. Bir imajın üretilmesi, AWS'de servis yayınlandığı anlamına gelmez. Dağıtım için ortam, kimlik, sürüm ve geri dönüş adımları ayrıca hazırlanacak.

**Tamamlanma kanıtı:** Metrik örnekleri, panel çalıştırma notu, anlamlı entegrasyon testleri ve başarılı image build kaydı. İlgili gereksinimler: **F-03 eksik entegrasyon kapsamı, D-01, D-02**.

<a id="aws"></a>
## 8. AWS'ye taşıma ve Bedrock

### Önce verilecek kararlar

Uygulama ve API kullanımının bütçesi, bölge, servis barındırması ve PostgreSQL seçeneği kararlaştırılacak. S3 kaynak/çıktı saklama; ECR API imajı saklama rolünde değerlendirilecek. Veritabanı barındırması, pgvector desteği ve toplam maliyet birlikte incelenecek. Bu doküman belirli bir ücretli kaynak oluşturulduğunu veya bir AWS servisine kesin karar verildiğini söylemez.

### Uygulama sırası

1. Bölge, aylık hedef bütçe ve kullanım varsayımlarını kaydet.
2. Bütçe uyarılarını ve minimum gerekli erişim izinlerini hazırla. Uyarının tek başına otomatik harcama durdurması olmadığını operasyon notunda açıkla.
3. Gizli yapılandırmanın dağıtım ortamına nasıl verileceğini belirle.
4. S3 konumları, ECR imaj sürümü ve API barındırmasını kur.
5. Veritabanı şeması/yüklemesini uygula ve yerel veriyle tutarlılığı kontrol et.
6. Canlı health/readiness, kaynaklı cevap ve monitoring akışını doğrula.
7. Geri alma, yedekleme gereksinimi ve kaynak kaldırma adımlarını yaz.
8. Bedrock üzerinden ikinci cevap modeli bağlantısını ortak sağlayıcı arayüzüne ekle; aynı evaluation setinde karşılaştır.

Bedrock eklemek retrieval veya citation kurallarını değiştirmemeli. Sağlayıcı seçimi, timeout, hata ve tüketim bilgisi ortak cevap mantığından ayrılacak. Model erişimi, bölge ve fiyatlar uygulama aşamasında güncel resmi kaynaklardan kontrol edilecek.

**Tamamlanma kanıtı:** Çalışan ortam, kullanılan kaynak listesi, gerçek dağıtım kontrolü, bütçe uyarıları, veritabanı tercihi, geri alma/kapatma kılavuzu ve kayıtlı Bedrock karşılaştırması. İlgili gereksinim: **D-02**.

<a id="mcp"></a>
## 9. MCP ve portföy teslimi

### MCP

RAG sorgulaması bir MCP aracı olarak sunulacak. REST ve MCP aynı retrieval/cevap servisini kullanacak; iki ayrı mantık zinciri oluşmayacak. Araç girdi/çıktısı, belge kapsamı, kaynak alanları, abstention ve operasyonel hata sözleşmesi açık olacak.

Keşif, istemci entegrasyonu, erişim ve taşıma seçimi uygulama aşamasında değerlendirilecek. MCP aracının çalışması, kaynakların cevabı desteklemesi değerlendirmesinin yerini tutmayacak.

### Portföy

README, güncel mimari, ekran görüntüsü/demo, değerlendirme raporu ve kurulabilir çalışma adımları tamamlanacak. CV satırı ancak gerçek ölçümler elde edildiğinde yazılacak. İyileşme yüzdesi, gecikme veya maliyet sonucu kaynak koşusu olmadan kullanılmayacak.

**Tamamlanma kanıtı:** Çalışan araç şeması ve istemci örneği, REST ile tutarlılık testi, tekrar üretilebilir demo, ölçüm bağlantıları ve mevcut durumu yansıtan README. İlgili gereksinim: **D-03**.

## 10. Her aşamada aynı kayıt düzeni

Her uygulama aşaması, uygun kapsamda ayrı bir dal/PR ile ilerler. İlgili kabul kriteri, kod, orantılı test ve dokümantasyon aynı değişiklikte bulunur. Test/CI sonucu tamamlandıktan sonra gözlenen durum kaydedilir; birleştirme sonrası sonuç sonraki geçmiş güncellemesinde kesin SHA ve bağlantısıyla tamamlanabilir.

| Kayıt | Sorulacak soru |
| --- | --- |
| Amaç ve kabul kriteri | Hangi somut davranışı tamamladık? |
| Değişen dosyalar | Uygulama, ayar, test ve doküman nerede? |
| Kimlikler | Hangi kod, veri, ayar ve model sürümü kullanıldı? |
| Yerel doğrulama | Hangi komut çalıştı ve gerçek sonuç neydi? |
| GitHub kanıtı | Hangi dal, commit, PR ve Actions çalışması? |
| Kullanım | Kullanıcı güncel sistemi hangi komutla çalıştırır? |
| Sınır ve sonraki adım | Hangi davranış henüz tamamlanmadı? |

Ayrıntılı kayıt şablonu [proje rehberinde](project-guide.md#guncelleme) bulunur. Gelecek plan değişiklikleri bu dosyada gerekçeleriyle kaydedilir. Mevcut aşamanın tamamlanması, sonraki aşamaların otomatik olarak tamamlandığı anlamına gelmez.

